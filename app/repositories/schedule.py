from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Sequence

from app.schemas.schedule import ScheduleUpdateTime, ScheduleBulkUpdate
from app.models.schedule import WorkingSchedule


class ScheduleRepository:
    def __init__(self, db: AsyncSession):
        self.db = db


    async def get_all_schedules(self) -> Sequence[WorkingSchedule]:
        query = select(WorkingSchedule).order_by(WorkingSchedule.day_of_week.asc())
        result = await self.db.execute(query)
        schedule = result.scalars().all()

        return schedule


    async def get_schedule_by_day(self, working_day: int) -> WorkingSchedule | None:
        query = select(WorkingSchedule).filter(WorkingSchedule.day_of_week == working_day)
        result = await self.db.execute(query)
        schedule = result.scalar_one_or_none()

        return schedule


    async def toggle_working_day(self, working_day: int) -> WorkingSchedule | None:
        day_schedule = await self.get_schedule_by_day(working_day)

        if not day_schedule:
            return None

        day_schedule.is_working_day = not day_schedule.is_working_day

        await self.db.commit()
        await self.db.refresh(day_schedule)

        return day_schedule


    async def update_day_time(self, working_day: int, time_in: ScheduleUpdateTime) -> WorkingSchedule | None:
        day_schedule = await self.get_schedule_by_day(working_day)

        if not day_schedule:
            return None

        update_data = time_in.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(day_schedule, key, value)

        await self.db.commit()
        await self.db.refresh(day_schedule)

        return day_schedule


    async def update_all_days(self, time_in: ScheduleBulkUpdate) -> Sequence[WorkingSchedule]:
        schedule = await self.get_all_schedules()
        update_data = time_in.model_dump(exclude_unset=True)
        
        for day in schedule:
            for key, value in update_data.items():
                setattr(day, key, value)

        await self.db.commit()
        
        return await self.get_all_schedules()