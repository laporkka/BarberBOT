from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, date

from app.schemas.appointment import AppointmentCreate, AppointmentResponse
from app.core.database import get_db
from app.repositories.appointment import AppointmentRepository
from app.repositories.service import ServiceRepository
from app.services.schedule import ScheduleService


router = APIRouter(prefix="/appointment", tags=["Appointment"])


@router.post("/add/appointment", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
async def create_record(
    appointment_in: AppointmentCreate,
    db: AsyncSession = Depends(get_db)
):
    service = await ServiceRepository(db).get_service_by_id(appointment_in.service_id)

    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )

    new_appointment = await AppointmentRepository(db).create_appointment(appointment_in, service.duration_min)
    return new_appointment


@router.get("/get/available_time", response_model=list, status_code=status.HTTP_200_OK)
async def get_available_time(
    duration_min: int,
    barber_id: int,
    target_data: date,
    db: AsyncSession = Depends(get_db)
):
    appointment_repo = AppointmentRepository(db)
    
    available_time = await ScheduleService(appointment_repo).get_available_time(duration_min, barber_id, target_data)
    return available_time


@router.get("/get/by_tg_id/{customer_tg_id}", response_model=list[AppointmentResponse], status_code=status.HTTP_200_OK)
async def get_client_appointments(
    customer_tg_id: str,
    db: AsyncSession = Depends(get_db)
):
    appointments = await AppointmentRepository(db).get_appointments_by_tg_id(customer_tg_id)
    return appointments


@router.get("/get/by_barber", response_model=list[AppointmentResponse], status_code=status.HTTP_200_OK)
async def get_appointments_by_barber(
    barber_id: int,
    target_date: date,
    db: AsyncSession = Depends(get_db)
):
    appointments = await AppointmentRepository(db).get_by_barber_and_date(barber_id, target_date)
    return appointments


@router.get("/get/all/by_date", response_model=list[AppointmentResponse], status_code=status.HTTP_200_OK)
async def get_appointmens_by_date(
    target_date: date,
    db: AsyncSession = Depends(get_db)
):
    appointments = await AppointmentRepository(db).get_all_by_date(target_date)
    return appointments