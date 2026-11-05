from aiogram.fsm.state import StatesGroup, State


class BookingState(StatesGroup):
    choose_barber = State()
    choose_service = State()
    choose_date = State()
    choose_time = State()
    get_name = State()
    get_phone = State()
    confirmation = State()