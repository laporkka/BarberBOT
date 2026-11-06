from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import datetime, timedelta, timezone

from app.bot.fsm import BookingState
from app.bot.utils.api_client import api_client
from app.bot.keycads.client import keyboards
from app.bot.keycads.shedule import schedule_funcs


router = Router()


@router.callback_query(F.data == "start_booking")
async def start_booking(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()

    barbers = await api_client.get_active_barbers()

    await state.set_state(BookingState.choose_barber)

    markup = keyboards.get_barbers_keyboards(barbers)

    await callback.message.edit_text(
        text="Выберите мастера",
        reply_markup=markup
    )


@router.callback_query(BookingState.choose_barber, F.data.startswith("barber_"))
async def barber_selected(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()

    barber_id = int(callback.data.split("_")[1])

    services = await api_client.get_all_services()

    await state.update_data(barber_id=barber_id)
    await state.set_state(BookingState.choose_service)

    markup = keyboards.get_services_keyboards(services)

    await callback.message.edit_text(
        text="Выберите услугу",
        reply_markup=markup
    )


@router.callback_query(BookingState.choose_service, F.data.startswith("service_"))
async def service_selected(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()

    dates_payload = schedule_funcs.get_dates_payload()

    service_id = int(callback.data.split("_")[1])
    service = await api_client.get_service_by_id(service_id)

    if not service:
        await callback.message.answer("⚠️ Ошибка: Выбранная услуга не найдена в системе.")
        return
    
    duration_min = service["duration_min"]

    await state.update_data(service_id=service_id, duration_min=duration_min)
    await state.set_state(BookingState.choose_date)

    markup = keyboards.get_dates_keyboards(dates_payload)

    await callback.message.edit_text(
        text="Выберите дату",
        reply_markup=markup
    )


@router.callback_query(BookingState.choose_date, F.data.startswith("date_"))
async def date_selected(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()

    selected_date = callback.data.split("_")[1]

    date_obj = datetime.strptime(selected_date, "%Y-%m-%d").date()
    
    user_data = await state.get_data()
    duration_min = user_data.get("duration_min")
    barber_id = user_data.get("barber_id")

    available_slots = await api_client.get_available_time(
        duration_min=duration_min,
        barber_id=barber_id,
        target_data=date_obj
    )

    await state.update_data(selected_date=selected_date)
    await state.set_state(BookingState.choose_time)

    markup = keyboards.get_times_keyboards(available_slots)

    await callback.message.edit_text(
        text="Выберите время",
        reply_markup=markup
    )


@router.callback_query(BookingState.choose_time, F.data.startswith("time_"))
async def time_selected(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()

    selected_time = callback.data.split("_")[1]

    await state.update_data(selected_time=selected_time)
    await state.set_state(BookingState.get_name)

    await callback.message.answer("Введите ваше имя для записи:")


@router.message(BookingState.get_name)
async def name_selected(message: Message, state: FSMContext):
    client_name = message.text

    await state.update_data(customer_name=client_name)
    await state.set_state(BookingState.get_phone)

    markup = keyboards.get_phone_keyboard()

    await message.answer(
        text=f"Принят, {client_name}! Теперь отправьте ваш номер телефона, нажав на кнопку ниже:",
        reply_markup=markup
    )


@router.message(BookingState.get_phone, F.contact)
async def phone_selected(message: Message, state: FSMContext):
    customer_phone = message.contact.phone_number
    customer_tg_id = message.from_user.id

    user_data = await state.get_data()
    customer_name = user_data.get("customer_name")
    barber_id = user_data.get("barber_id")
    service_id = user_data.get("service_id")
    selected_date = user_data.get("selected_date") 
    selected_time = user_data.get("selected_time") 

    start_at_datetime = datetime.fromisoformat(f"{selected_date}T{selected_time}:00")

    appointment = await api_client.create_appointment(
        customer_tg_id=customer_tg_id,
        customer_name=customer_name,
        customer_phone=customer_phone,
        barber_id=barber_id,
        service_id=service_id,
        start_at=start_at_datetime
    )

    if not appointment:
        await message.answer(
            "❌ Что-то пошло не так при создании записи.\n"
            "Пожалуйста, попробуйте начать заново с помощью команды /start.",
            reply_markup=ReplyKeyboardRemove()
        )
        return

    await state.clear()

    await message.answer(
        text=f"🎉 {customer_name}, ты успешно записан!\n\n"
             f"📅 Дата: {selected_date}\n"
             f"⏰ Время: {selected_time}\n\n"
             "Ждем тебя в барбершопе! 🙌",
        reply_markup=ReplyKeyboardRemove() 
    )


@router.callback_query(BookingState.choose_service, F.data == "back_to_barbers")
async def back_to_barbers(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    
    await state.set_state(BookingState.choose_barber)
    
    barbers = await api_client.get_active_barbers()
    markup = keyboards.get_barbers_keyboards(barbers)
    
    await callback.message.edit_text(
        text="Выберите мастера:",
        reply_markup=markup
    )


@router.callback_query(BookingState.choose_date, F.data == "back_to_services")
async def back_to_services(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    
    await state.set_state(BookingState.choose_service)
    
    services = await api_client.get_all_service()
    markup = keyboards.get_services_keyboards(services)
    
    await callback.message.edit_text(
        text="Выберите услугу:",
        reply_markup=markup
    )


@router.callback_query(BookingState.choose_time, F.data == "back_to_dates")
async def back_to_date(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()

    await state.set_state(BookingState.choose_date)

    dates_payload = schedule_funcs.get_dates_payload()
    markup = keyboards.get_dates_keyboards(dates_payload)

    await callback.message.edit_text(
        text="Выберите время",
        reply_markup=markup
    )


@router.callback_query(F.data == "cancel_booking")
async def cancel_booking(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer("Запись отменена ❌")
    
    await state.clear()
    
    builder = InlineKeyboardBuilder()
    builder.button(text="📅 Записаться на стрижку", callback_data="start_booking")
    builder.button(text="📋 Мои записи", callback_data="my_appointments")
    builder.button(text="🗂️ Список услуг", callback_data="service_list")
    builder.adjust(1)

    await callback.message.edit_text(
        text="Запись отменена. Вы вернулись в главное меню. Выберите действие:",
        reply_markup=builder.as_markup()
    )



@router.callback_query(F.data == "my_appointments")
async def view_my_appointments(callback: types.CallbackQuery, state: FSMContext):
    callback.answer()

    customer_tg_id = callback.from_user.id

    appointments = await api_client.get_appointments_by_tg_id(customer_tg_id)

    if not appointments:
        builder = InlineKeyboardBuilder()
        builder.button(text="⬅️ В главное меню", callback_data="back_to_main_menu")

        await callback.message.edit_text(
            text="📋 У тебя пока нет активных записей в наш барбершоп.",
            reply_markup=builder.as_markup()
        )

        return

    STATUS_MAPPER = {
        "pending": "⏳ В ожидании подтверждения",
        "confirmed": "🟢 Подтверждена",
        "cancelled": "❌ Отменена",
        "completed": "✨ Завершена"
    }

    text = "<b>📋 ТВОИ ЗАПИСИ:</b>\n\n"
    has_active_bookings = False

    for idx, app in enumerate(appointments, 1):
        if app["status"] == "cancelled":
            continue
            
        has_active_bookings = True
    
        start_at_dt = datetime.fromisoformat(app["start_at"])
        date_str = start_at_dt.strftime("%d.%m.%Y")
        time_str = start_at_dt.strftime("%H:%M")
        
        ru_status = STATUS_MAPPER.get(app["status"], "Неизвестный статус")
        
        text += (
            f"{idx}. 📅 <b>Дата:</b> {date_str}\n"
            f"   ⏰ <b>Время:</b> {time_str}\n"
            f"   🆔 <b>Номер брони:</b> #{app['id']}\n"
            f"   📊 <b>Статус:</b> {ru_status}\n\n"
        )

    if not has_active_bookings:
        text = "📋 У тебя нет активных записей на ближайшее время."

    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ В главное меню", callback_data="back_to_main_menu")
    builder.adjust(1)

    await callback.message.edit_text(
        text=text,
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "service_list")
async def view_service_list(callback: types.CallbackQuery, state: FSMContext):
    callback.answer()

    services = await api_client.get_all_services()

    if not services:
        await callback.message.answer("📋 Прайс-лист сейчас пуст. Мы скоро добавим услуги!")
        return
    
    text = "<b>✂️ НАШ ПРАЙС-ЛИСТ:</b>\n\n"
    
    for idx, service in enumerate(services, 1):
        price_rub = service['price'] / 100  
        text += (
            f"{idx}. <b>{service['title']}</b>\n"
            f"   ⏳ Длительность: {service['duration_min']} мин.\n"
            f"   💰 Стоимость: {price_rub:.0f} руб.\n\n"
        )

    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ В главное меню", callback_data="back_to_main_menu")
    
    await callback.message.edit_text(
        text=text,
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "back_to_main_menu")
async def back_to_main_menu(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()

    builder = InlineKeyboardBuilder()
    builder.button(text="📅 Записаться на стрижку", callback_data="start_booking")
    builder.button(text="📋 Мои записи", callback_data="my_appointments")
    builder.button(text="🗂️ Список услуг", callback_data="service_list")
    builder.adjust(1)

    user_name = callback.from_user.first_name
    await callback.message.edit_text(
        text=f"Привет, {user_name}! 👋\nВы вернулись в главное меню. Выберите действие:",
        reply_markup=builder.as_markup()
    )
