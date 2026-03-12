"""Уведомление админов о новой заявке."""
from aiogram import Bot
from loguru import logger

from src.bot.keyboards import kb_lead_actions
from src.config import get_settings


SERVICE_NAMES = {
    "cert_tr_ts": "Сертификат ТР ТС",
    "declaration": "Декларация",
    "iso": "ISO",
    "ce": "CE",
    "halal": "Халяль",
    "tm": "Регистрация ТМ",
}
COUNTRY_NAMES = {"russia": "Россия", "china": "Китай", "turkey": "Турция", "eu": "ЕС", "other": "Другая"}
URGENCY_NAMES = {"standard": "30 дней", "14": "14 дней", "7": "7 дней"}


async def notify_admins_new_lead(bot: Bot, calc_data: dict, lead, calculation) -> None:
    """Отправляет всем админам сообщение о новой заявке с inline-кнопками."""
    settings = get_settings()
    if not settings.admin_ids_list:
        return
    text = (
        "<b>Новая заявка</b>\n\n"
        f"Услуга: {SERVICE_NAMES.get(calc_data.get('service_key'), calc_data.get('service_key'))}\n"
        f"Страна: {COUNTRY_NAMES.get(calc_data.get('country_key'), calc_data.get('country_key'))}\n"
        f"Продукция: {calc_data.get('product_type', '-')}\n"
        f"SKU: {calc_data.get('sku_count')}\n"
        f"Срочность: {URGENCY_NAMES.get(calc_data.get('urgency_key'), calc_data.get('urgency_key'))}\n"
        f"Итог: {calc_data.get('final_price', 0):,.0f} ₽\n\n"
        f"Имя: {lead.name}\n"
        f"Телефон: {lead.phone}\n"
        f"Email: {lead.email}"
    )
    kb = kb_lead_actions(lead.id)
    for admin_id in settings.admin_ids_list:
        try:
            await bot.send_message(admin_id, text, reply_markup=kb)
        except Exception as exc:
            logger.warning("Не удалось отправить уведомление админу {}: {}", admin_id, exc)
