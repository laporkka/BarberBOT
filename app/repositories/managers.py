from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Sequence

from app.models.managers import Manager
from app.schemas.manager import ManagerCreate


class ManagerRepository:
    def __init__(self, db: AsyncSession):
            self.db = db
    
    async def create_manager(self, manager_in: ManagerCreate) -> Manager:
        new_manager = Manager(**manager_in.model_dump())

        self.db.add(new_manager)
        await self.db.commit()

        return new_manager

    async def get_manager_by_id(self, manager_id: int) -> Manager | None:
        query = select(Manager).filter(Manager.id == manager_id)
        result = await self.db.execute(query)
        manager = result.scalar_one_or_none()

        return manager

    async def get_manager_by_tg_id(self, manager_tg_id: str) -> Manager | None:
        query = select(Manager).filter(Manager.tg_id == manager_tg_id)
        result = await self.db.execute(query)
        manager = result.scalar_one_or_none()

        return manager
    
    async def get_active_managers(self) -> Sequence[Manager]:
        query = select(Manager).filter(Manager.is_active == True)
        result = await self.db.execute(query)
        managers = result.scalars().all()

        return managers

    async def get_all_managers(self) -> Sequence[Manager]:
        query = select(Manager)
        result = await self.db.execute(query)
        managers = result.scalars().all()

        return managers

    async def update_manager_by_id(self, manager_id: int, new_name: str) -> Manager | None:
        manager = await self.get_manager_by_id(manager_id)

        if not manager:
            return None

        manager.name = new_name
        await self.db.commit()

        return manager

    async def toggle_active_manager(self, manager_id: int) -> Manager | None:
        manager = await self.get_manager_by_id(manager_id)
        
        if not manager:
            return None

        manager.is_active = not manager.is_active
        await self.db.commit()

        return manager