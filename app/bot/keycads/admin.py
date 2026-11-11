from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup
from typing import List, Dict, Any


DAYS_MAP = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]


class AdminKeyboards:

    @staticmethod
    def get_week_schedule_keyboard(schedules: list[dict]) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        
        for sch in schedules:
            day_idx = sch["day_of_week"]
            day_name = DAYS_MAP[day_idx]
            
            if sch["is_working_day"]:
                start_str = sch["start_at"][:5]
                end_str = sch["end_at"][:5]
                btn_text = f"🟢 {day_name}: {start_str} — {end_str}"
            else:
                btn_text = f"🔴 {day_name}: Выходной"
                
            builder.button(text=btn_text, callback_data=f"adm_sch_day_{day_idx}")

        builder.button(text="⚡ Применить ко всем дням", callback_data="adm_sch_bulk")
        builder.button(text="⬅️ В меню админа", callback_data="back_to_admin_main")
        builder.adjust(1)
        return builder.as_markup()


    @staticmethod
    def get_day_card_keyboard(day_idx: int) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text="🕒 Изменить открытие", callback_data=f"adm_sch_start_{day_idx}")
        builder.button(text="🕕 Изменить закрытие", callback_data=f"adm_sch_end_{day_idx}")
        builder.button(text="🔄 Рабочий / Выходной", callback_data=f"adm_sch_tgl_{day_idx}")
        builder.button(text="⬅️ К списку дней", callback_data="schedule_management")
        builder.adjust(2, 1, 1)
        return builder.as_markup()


admin_keyboards = AdminKeyboards()