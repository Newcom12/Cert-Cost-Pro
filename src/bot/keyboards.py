"""Клавиатуры бота."""
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

# Услуги, шаг 1.
SERVICES = [
    ("Сертификат ТР ТС", "cert_tr_ts"),
    ("Декларация", "declaration"),
    ("ISO", "iso"),
    ("CE", "ce"),
    ("Халяль", "halal"),
    ("Регистрация ТМ", "tm"),
]

def kb_services() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=name, callback_data=f"svc:{key}")] for name, key in SERVICES
    ])


# Страна, шаг 2.
COUNTRIES = [
    ("Россия", "russia"),
    ("Китай", "china"),
    ("Турция", "turkey"),
    ("ЕС", "eu"),
    ("Другая", "other"),
]

def kb_countries() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=name, callback_data=f"country:{key}")] for name, key in COUNTRIES
    ])


# Типовые категории продукции, шаг 3.
TYPICAL_PRODUCTS = [
    "Одежда и текстиль",
    "Продукты питания",
    "Электроника",
    "Мебель",
    "Детские товары",
    "Строительные материалы",
]

def kb_typical_products() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=p, callback_data=f"prod:{i}")] for i, p in enumerate(TYPICAL_PRODUCTS)
    ])


# Срочность, шаг 5.
URGENCY_OPTIONS = [
    ("Стандарт (30 дней)", "standard"),
    ("Ускоренный (14 дней)", "14"),
    ("Экспресс (7 дней)", "7"),
]

def kb_urgency() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=name, callback_data=f"urg:{key}")] for name, key in URGENCY_OPTIONS
    ])


# Выезд эксперта, шаг 6.
def kb_inspection() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Да", callback_data="insp:1"),
            InlineKeyboardButton(text="Нет", callback_data="insp:0"),
        ]
    ])


# Действия после расчета.
def kb_after_calc() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Оставить заявку", callback_data="lead:submit")],
        [InlineKeyboardButton(text="Новый расчёт", callback_data="lead:new")],
    ])


# Действия админа по заявке.
def kb_lead_actions(lead_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Взять в работу", callback_data=f"adm:take:{lead_id}")],
        [InlineKeyboardButton(text="Закрыть", callback_data=f"adm:close:{lead_id}")],
        [InlineKeyboardButton(text="Написать клиенту", callback_data=f"adm:write:{lead_id}")],
    ])


# Главное меню.
def kb_main() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Рассчитать стоимость")]],
        resize_keyboard=True,
    )
