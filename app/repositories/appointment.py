from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Sequence

from app.schemas.appointment import AppointmentCreate
from app.models.appointments import Appointment


class AppointmentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_appointment(self, appointment_in: AppointmentCreate) -> Appointment:
        new_appointment = Appointment(**appointment_in.model_dump())

        self.db.add(new_appointment)
        await self.db.commit()

        return new_appointment

    async def get_appointment_by_id(self, appointment_id: int) -> Appointment | None:
        query = select(Appointment).filter(Appointment.id == appointment_id)
        result = await self.db.execute(query)
        appointment = result.scalar_one_or_none()

        return appointment

    async def get_appointments_by_tg_id(self, appointment_tg_id: int) -> Sequence[Appointment]:
        query = select(Appointment).filter(Appointment.customer_tg_id == appointment_tg_id)
        result = await self.db.execute(query)
        appointments = result.scalars().all()

        return appointments