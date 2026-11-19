from aiogram import Router, F, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from datetime import datetime, timedelta, timezone, date

from app.bot.utils.api_client import api_client
from app.bot.fsm import BarberState


router = Router()


async def show_barber_schedule(callback: types.CallbackQuery, target_date: datetime.date, title_text: str):
    await callback.answer()
    
    barber_tg_id = str(callback.from_user.id)
    
    params = {
        "barber_tg_id": barber_tg_id,
        "target_data": target_date.strftime("%Y-%m-%d")
    }

    barber = await api_client.get_barber_by_tg_id(barber_tg_id)

    if not barber:
        builder = InlineKeyboardBuilder()
        builder.button(text="📅 Записаться на стрижку", callback_data="start_booking")
        builder.button(text="📋 Мои записи", callback_data="my_appointments")
        builder.adjust(1)
        
        await callback.message.edit_text(
            text="⚠️ <b>Ваш профиль мастера больше не найден в системе.</b>\n"
                 "Возможно, учетная запись была деактивирована администратором.\n"
                 "Вы переведены в стандартный режим клиента:",
            reply_markup=builder.as_markup(),
            parse_mode="HTML"
        )
        return

    barber_id = barber["id"]

    appointments = await api_client.get_appointments_by_barber(barber_id, target_date)

    text = f"<b>📅 {title_text} ({target_date.strftime('%d.%m.%Y')}):</b>\n\n"
    
    active_count = 0
    if appointments:
        for app in appointments:
            if app["status"] == "cancelled":
                continue
            
            active_count += 1
            start_dt = datetime.fromisoformat(app["start_at"]).astimezone(timezone(timedelta(hours=3)))
            time_str = start_dt.strftime("%H:%M")
            
            text += (
                f"⏰ <b>{time_str}</b> — {app['customer_name']}\n"
                f"📞 Тел: {app['customer_phone']}\n"
                f"───────────────────\n"
            )

    if active_count == 0:
        text += "Записей нет. Можно отдыхать и пить кофе! ☕️"

    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ В меню мастера", callback_data="back_to_barber_main")
    builder.adjust(1)

    await callback.message.edit_text(
        text=text,
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "barber_today")
async def get_today_schedule(callback: types.CallbackQuery):
    today = datetime.now(timezone(timedelta(hours=3))).date()
    await show_barber_schedule(callback, today, "РАСПИСАНИЕ НА СЕГОДНЯ")


@router.callback_query(F.data == "barber_tomorrow")
async def get_tomorrow_schedule(callback: types.CallbackQuery):
    tomorrow = datetime.now(timezone(timedelta(hours=3))).date() + timedelta(days=1)
    await show_barber_schedule(callback, tomorrow, "РАСПИСАНИЕ НА ЗАВТРА")


@router.callback_query(F.data == "back_to_barber_main")
async def back_to_barber_main(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()

    await state.clear()
    
    builder = InlineKeyboardBuilder()
    builder.button(text="📅 Мой день (Сегодня)", callback_data="barber_today")
    builder.button(text="📆 Расписание на завтра", callback_data="barber_tomorrow")
    builder.adjust(1)

    await callback.message.edit_text(
        text="Вот твое рабочее меню на сегодня:",
        reply_markup=builder.as_markup()
    )


@router.callback_query(F.data == "barber_block_start")
async def barber_block_start(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()

    barber = await api_client.get_barber_by_tg_id(str(callback.from_user.id))
    
    if not barber or not barber.get("is_active"):
        await callback.message.answer("❌ Профиль мастера не найден или отключен.")
        return

    await state.update_data(barber_id=barber["id"])
    await state.set_state(BarberState.choose_date)

    DAYS_SHORT = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]

    builder = InlineKeyboardBuilder()
    today = datetime.now(timezone(timedelta(hours=3))).date()
    
    for i in range(7):
        day = today + timedelta(days=i)
        date_str = day.strftime("%Y-%m-%d")
        day_name = DAYS_SHORT[day.weekday()]
        btn_text = f"{day.strftime('%d.%m')} ({day_name})"
        builder.button(text=btn_text, callback_data=f"brb_blk_date_{date_str}")

    builder.button(text="❌ Отмена", callback_data="back_to_barber_main")
    builder.adjust(1)

    await callback.message.edit_text(
        text="🔒 <b>БЛОКИРОВКА ВРЕМЕНИ</b>\nВыберите дату, на которую нужно закрыть слот:",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )


@router.callback_query(BarberState.choose_date, F.data.startswith("brb_blk_date_"))
async def barber_block_date_selected(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()

    selected_date = callback.data.split("_")[-1]
    target_date_obj = date.fromisoformat(selected_date)
    
    user_data = await state.get_data()
    barber_id = user_data.get("barber_id")

    available_slots = await api_client.get_available_time(
        barber_id=barber_id,
        duration_min=30,
        target_data=target_date_obj
    )

    if not available_slots:
        builder = InlineKeyboardBuilder()
        builder.button(text="⬅️ Выбрать другую дату", callback_data="barber_block_start")
        builder.button(text="❌ Отмена", callback_data="back_to_barber_main")
        builder.adjust(1)
        await callback.message.edit_text(
            text="На эту дату нет свободных слотов или салон закрыт.",
            reply_markup=builder.as_markup()
        )
        return

    await state.update_data(selected_date=selected_date)
    await state.set_state(BarberState.choose_time)

    builder = InlineKeyboardBuilder()
    for slot in available_slots:
        builder.button(text=slot, callback_data=f"brb_blk_time_{slot}")

    rows = [4] * (len(available_slots) // 4)
    if len(available_slots) % 4 > 0:
        rows.append(len(available_slots) % 4)
    
    builder.button(text="⬅️ Назад к датам", callback_data="barber_block_start")
    builder.button(text="❌ Отмена", callback_data="back_to_barber_main")
    rows.extend([1, 1])
    
    builder.adjust(*rows)

    await callback.message.edit_text(
        text=f"📅 Дата: <b>{selected_date}</b>\nВыберите слот (30 мин), который хотите закрыть:",
        reply_markup=builder.as_markup(),
        parse_mode="HTML"
    )


@router.callback_query(BarberState.choose_time, F.data.startswith("brb_blk_time_"))
async def barber_block_time_selected(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()

    selected_time = callback.data.split("_")[-1]
    
    user_data = await state.get_data()
    barber_id = user_data.get("barber_id")
    selected_date = user_data.get("selected_date")

    services = await api_client.get_all_services()
    slot_service = next((s for s in services if s["duration_min"] == 30), services[0] if services else None)

    if not slot_service:
        await callback.message.edit_text("❌ Ошибка: В базе нет ни одной услуги для создания слота.")
        await state.clear()
        return

    start_at_dt = datetime.fromisoformat(f"{selected_date}T{selected_time}:00").replace(tzinfo=timezone(timedelta(hours=3)))

    appointment = await api_client.create_appointment(
        customer_tg_id=callback.from_user.id,
        customer_name="🔒 ПЕРЕРЫВ МАСТЕРА",
        customer_phone="-----------",
        barber_id=barber_id,
        service_id=slot_service["id"],
        start_at=start_at_dt
    )

    await state.clear()

    builder = InlineKeyboardBuilder()
    builder.button(text="🔒 Закрыть еще один слот", callback_data="barber_block_start")
    builder.button(text="⬅️ В меню мастера", callback_data="back_to_barber_main")
    builder.adjust(1)

    if appointment:
        await callback.message.edit_text(
            text=f"✅ Слот <b>{selected_date} в {selected_time}</b> успешно заблокирован.\nКлиенты больше не смогут записаться на это время.",
            reply_markup=builder.as_markup(),
            parse_mode="HTML"
        )
    else:
        await callback.message.edit_text(
            text="⚠️ Не удалось заблокировать слот. Возможно, его только что занял клиент.",
            reply_markup=builder.as_markup()
        )