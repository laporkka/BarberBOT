from datetime import datetime

from app.repositories.appointment import AppointmentRepository


class ScheduleService:
    def __init__(self, appointment_repo: AppointmentRepository):
        self.appointment_repo = appointment_repo

    async def get_available_time(self, duration_min: int, barber_id: int, target_data: datetime.date):
        booked_dates = await self.appointment_repo.get_by_barber_and_date(barber_id, target_data)

        bit_map = 0

        for app in booked_dates:
            start_idx = ((app.start_at.hour - 10) * 2) + (1 if app.start_at.minute == 30 else 0)
            end_idx = ((app.end_at.hour - 10) * 2) + (1 if app.end_at.minute == 30 else 0)
            
            for idx in range(start_idx, end_idx):
                bit_map |= (1 << idx)

        available_slots = []
        slots_needed = duration_min // 30 

        for slot_idx in range(20 - slots_needed + 1):
            service_mask = 0

            for i in range(slots_needed):
                service_mask |= (1 << (slot_idx + i))

            if bit_map & service_mask == 0:
                total_minutes = 10 * 60 + slot_idx * 30
                hour = total_minutes // 60
                minute = total_minutes % 60 

                time_str = f"{hour:02d}:{minute:02d}"
                available_slots.append(time_str)
  
        return available_slots