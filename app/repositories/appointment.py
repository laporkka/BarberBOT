from sqlalchemy import select, cast, Date
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Sequence
from datetime import datetime, timedelta

from app.schemas.appointment import AppointmentCreate
from app.models.appointments import Appointment


class AppointmentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_appointment(self, appointment_in: AppointmentCreate, duration_min: int) -> Appointment:
        end_at = appointment_in.start_at + timedelta(minutes=duration_min)

        new_appointment = Appointment(
            **appointment_in.model_dump(),
            end_at=end_at
        )

        self.db.add(new_appointment)
        await self.db.commit()

        return new_appointment

    async def get_appointment_by_id(self, appointment_id: int) -> Appointment | None:
        query = select(Appointment).filter(Appointment.id == appointment_id)
        result = await self.db.execute(query)
        appointment = result.scalar_one_or_none()

        return appointment

    async def get_appointments_by_tg_id(self, customer_tg_id: str) -> Sequence[Appointment]:
        query = select(Appointment).filter(Appointment.customer_tg_id == customer_tg_id)
        result = await self.db.execute(query)
        appointments = result.scalars().all()

        return appointments

    async def get_by_barber_and_date(self, barber_id: int, date: datetime.date) -> Sequence[Appointment]:
        query = (
            select(Appointment)
            .filter(Appointment.barber_id == barber_id)
            .filter(cast(Appointment.start_at, Date) == date)
            .order_by(Appointment.start_at.asc())       
        )

        result = await self.db.execute(query)
        appointments = result.scalars().all()

        return appointments

    async def get_all_by_date(self, date: datetime.date) -> Sequence[Appointment]:
        query = (
            select(Appointment)
            .filter(cast(Appointment.start_at, Date) == date)
            .order_by(Appointment.start_at.asc())
        )

        result = await self.db.execute(query)
        appointments = result.scalars().all()

        return appointments