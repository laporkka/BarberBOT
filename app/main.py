from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.barber_router import router as barber_router
from app.api.v1.service_router import router as service_router
from app.api.v1.appointment_router import router as appointment_router
from app.api.v1.schedule_router import router as schedule_router
from app.api.v1.manager_router import router as manager_router


app = FastAPI(
    title="BarberBOT API",
    version="0.1.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          
    allow_credentials=True,       
    allow_methods=["*"],          
    allow_headers=["*"], 
)


app.include_router(barber_router)
app.include_router(service_router)
app.include_router(appointment_router)
app.include_router(schedule_router)
app.include_router(manager_router)


@app.get("/")
async def root():
    return {"message": "Бэкенд BarberBOT работает!"}