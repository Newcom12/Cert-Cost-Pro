"""FSM-состояния для сценария расчёта и заявки."""
from aiogram.fsm.state import State, StatesGroup


class CalcStates(StatesGroup):
    select_service = State()
    select_country = State()
    enter_product_type = State()
    enter_sku_count = State()
    select_urgency = State()
    need_inspection = State()
    show_result = State()
    enter_contacts = State()
