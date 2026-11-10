from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.schedule import ScheduleResponse, ScheduleBulkUpdate, ScheduleUpdateTime
from app.core.database import get_db
from app.repositories.schedule import ScheduleRepository


router = APIRouter(prefix="/schedule", tags=["Schedule"])


@router.get("/get/all", response_model=list[ScheduleResponse], status_code=status.HTTP_200_OK)
async def get_all_schedules(
    db: AsyncSession = Depends(get_db)
):
    schedules = await ScheduleRepository(db).get_all_schedules()
    return schedules
    

@router.get("/get/by_day/{working_day}", response_model=ScheduleResponse, status_code=status.HTTP_200_OK)
async def get_schedule_by_day(
    working_day: int,
    db: AsyncSession = Depends(get_db)
):
    schedule = await ScheduleRepository(db).get_schedule_by_day(working_day)

    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )

    return schedule


@router.patch("/{working_day}/toggle", response_model=ScheduleResponse, status_code=status.HTTP_200_OK)
async def toggle_working_day(
    working_day: int,
    db: AsyncSession = Depends(get_db)
):
    schedule_update = await ScheduleRepository(db).toggle_working_day(working_day)

    if not schedule_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )

    return schedule_update


@router.patch("/{working_day}/update-time", response_model=ScheduleResponse, status_code=status.HTTP_200_OK)
async def update_day_time(
    working_day: int,
    time_in: ScheduleUpdateTime,
    db: AsyncSession = Depends(get_db)
):
    schedule_update = await ScheduleRepository(db).update_day_time(working_day, time_in)
    
    if not schedule_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )

    return schedule_update


@router.patch("/update-all", response_model=list[ScheduleResponse], status_code=status.HTTP_200_OK)
async def update_all_days(
    time_in: ScheduleBulkUpdate,
    db: AsyncSession = Depends(get_db)
):
    schedule_update = await ScheduleRepository(db).update_all_days(time_in)
    return schedule_update