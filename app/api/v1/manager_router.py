from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.manager import ManagerResponse, ManagerCreate
from app.core.database import get_db
from app.repositories.managers import ManagerRepository


router = APIRouter(prefix="/manager", tags=["Manager"])


@router.post("/add/manager", response_model=ManagerResponse, status_code=status.HTTP_201_CREATED)
async def create_manager(
    manager_in: ManagerCreate,
    db: AsyncSession = Depends(get_db)
):
    manager_repo = ManagerRepository(db)

    exist_manager = await manager_repo.get_manager_by_tg_id(manager_in.tg_id)
    
    if exist_manager:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Manager already exist"
        )

    new_manager = await manager_repo.create_manager(manager_in)
    return new_manager


@router.get("/get/all_active", response_model=list[ManagerResponse], status_code=status.HTTP_200_OK)
async def get_active_managers(
    db: AsyncSession = Depends(get_db)
):
    response = await ManagerRepository(db).get_active_managers()
    return response


@router.get("/get/all", response_model=list[ManagerResponse], status_code=status.HTTP_200_OK)
async def get_all_managers(
    db: AsyncSession = Depends(get_db)
):
    response = await ManagerRepository(db).get_all_managers()
    return response


@router.get("/get/by_id/{manager_id}", response_model=ManagerResponse, status_code=status.HTTP_200_OK)
async def get_manager_by_id(
    manager_id: int,
    db: AsyncSession = Depends(get_db)
):
    response = await ManagerRepository(db).get_manager_by_id(manager_id)

    if not response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Manager not found"
        )
    
    return response


@router.get("/get/by_tg_id/{manager_tg_id}", response_model=ManagerResponse, status_code=status.HTTP_200_OK)
async def get_manager_by_tg_id(
    manager_tg_id: str,
    db: AsyncSession = Depends(get_db)    
):
    response = await ManagerRepository(db).get_manager_by_tg_id(manager_tg_id)

    if not response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Manager not found"
        )
    
    return response


@router.patch("/{manager_id}/update-name", response_model=ManagerResponse, status_code=status.HTTP_200_OK)
async def update_manager_name_by_id(
    manager_id: int,
    new_name: str = Body(..., embed=True),
    db: AsyncSession = Depends(get_db)
):
    manager_update = await ManagerRepository(db).update_manager_by_id(manager_id, new_name)

    if not manager_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Manager not found"
        )

    return manager_update


@router.patch("/{manager_id}/toggle-active", response_model=ManagerResponse, status_code=status.HTTP_200_OK)
async def toggle_active_manager_by_id(
    manager_id: int,
    db: AsyncSession = Depends(get_db)
):
    manager_update = await ManagerRepository(db).toggle_active_manager(manager_id)

    if not manager_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Manager not found"
        )

    return manager_update