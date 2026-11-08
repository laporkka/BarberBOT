from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup
from typing import List, Dict, Any


class Keyboards:

    @staticmethod
    def get_barbers_keyboards(barbers: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        for barber in barbers:
            builder.button(
                text=f"💈 {barber['name']}",
                callback_data=f"barber_{barber['id']}"
            )

        builder.button(text="❌ Отмена", callback_data="cancel_booking")
        builder.adjust(1)

        return builder.as_markup()


    @staticmethod
    def get_services_keyboards(services: List[Dict[str, Any]]) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        for service in services:
            price_rub = service['price'] / 100
            builder.button(
                text=f"✂️ {service['title']} — {price_rub:.0f} руб.", 
                callback_data=f"service_{service['id']}"
            )

        builder.button(text="⬅️ Назад", callback_data="back_to_barbers")
        builder.button(text="❌ Отмена", callback_data="cancel_booking")
        builder.adjust(1)

        return builder.as_markup()
        

    @staticmethod
    def get_dates_keyboards(date_list: List[Dict[str, str]]) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        for data_item in date_list:
            builder.button(
                text=data_item["readable"], 
                callback_data=f"date_{data_item['raw']}"
            )

        builder.button(text="⬅️ Назад", callback_data="back_to_services")
        builder.button(text="❌ Отмена", callback_data="cancel_booking")
        builder.adjust(1)

        return builder.as_markup()


    @staticmethod
    def get_times_keyboards(available_slots: list[str]) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        
        for slot in available_slots:
            builder.button(text=slot, callback_data=f"time_{slot}")
            
        time_rows = []
        total_slots = len(available_slots)
        
        for _ in range(total_slots // 4):
            time_rows.append(4)
            
        if total_slots % 4 > 0:
            time_rows.append(total_slots % 4)

        builder.button(text="⬅️ Назад", callback_data="back_to_dates")
        builder.button(text="❌ Отмена", callback_data="cancel_booking")
        
        time_rows.append(1)
        time_rows.append(1)
        
        builder.adjust(*time_rows)
        return builder.as_markup()


    @staticmethod
    def get_phone_keyboard() -> ReplyKeyboardMarkup:
        builder = ReplyKeyboardBuilder()

        builder.button(text="📱 Поделиться номером телефона", request_contact=True)
        builder.adjust(1)

        return builder.as_markup(resize_keyboard=True, one_time_keyboard=True, input_field_placeholder="Нажми на кнопку ниже 👇")


keyboards = Keyboards()