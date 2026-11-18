from aiogram import Router, html
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.fsm import BookingState
from app.core.config import settings
from app.bot.utils.api_client import api_client


router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()

    user_tg_id = str(message.from_user.id)
    user_name = message.from_user.first_name

    if user_tg_id in settings.ADMIN_IDS:
        builder = InlineKeyboardBuilder()
        builder.button(text="📊 Загрузка салона", callback_data="cabin_occupancy")
        builder.button(text="🗂️ Управление барберами", callback_data="barber_management")
        builder.button(text="🗂️ Управление услугами", callback_data="service_management")
        builder.button(text="🕒 График работы салона", callback_data="schedule_management")
        builder.button(text="👔 Управление менеджерами", callback_data="manager_management")
        builder.adjust(1)

        await message.answer(
            f"Привет, {user_name}! 👋\n"
            f"Ты авторизован как суперадмин. Вот твое рабочее меню на сегодня:",
            reply_markup=builder.as_markup(),
            parse_mode="HTML"
        )

        return

    manager = await api_client.get_manager_by_tg_id(user_tg_id)
    
    if manager and manager.get("is_active"):
        builder = InlineKeyboardBuilder()
        builder.button(text="📊 Загрузка салона", callback_data="cabin_occupancy")
        builder.button(text="🗂️ Управление барберами", callback_data="barber_management")
        builder.button(text="🗂️ Управление услугами", callback_data="service_management")
        builder.button(text="🕒 График работы салона", callback_data="schedule_management")
        builder.adjust(1)

        await message.answer(
            f"Привет, {user_name}! 👋\n"
            f"Ты авторизован как управляющий. Вот твое рабочее меню на сегодня:",
            reply_markup=builder.as_markup(),
            parse_mode="HTML"
        )

        return
    
    barber = await api_client.get_barber_by_tg_id(user_tg_id)

    if barber and barber.get("is_active"):
        builder = InlineKeyboardBuilder()
        builder.button(text="📅 Мой день (Сегодня)", callback_data="barber_today")
        builder.button(text="📆 Расписание на завтра", callback_data="barber_tomorrow")
        builder.adjust(1)

        await message.answer(
            f"Привет, {html.bold(barber['name'])}! 👋\n"
            f"Ты авторизован как мастер. Вот твое рабочее меню на сегодня:",
            reply_markup=builder.as_markup(),
            parse_mode="HTML"
        )

        return 
    
    builder = InlineKeyboardBuilder()
    builder.button(text="📅 Записаться на стрижку", callback_data="start_booking")
    builder.button(text="📋 Мои записи", callback_data="my_appointments")
    builder.button(text="🗂️ Список услуг", callback_data="service_list")
    builder.adjust(1)

    await message.answer(
        f"Привет, {user_name}! 👋\n"
        f"Добро пожаловать в наш барбершоп. Выбери действие ниже, чтобы продолжить:",
        reply_markup=builder.as_markup()
    )