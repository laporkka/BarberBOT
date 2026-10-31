from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.barber import BarberCreate, BarberResponse
from app.core.database import get_db
from app.repositories.barber import BarberRepository


router = APIRouter(prefix="/barber", tags=["Barber"])


@router.post("/add", response_model=BarberResponse, status_code=status.HTTP_201_CREATED)
async def create_barber(
    barber_in: BarberCreate,
    db: AsyncSession = Depends(get_db)
):
    barber_repo = BarberRepository(db)

    exist_barber = await barber_repo.get_barber_by_tg_id(barber_in.tg_id)
    
    if exist_barber:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Barber already exist"
        )

    new_barber = await barber_repo.create_barber(barber_in)
    return new_barber


@router.get("/get/all_active", response_model=list[BarberResponse], status_code=status.HTTP_200_OK)
async def get_active_barbers(
    db: AsyncSession = Depends(get_db)
):
    response = await BarberRepository(db).get_active_barbers()
    return response


@router.get("/get/all", response_model=list[BarberResponse], status_code=status.HTTP_200_OK)
async def get_all_barbers(
    db: AsyncSession = Depends(get_db)
):
    response = await BarberRepository(db).get_all_barbers()
    return response


@router.get("/get/by_id/{barber_id}", response_model=BarberResponse, status_code=status.HTTP_200_OK)
async def get_barber_by_id(
    barber_id: int,
    db: AsyncSession = Depends(get_db)
):
    response = await BarberRepository(db).get_barber_by_id(barber_id)
    if not response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Barber not found"
        )
    
    return response


@router.get("/get/by_tg_id/{barber_tg_id}", response_model=BarberResponse, status_code=status.HTTP_200_OK)
async def get_barber_by_tg_id(
    barber_tg_id: str,
    db: AsyncSession = Depends(get_db)    
):
    response = await BarberRepository(db).get_barber_by_tg_id(barber_tg_id)
    if not response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Barber not found"
        )
    
    return response

