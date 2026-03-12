"""Админ-команды и обработка кнопок заявок."""
import io

from aiogram import F, Router
from aiogram.types import BufferedInputFile, CallbackQuery, Message
from sqlalchemy import select

from src.config import get_settings
from src.models import Lead
from src.services.notify import COUNTRY_NAMES, SERVICE_NAMES, URGENCY_NAMES
from src.services.metrics import (
    get_avg_check,
    get_calculations_per_day,
    get_stats,
    get_top_countries,
    get_top_services,
)

router = Router(name="admin")


def is_admin(telegram_id: int) -> bool:
    return telegram_id in get_settings().admin_ids_list


# ----- Команды только для админов -----
@router.message(F.text.in_(["/stats", "/export_csv", "/top_services", "/avg_check"]))
async def admin_commands(message: Message, session):
    if not is_admin(message.from_user.id):
        return
    text = message.text
    if text == "/stats":
        stats = await get_stats(session)
        msg = (
            f"<b>Статистика</b>\n\n"
            f"Расчетов: {stats['total_calculations']}\n"
            f"Заявок: {stats['total_leads']}\n"
            f"Конверсия расчет -> заявка: {stats['conversion_percent']}%"
        )
        await message.answer(msg)
        return
    if text == "/avg_check":
        avg = await get_avg_check(session)
        await message.answer(f"Средний чек: <b>{avg:,.0f} ₽</b>")
        return
    if text == "/top_services":
        top = await get_top_services(session)
        lines = [f"{SERVICE_NAMES.get(s, s)}: {c}" for s, c in top]
        await message.answer("Топ услуг:\n" + "\n".join(lines) if lines else "Нет данных")
        return
    if text == "/export_csv":
        from src.models import Calculation
        r = await session.execute(
            select(Calculation, Lead)
            .join(Lead, Lead.calculation_id == Calculation.id)
            .order_by(Lead.created_at.desc())
        )
        rows = r.all()
        buf = io.StringIO()
        buf.write("id;calculation_id;name;phone;email;status;service;country;sku;urgency;final_price;created_at\n")
        for calc, lead in rows:
            buf.write(
                f"{lead.id};{lead.calculation_id};{lead.name};{lead.phone};{lead.email};{lead.status};"
                f"{calc.service_type};{calc.country};{calc.sku_count};{calc.urgency};{calc.final_price};{lead.created_at}\n"
            )
        file = BufferedInputFile(buf.getvalue().encode("utf-8-sig"), filename="leads.csv")
        await message.answer_document(file, caption="Экспорт заявок")
        return


# ----- Inline: Взять в работу / Закрыть / Написать -----
@router.callback_query(F.data.startswith("adm:"))
async def admin_lead_action(cq: CallbackQuery, session):
    if not is_admin(cq.from_user.id):
        await cq.answer("Доступ запрещён.")
        return
    parts = cq.data.split(":")
    if len(parts) < 3:
        await cq.answer()
        return
    action, lead_id_s = parts[1], parts[2]
    try:
        lead_id = int(lead_id_s)
    except ValueError:
        await cq.answer()
        return
    r = await session.execute(select(Lead).where(Lead.id == lead_id))
    lead = r.scalar_one_or_none()
    if not lead:
        await cq.answer("Заявка не найдена.")
        return
    if action == "take":
        lead.status = "contacted"
        lead.manager_id = cq.from_user.id
        await cq.answer("Заявка взята в работу.")
        await cq.message.edit_reply_markup(reply_markup=None)
    elif action == "close":
        lead.status = "closed"
        lead.manager_id = cq.from_user.id
        await cq.answer("Заявка закрыта.")
        await cq.message.edit_reply_markup(reply_markup=None)
    elif action == "write":
        await cq.answer("Напишите клиенту в личку (контакт в сообщении выше).")
    else:
        await cq.answer()
