from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from datetime import datetime, timedelta, timezone
from aiogram.types import Message

from app.bot.fsm import BookingState
from app.bot.utils.api_client import api_client
from app.bot.keycads.client import keyboards


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

    services = await api_client.get_all_service()

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

    weekdays = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    dates_payload = []
    now = datetime.now(timezone.utc).date()

    for i in range(7):
        date = now + timedelta(days=i)
        
        raw_date = date.strftime("%Y-%m-%d")
        readable_date = date.strftime(f"{weekdays[date.weekday()]} (%d.%m)")

        dates_payload.append(
            {
                "raw": raw_date,
                "readable": readable_date
            }
        )

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
    user_data = await state.get_data()
    duration_min = user_data.get("duration_min")
    barber_id = user_data.get("barber_id")

    available_slots = await api_client.get_available_time(
        duration_min=duration_min,
        barber_id=barber_id,
        target_data=selected_date
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
async def name_selected(message: Message, callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()

    client_name = message.text

    await state.update_data(customer_name=client_name)
    await state.set_state(BookingState.get_phone)

    markup = keyboards.get_phone_keyboard()

    await message.answer(
        text=f"Принят, {client_name}! Теперь отправьте ваш номер телефона, нажав на кнопку ниже:",
        reply_markup=markup
    )