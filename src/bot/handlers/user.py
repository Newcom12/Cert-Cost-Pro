"""Обработчики пользовательского сценария (FSM): расчёт и заявка."""
from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.keyboards import (
    TYPICAL_PRODUCTS,
    kb_after_calc,
    kb_countries,
    kb_inspection,
    kb_services,
    kb_typical_products,
    kb_urgency,
)
from src.bot.states import CalcStates
from src.models import Calculation, User
from src.services.calculator import INSPECTION_COST, calculate
from src.utils.validators import is_valid_email, is_valid_phone

router = Router(name="user")


async def get_or_create_user(session: AsyncSession, telegram_id: int, username: str | None) -> User:
    r = await session.execute(select(User).where(User.telegram_id == telegram_id))
    user = r.scalar_one_or_none()
    if user:
        return user
    user = User(telegram_id=telegram_id, username=username)
    session.add(user)
    await session.flush()
    return user


# ----- /start и начало -----
@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Добро пожаловать в <b>CertCost Pro</b>.\n\n"
        "Я помогу рассчитать стоимость сертификации. Выберите услугу:",
        reply_markup=kb_services(),
    )
    await state.set_state(CalcStates.select_service)


# ----- Шаг 1: Услуга -----
@router.callback_query(F.data.startswith("svc:"), CalcStates.select_service)
async def step_service(cq: CallbackQuery, state: FSMContext):
    service_key = cq.data.removeprefix("svc:")
    await state.update_data(service_key=service_key)
    await state.set_state(CalcStates.select_country)
    await cq.message.edit_text("Укажите страну производства:", reply_markup=kb_countries())
    await cq.answer()


# ----- Шаг 2: Страна -----
@router.callback_query(F.data.startswith("country:"), CalcStates.select_country)
async def step_country(cq: CallbackQuery, state: FSMContext):
    country_key = cq.data.removeprefix("country:")
    await state.update_data(country_key=country_key)
    await state.set_state(CalcStates.enter_product_type)
    await cq.message.edit_text(
        "Введите тип продукции (текстом) или выберите типовую категорию:",
        reply_markup=kb_typical_products(),
    )
    await cq.answer()


# ----- Шаг 3: Тип продукции -----
@router.callback_query(F.data.startswith("prod:"), CalcStates.enter_product_type)
async def step_product_callback(cq: CallbackQuery, state: FSMContext):
    idx = cq.data.removeprefix("prod:")
    try:
        product_type = TYPICAL_PRODUCTS[int(idx)]
    except (ValueError, IndexError):
        await cq.answer("Выберите категорию из списка.")
        return
    await state.update_data(product_type=product_type)
    await state.set_state(CalcStates.enter_sku_count)
    await cq.message.edit_text("Введите количество SKU (число):")
    await cq.answer()


@router.message(F.text, CalcStates.enter_product_type)
async def step_product_text(message: Message, state: FSMContext):
    product_type = (message.text or "").strip()
    if not product_type or len(product_type) > 500:
        await message.answer("Введите краткое описание продукции (до 500 символов).")
        return
    await state.update_data(product_type=product_type)
    await state.set_state(CalcStates.enter_sku_count)
    await message.answer("Введите количество SKU (число):")


# ----- Шаг 4: SKU -----
@router.message(F.text.regexp(r"^\d+$"), CalcStates.enter_sku_count)
async def step_sku_ok(message: Message, state: FSMContext):
    sku = int(message.text)
    if sku < 1:
        await message.answer("Введите число больше 0.")
        return
    if sku > 50:
        await message.answer(
            "⚠️ Количество SKU больше 50 — сроки и стоимость могут существенно вырасти. "
            "Продолжаем с введённым значением?"
        )
    await state.update_data(sku_count=sku)
    await state.set_state(CalcStates.select_urgency)
    await message.answer("Выберите срочность:", reply_markup=kb_urgency())


@router.message(CalcStates.enter_sku_count)
async def step_sku_invalid(message: Message):
    await message.answer("Введите одно целое число (количество SKU).")


# ----- Шаг 5: Срочность -----
@router.callback_query(F.data.startswith("urg:"), CalcStates.select_urgency)
async def step_urgency(cq: CallbackQuery, state: FSMContext):
    urgency_key = cq.data.removeprefix("urg:")
    await state.update_data(urgency_key=urgency_key)
    await state.set_state(CalcStates.need_inspection)
    await cq.message.edit_text("Нужен ли выезд эксперта?", reply_markup=kb_inspection())
    await cq.answer()


# ----- Шаг 6: Выезд эксперта -----
@router.callback_query(F.data.startswith("insp:"), CalcStates.need_inspection)
async def step_inspection(cq: CallbackQuery, state: FSMContext, session: AsyncSession):
    inspection = cq.data == "insp:1"
    data = await state.get_data()
    base, k_c, k_s, k_u, final_raw, final_rounded = calculate(
        data["service_key"],
        data["country_key"],
        data["sku_count"],
        data["urgency_key"],
        inspection,
    )
    await state.update_data(
        inspection_required=inspection,
        base_price=base,
        k_country=k_c,
        k_sku=k_s,
        k_urgency=k_u,
        final_price=float(final_rounded),
    )
    await state.set_state(CalcStates.show_result)

    # Сохраняем расчёт в БД
    user = await get_or_create_user(
        session, cq.from_user.id, cq.from_user.username
    )
    calc = Calculation(
        user_id=user.id,
        service_type=data["service_key"],
        country=data["country_key"],
        product_type=data["product_type"],
        sku_count=data["sku_count"],
        urgency=data["urgency_key"],
        inspection_required=inspection,
        base_price=base,
        k_country=k_c,
        k_sku=k_s,
        k_urgency=k_u,
        final_price=float(final_rounded),
    )
    session.add(calc)
    await session.flush()
    await state.update_data(calculation_id=calc.id)

    service_names = {
        "cert_tr_ts": "Сертификат ТР ТС",
        "declaration": "Декларация",
        "iso": "ISO",
        "ce": "CE",
        "halal": "Халяль",
        "tm": "Регистрация ТМ",
    }
    country_names = {"russia": "Россия", "china": "Китай", "turkey": "Турция", "eu": "ЕС", "other": "Другая"}
    urgency_names = {"standard": "30 дней", "14": "14 дней", "7": "7 дней"}

    text = (
        f"<b>Расчёт</b>\n\n"
        f"База: {base:,.0f} ₽\n"
        f"Коэфф. страна ({country_names.get(data['country_key'], data['country_key'])}): {k_c}\n"
        f"Коэфф. SKU: {k_s:.2f}\n"
        f"Коэфф. срочность ({urgency_names.get(data['urgency_key'], data['urgency_key'])}): {k_u}\n\n"
        f"<i>{base:,.0f} × {k_c} × {k_s:.2f} × {k_u} = {base * k_c * k_s * k_u:,.0f} ₽</i>\n"
    )
    if inspection:
        text += f"\nВыезд эксперта: {INSPECTION_COST:,} ₽\n"
    text += f"\n<b>ИТОГО: {final_rounded:,} ₽</b>"

    await cq.message.edit_text(text, reply_markup=kb_after_calc())
    await cq.answer()


# ----- После расчёта: новая заявка или новый расчёт -----
@router.callback_query(F.data == "lead:new", CalcStates.show_result)
async def lead_new_calc(cq: CallbackQuery, state: FSMContext):
    await state.clear()
    await cq.message.edit_text("Выберите услугу:", reply_markup=kb_services())
    await state.set_state(CalcStates.select_service)
    await cq.answer()


@router.callback_query(F.data == "lead:submit", CalcStates.show_result)
async def lead_start_contacts(cq: CallbackQuery, state: FSMContext):
    await state.set_state(CalcStates.enter_contacts)
    await cq.message.edit_text("Чтобы оставить заявку, введите <b>имя</b> (одним сообщением):")
    await cq.answer()


# ----- Шаг 8: Контакты (имя → телефон → email) -----
# Используем подсостояние через data: step_contacts = name | phone | email
@router.message(CalcStates.enter_contacts, F.text)
async def step_contacts(message: Message, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    step = data.get("contact_step", "name")

    if step == "name":
        name = (message.text or "").strip()
        if len(name) < 2:
            await message.answer("Введите корректное имя.")
            return
        await state.update_data(lead_name=name, contact_step="phone")
        await message.answer("Введите <b>телефон</b> (например +7 999 123 45 67):")
        return

    if step == "phone":
        if not is_valid_phone(message.text or ""):
            await message.answer("Неверный формат телефона. Введите, например: +7 999 123 45 67")
            return
        await state.update_data(lead_phone=(message.text or "").strip(), contact_step="email")
        await message.answer("Введите <b>email</b>:")
        return

    if step == "email":
        if not is_valid_email(message.text or ""):
            await message.answer("Неверный формат email.")
            return
        lead_email = (message.text or "").strip()
        full_data = await state.get_data()
        user = await get_or_create_user(
            session, message.from_user.id, message.from_user.username
        )
        from src.models import Lead

        lead = Lead(
            calculation_id=full_data["calculation_id"],
            user_id=user.id,
            name=full_data["lead_name"],
            phone=full_data["lead_phone"],
            email=lead_email,
            status="new",
        )
        session.add(lead)
        await session.flush()

        await state.clear()
        await message.answer(
            "✅ Заявка отправлена! Менеджер свяжется с вами в ближайшее время."
        )
        from src.services.notify import notify_admins_new_lead
        # calculation_id и данные расчёта в full_data; для текста нужны поля расчёта
        calc_data = {
            "service_key": full_data.get("service_key"),
            "country_key": full_data.get("country_key"),
            "product_type": full_data.get("product_type"),
            "sku_count": full_data.get("sku_count"),
            "urgency_key": full_data.get("urgency_key"),
            "final_price": full_data.get("final_price"),
        }
        await notify_admins_new_lead(message.bot, calc_data, lead, None)
        return


# ----- Команда /calc для быстрого старта -----
@router.message(Command("calc"))
async def cmd_calc(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Выберите услугу:", reply_markup=kb_services())
    await state.set_state(CalcStates.select_service)
