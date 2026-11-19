import httpx
from typing import List, Dict, Any
from datetime import datetime, date, time

from app.core.config import settings


class ApiClient:
    def __init__(self):
        self.base_url = "http://api:8000"


    async def _send_request(
        self,
        method: str, 
        path: str,
        **kwargs
    ) -> Any:
        url = f"{self.base_url}{path}"

        async with httpx.AsyncClient() as client:
            try:
                response = await client.request(method, url, **kwargs)

                response.raise_for_status()
                return response.json()
                
            except httpx.HTTPStatusError as e:
                print(f"❌ Ошибка API ({url}): {e.response.status_code} - {e.response.text}")
                return None
            except httpx.RequestError as e:
                print(f"❌ Ошибка сети при запросе к API ({url}): {e}")
                return None


    async def get_active_barbers(self) -> List[Dict[str, Any]]:
        response = await self._send_request("GET", "/barber/get/all_active")
        return response or []


    async def get_all_barbers(self) -> List[Dict[str, Any]]:
        response = await self._send_request("GET", "/barber/get/all")
        return response or []
    

    async def get_barber_by_tg_id(self, tg_id: int) -> Dict[str, Any] | None:
        response = await self._send_request("GET", f"/barber/get/by_tg_id/{tg_id}")
        return response


    async def create_barber(
        self, 
        name: str, 
        tg_id: int, 
        is_active: bool
    ) -> Dict[str, Any]:
        json_data = {
            "name": name,
            "tg_id": tg_id,
            "is_active": is_active
        }

        response = await self._send_request("POST", "/barber/add/barber", json=json_data)
        return response


    async def update_barber_name_by_id(self, barber_id: int, new_name: str) -> Dict[str, Any] | None:
        json_data = {"new_name": new_name} 

        response = await self._send_request("PATCH", f"/barber/{barber_id}/update-name", json=json_data)
        return response


    async def toggle_active_barber_by_id(self, barber_id: int) -> Dict[str, Any] | None:
        response = await self._send_request("PATCH", f"/barber/{barber_id}/toggle-active")
        return response


    async def get_service_by_id(self, service_id: int) -> Dict[str, Any] | None:
        response = await self._send_request("GET", f"/service/get/by_id/{service_id}")
        return response

      
    async def get_all_services(self) -> List[Dict[str, Any]]:
        response = await self._send_request("GET", "/service/get/all")
        return response or []


    async def update_service_price_by_id(self, service_id: int, new_price) -> Dict[str, Any] | None:
        json_data = {"new_price": new_price}

        response = await self._send_request("PATCH", f"/service/{service_id}/update-price", json=json_data)
        return response


    async def toggle_active_service_by_id(self, service_id: int) -> Dict[str, Any] | None:
        response = await self._send_request("PATCH", f"/service/{service_id}/toggle-active")
        return response


    async def create_service(
        self, 
        title: str, 
        price: int, 
        duration_min: int
    ) -> Dict[str, Any]:
        json_data = {
            "title": title,
            "price": price,
            "duration_min": duration_min
        }

        response = await self._send_request("POST", "/service/add/service", json=json_data)
        return response


    async def create_appointment(
        self, 
        customer_tg_id: int,
        customer_name: str,
        customer_phone: str,
        barber_id: int,
        service_id: int,
        start_at: datetime
    ) -> Dict[str, Any]:
        json_data = {
            "customer_tg_id": str(customer_tg_id),
            "customer_name": customer_name,
            "customer_phone": customer_phone,
            "barber_id": barber_id,
            "service_id": service_id,
            "start_at": start_at.isoformat()
        }

        response = await self._send_request("POST", "/appointment/add/appointment", json=json_data)
        return response


    async def get_available_time(
        self,
        duration_min: int,
        barber_id: int,
        target_data: date
    ) -> List[str]:
        params = {
            "duration_min": duration_min,
            "barber_id": barber_id,
            "target_data": target_data.strftime("%Y-%m-%d")
        }

        response = await self._send_request("GET", "/appointment/get/available_time", params=params)
        return response or []


    async def get_appointments_by_tg_id(self, customer_tg_id: str) -> List[Dict[str, Any]]:
        response = await self._send_request("GET", f"/appointment/get/by_tg_id/{customer_tg_id}")
        return response or []


    async def get_appointments_by_barber(self, barber_id: int, target_date: date) -> List[Dict[str, Any]]:
        params = {
            "barber_id": barber_id,
            "target_date": target_date.strftime("%Y-%m-%d")
        }

        response = await self._send_request("GET", "/appointment/get/by_barber", params=params)
        return response or []


    async def get_all_appointments_by_date(self, target_date: str) -> List[Dict[str, Any]]:
        params = {"target_date": target_date}

        response = await self._send_request("GET", "/appointment/get/all/by_date", params=params)
        return response or []


    async def get_all_schedules(self) -> List[Dict[str, Any]]:
        response = await self._send_request("GET", "/schedule/get/all")
        return response or []


    async def get_schedule_by_day(self, working_day: int) -> Dict[str, Any]:
        response = await self._send_request("GET", f"/schedule/get/by_day/{working_day}")
        return response


    async def toggle_schedule_by_day(self, working_day: int) -> Dict[str, Any]:
        response = await self._send_request("PATCH", f"/schedule/{working_day}/toggle")
        return response


    async def update_time_by_day(
        self,
        working_day: int,
        start_at: time | None = None,
        end_at: time | None = None
    ) -> Dict[str, Any]:
        json_data = {}

        if start_at is not None:
            json_data["start_at"] = start_at.isoformat() if isinstance(start_at, time) else start_at
        if end_at is not None:
            json_data["end_at"] = end_at.isoformat() if isinstance(end_at, time) else end_at

        response = await self._send_request("PATCH", f"/schedule/{working_day}/update-time", json=json_data)
        return response


    async def update_all_schedule_by_template(
        self, 
        start_at: time,
        end_at: time
    ) -> List[Dict[str, Any]]:
        json_data = {
            "start_at": start_at.isoformat() if isinstance(start_at, time) else start_at,
            "end_at": end_at.isoformat() if isinstance(end_at, time) else end_at
        }

        response = await self._send_request("PATCH", "/schedule/update-all", json=json_data)
        return response or []


api_client = ApiClient()