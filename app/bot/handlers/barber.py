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
            start_dt = datetime.fromisoformat(app["start_at"])
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
    today = datetime.now(timezone.utc).date()
    await show_barber_schedule(callback, today, "РАСПИСАНИЕ НА СЕГОДНЯ")


@router.callback_query(F.data == "barber_tomorrow")
async def get_tomorrow_schedule(callback: types.CallbackQuery):
    tomorrow = datetime.now(timezone.utc).date() + timedelta(days=1)
    await show_barber_schedule(callback, tomorrow, "РАСПИСАНИЕ НА ЗАВТРА")


@router.callback_query(F.data == "back_to_barber_main")
async def back_to_barber_main(callback: types.CallbackQuery):
    await callback.answer()
    
    builder = InlineKeyboardBuilder()
    builder.button(text="📅 Мой день (Сегодня)", callback_data="barber_today")
    builder.button(text="📆 Расписание на завтра", callback_data="barber_tomorrow")
    builder.adjust(1)

    await callback.message.edit_text(
        text="Вот твое рабочее меню на сегодня:",
        reply_markup=builder.as_markup()
    )