from aiogram.fsm.state import StatesGroup, State


class BookingState(StatesGroup):
    choose_barber = State()
    choose_service = State()
    choose_date = State()
    choose_time = State()
    get_name = State()
    get_phone = State()
    confirmation = State()


class AdminState(StatesGroup):
    get_barber_name = State()      
    get_barber_tg_id = State()     
    get_service_title = State()    
    get_service_price = State()    
    get_service_duration = State()
    get_work_start = State()
    get_work_end = State()
    get_bulk_schedule = State()


class BarberState(StatesGroup):
    choose_date = State()
    choose_duration = State()
    choose_time = State()