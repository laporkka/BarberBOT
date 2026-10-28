from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Sequence

from app.schemas.service import ServiceCreate
from app.models.services import Service


class ServiceRepository:
    def __init__(self, db: AsyncSession):
        self.db = db


    async def create_service(self, service_in: ServiceCreate) -> Service:
        new_service = Service(**service_in.model_dump())

        self.db.add(new_service)
        await self.db.commit()

        return new_service

    async def get_all_services(self) -> Sequence[Service]:
        query = select(Service)
        result = await self.db.execute(query)
        services = result.scalars().all()

        return services

    async def get_service_by_id(self, service_id: int) -> Service | None:
            query = select(Service).filter(Service.id == service_id)
            result = await self.db.execute(query)
            service = result.scalar_one_or_none()
    
            return service