from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Sequence

from app.schemas.barber import BarberCreate
from app.models.barbers import Barber


class BarberRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_barber(self, barber_in: BarberCreate) -> Barber:
        new_barber = Barber(**barber_in.model_dump())

        self.db.add(new_barber)
        await self.db.commit()

        return new_barber

    async def get_barber_by_id(self, barber_id: int) -> Barber | None:
        query = select(Barber).filter(Barber.id == barber_id)
        result = await self.db.execute(query)
        barber = result.scalar_one_or_none()

        return barber

    async def get_barber_by_tg_id(self, barber_tg_id: str) -> Barber | None:
        query = select(Barber).filter(Barber.tg_id == barber_tg_id)
        result = await self.db.execute(query)
        barber = result.scalar_one_or_none()

        return barber
    
    async def get_active_barbers(self) -> Sequence[Barber]:
        query = select(Barber).filter(Barber.is_active == True)
        result = await self.db.execute(query)
        barbers = result.scalars().all()

        return barbers

    async def get_all_barbers(self) -> Sequence[Barber]:
        query = select(Barber)
        result = await self.db.execute(query)
        barbers = result.scalars().all()

        return barbers

    async def delete_barber_by_id(self, barber_in: Barber):
        await self.db.delete(barber_in)
        await self.db.commit()