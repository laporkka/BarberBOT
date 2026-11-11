from datetime import date

from app.repositories.appointment import AppointmentRepository
from app.repositories.schedule import ScheduleRepository


class ScheduleService:
    def __init__(self, appointment_repo: AppointmentRepository, schedule_repo: ScheduleRepository):
        self.appointment_repo = appointment_repo
        self.schedule_repo = schedule_repo


    async def get_available_time(self, duration_min: int, barber_id: int, target_data: date):
        booked_dates = await self.appointment_repo.get_by_barber_and_date(barber_id, target_data)
        day_schedule = await self.schedule_repo.get_schedule_by_day(target_data.weekday())

        if not day_schedule or not day_schedule.is_working_day:
            return []
        
        work_start_min = day_schedule.start_at.hour * 60 + day_schedule.start_at.minute
        work_end_min = day_schedule.end_at.hour * 60 + day_schedule.end_at.minute

        bit_map = 0

        for app in booked_dates:
            if app.status == "cancelled":
                continue

            start_idx = (app.start_at.hour * 60 + app.start_at.minute - work_start_min) // 30 
            end_idx = (app.end_at.hour * 60 + app.end_at.minute - work_start_min) // 30 
            
            for idx in range(start_idx, end_idx):
                bit_map |= (1 << idx)

        available_slots = []
        slots_needed = duration_min // 30 
        total_slots = (work_end_min - work_start_min) // 30

        for slot_idx in range(total_slots - slots_needed + 1):
            service_mask = 0

            for i in range(slots_needed):
                service_mask |= (1 << (slot_idx + i))

            if bit_map & service_mask == 0:
                total_minutes = work_start_min + slot_idx * 30
                hour = total_minutes // 60
                minute = total_minutes % 60 

                time_str = f"{hour:02d}:{minute:02d}"
                available_slots.append(time_str)
  
        return available_slots