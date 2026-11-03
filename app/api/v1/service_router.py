from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.service import ServiceCreate, ServiceResponse
from app.core.database import get_db
from app.repositories.service import ServiceRepository


router = APIRouter(prefix="/service", tags=["Service"])


@router.post("/add/service", response_model=ServiceResponse, status_code=status.HTTP_201_CREATED)
async def create_service(
    service_in: ServiceCreate,
    db: AsyncSession = Depends(get_db)
):
    service_repo = ServiceRepository(db)

    exist_service = await service_repo.get_service_by_title(service_in.title)

    if exist_service:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Service already exist"
        )
    
    new_service = await service_repo.create_service(service_in)
    return new_service


@router.get("/get/by_id/{service_id}", response_model=ServiceResponse, status_code=status.HTTP_200_OK)
async def get_service_by_id(
    service_id: int,
    db: AsyncSession = Depends(get_db)
):
    response = await ServiceRepository(db).get_service_by_id(service_id)
    if not response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )

    return response


@router.get("/get/by_title/{service_title}", response_model=ServiceResponse, status_code=status.HTTP_200_OK)
async def get_service_by_title(
    service_title: str,
    db: AsyncSession = Depends(get_db)
):
    response = await ServiceRepository(db).get_service_by_title(service_title)
    if not response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )

    return response


@router.get("/get/all", response_model=list[ServiceResponse], status_code=status.HTTP_200_OK)
async def get_all_services(
    db: AsyncSession = Depends(get_db)
):
    response = await ServiceRepository(db).get_all_services()
    return response