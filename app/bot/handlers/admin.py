from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import datetime, timezone

from app.bot.fsm import AdminState
from app.bot.utils.api_client import api_client
from app.core.config import settings


router = Router()


async def send_admin_menu(message: types.Message | types.CallbackQuery, text: str):
    builder = InlineKeyboardBuilder()
    builder.button(text="📊 Загрузка салона", callback_data="cabin_occupancy")
    builder.button(text="🗂️ Управление барберами", callback_data="barber_management")
    builder.button(text="🗂️ Управление услугами", callback_data="service_management")
    builder.adjust(1)

    if isinstance(message, types.CallbackQuery):
        await message.message.edit_text(text=text, reply_markup=builder.as_markup(), parse_mode="HTML")
    else:
        await message.answer(text=text, reply_markup=builder.as_markup(), parse_mode="HTML")



@router.callback_query(F.data == "cabin_occupancy")
async def show_cabin_occupancy(callback: types.CallbackQuery):
    await callback.answer()
    
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    appointments = await api_client.get_all_appointments_by_date(today_str)
    barbers = await api_client.get_active_barbers()

    text = f"<b>📊 ЗАГРУЗКА САЛОНА НА СЕГОДНЯ ({datetime.now().strftime('%d.%m.%Y')}):</b>\n\n"

    for barber in barbers:
        barber_apps = [a for a in appointments if a["barber_id"] == barber["id"] and a["status"] != "cancelled"]
        text += f"👤 <b>{barber['name']}</b>:\n"
        
        if not barber_apps:
            text += "   🟢 Записей нет, мастер свободен.\n"
        else:
            text += f"   🔴 Активных записей: {len(barber_apps)}\n"
            for app in barber_apps:
                start_dt = datetime.fromisoformat(app["start_at"])
                text += f"   • ⏰ {start_dt.strftime('%H:%M')} — {app['customer_name']} ({app['customer_phone']})\n"

        text += "───────────────────\n"

    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ В меню админа", callback_data="back_to_admin_main")

    await callback.message.edit_text(text=text, reply_markup=builder.as_markup(), parse_mode="HTML")


@router.callback_query(F.data == "barber_management")
async def barber_management(callback: types.CallbackQuery):
    await callback.answer()
    
    barbers = await api_client.get_all_barbers()
    
    text = "<b>🗂️ УПРАВЛЕНИЕ МАСТЕРАМИ:</b>\nКликни по статусу, чтобы изменить его.\n\n"
    builder = InlineKeyboardBuilder()
    
    for b in barbers:
        status_emoji = "🟢" if b["is_active"] else "🔴"
        status_text = "Активен" if b["is_active"] else "Отключен"
        
        builder.button(text=f"👤 {b['name']}", callback_data="noop")
        builder.button(text=f"{status_emoji} {status_text}", callback_data=f"adm_tgl_brb_{b['id']}")
        builder.button(text="✏️ Изменить имя", callback_data=f"adm_ren_brb_{b['id']}")

    builder.adjust(3) 
    
    builder.row(types.InlineKeyboardButton(text="➕ Добавить мастера", callback_data="add_barber_start"))
    builder.row(types.InlineKeyboardButton(text="⬅️ В меню админа", callback_data="back_to_admin_main"))
    
    await callback.message.edit_text(text=text, reply_markup=builder.as_markup(), parse_mode="HTML")


@router.callback_query(F.data.startswith("adm_tgl_brb_"))
async def adm_toggle_barber(callback: types.CallbackQuery):
    barber_id = int(callback.data.split("_")[-1])
    
    await api_client.toggle_active_barber_by_id(barber_id)
    
    await barber_management(callback)


@router.callback_query(F.data.startswith("adm_ren_brb_"))
async def adm_edit_barber_name_start(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    barber_id = int(callback.data.split("_")[-1])
    
    await state.update_data(edit_barber_id=barber_id)
    
    await state.set_state(AdminState.get_barber_name) 
    await callback.message.answer("✏️ Введите НОВОЕ имя для этого мастера:")


@router.callback_query(F.data == "add_barber_start")
async def add_barber_start(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(AdminState.get_barber_name)
    await callback.message.answer("✏️ Введите имя нового мастера:")


@router.message(AdminState.get_barber_name, F.text)
async def add_barber_name(message: types.Message, state: FSMContext):
    new_name = message.text.strip()
    user_data = await state.get_data()
    
    edit_id = user_data.get("edit_barber_id")
    
    if edit_id:
        await api_client.update_barber_name_by_id(barber_id=edit_id, new_name=new_name)
        await state.clear()
        await send_admin_menu(message, f"✅ Имя мастера успешно изменено на <b>{new_name}</b>!")
        return

    await state.update_data(new_barber_name=new_name)
    await state.set_state(AdminState.get_barber_tg_id)
    await message.answer("🆔 Теперь введите цифровой Telegram ID мастера:")


@router.message(AdminState.get_barber_tg_id, F.text)
async def add_barber_tg_id(message: types.Message, state: FSMContext):
    tg_id = message.text.strip()
    if not tg_id.isdigit():
        await message.answer("❌ Telegram ID должен состоять только из цифр. Введите еще раз:")
        return

    user_data = await state.get_data()
    name = user_data.get("new_barber_name")

    result = await api_client.create_barber(name=name, tg_id=tg_id, is_active=True)
    await state.clear()

    if result:
        await send_admin_menu(message, f"✅ Мастер <b>{name}</b> успешно добавлен!")
    else:
        await send_admin_menu(message, "❌ Ошибка при создании мастера.")


@router.callback_query(F.data == "service_management")
async def service_management(callback: types.CallbackQuery):
    await callback.answer()
    
    services = await api_client.get_all_services()

    text = "<b>🗂️ УПРАВЛЕНИЕ УСЛУГАМИ Салона:</b>\nУправляй видимостью и ценами прайса.\n\n"
    builder = InlineKeyboardBuilder()
    
    for s in services:
        status_emoji = "🟢" if s["is_active"] else "🔴"
        price_rub = s["price"] / 100
        
        
        builder.button(text=f"✂️ {s['title']} ({s['duration_min']} мин.)", callback_data="noop")
        builder.button(text=f"{status_emoji} Статус", callback_data=f"adm_tgl_srv_{s['id']}")
        builder.button(text=f"💰 {price_rub:.0f} руб.", callback_data=f"adm_prc_srv_{s['id']}")

    row_sizes = []
    for _ in services:
        row_sizes.append(1) 
        row_sizes.append(2) 
        
    builder.adjust(*row_sizes)

    builder.row(types.InlineKeyboardButton(text="➕ Добавить новую услугу", callback_data="add_service_start"))
    builder.row(types.InlineKeyboardButton(text="⬅️ В меню админа", callback_data="back_to_admin_main"))
    
    await callback.message.edit_text(text=text, reply_markup=builder.as_markup(), parse_mode="HTML")


@router.callback_query(F.data.startswith("adm_tgl_srv_"))
async def adm_toggle_service(callback: types.CallbackQuery):
    service_id = int(callback.data.split("_")[-1])

    await api_client.toggle_active_service_by_id(service_id)
    await service_management(callback)


@router.callback_query(F.data.startswith("adm_prc_srv_"))
async def adm_edit_price_start(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()

    service_id = int(callback.data.split("_")[-1])
    
    await state.update_data(edit_service_id=service_id)
    await state.set_state(AdminState.get_service_price) 
    await callback.message.answer("💰 Введите НОВУЮ стоимость услуги в рублях (целое число):")


@router.callback_query(F.data == "add_service_start")
async def add_service_start(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(AdminState.get_service_title)
    await callback.message.answer("✏️ Введите название услуги (например: Стрижка бороды):")


@router.message(AdminState.get_service_title, F.text)
async def add_service_title(message: types.Message, state: FSMContext):
    await state.update_data(new_service_title=message.text)
    await state.set_state(AdminState.get_service_price)
    await message.answer("💰 Введите стоимость услуги в рублях (целое число):")


@router.message(AdminState.get_service_price, F.text)
async def add_service_price(message: types.Message, state: FSMContext):
    price_text = message.text.strip()

    if not price_text.isdigit():
        await message.answer("❌ Введите цену целым числом:")
        return
        
    price_cents = int(price_text) * 100
    user_data = await state.get_data()
    
    edit_id = user_data.get("edit_service_id")

    if edit_id:
        await api_client.update_service_price_by_id(service_id=edit_id, new_price=price_cents)
        await state.clear()
        await send_admin_menu(message, "✅ Стоимость услуги успешно обновлена в базе данных!")
        return

    await state.update_data(new_service_price_cents=price_cents)
    await state.set_state(AdminState.get_service_duration)
    await message.answer("⏳ Введите длительность услуги в минутах (например: 30, 60):")


@router.message(AdminState.get_service_duration, F.text)
async def add_service_duration(message: types.Message, state: FSMContext):
    duration_text = message.text.strip()
    
    if not duration_text.isdigit():
        await message.answer("❌ Введите длительность числом минут:")
        return
    
    user_data = await state.get_data()
    title = user_data.get("new_service_title")
    price_cents = user_data.get("new_service_price_cents")
    duration_min = int(duration_text)
    result = await api_client.create_service(title=title, price=price_cents, duration_min=duration_min)
    await state.clear()
    
    if result:
        await send_admin_menu(message, f"✅ Услуга {title} успешно добавлена в прайс!")
    else:
        await send_admin_menu(message, "❌ Ошибка при создании услуги.")


@router.callback_query(F.data == "back_to_admin_main")
async def back_to_admin_main(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    await send_admin_menu(callback, "Вот твое рабочее меню на сегодня:")


@router.callback_query(F.data == "noop")
async def noop_callback(callback: types.CallbackQuery):
    await callback.answer()