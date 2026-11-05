import httpx
from typing import List, Dict, Any
from datetime import datetime, date

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
        return response


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

        response = await self._send_request("POST", "/barber/add", json=json_data)
        return response


    async def get_all_service(self) -> List[Dict[str, Any]]:
        response = await self._send_request("GET", "/service/get/all")
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
        customer_tg_id: str,
        customer_name: str,
        customer_phone: str,
        burber_id: int,
        service_id: int,
        start_at: datetime
    ) -> Dict[str, Any]:
        json_data = {
            "customer_tg_id": customer_tg_id,
            "customer_name": customer_name,
            "customer_phone": customer_phone,
            "burber_id": burber_id,
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
    ):
        params = {
            "duration_min": duration_min,
            "barber_id": barber_id,
            "target_data": target_data.strftime("%Y-%m-%d")
        }

        response = await self._send_request("GET", "/appointment/get/available_time", params=params)
        return response

    async def get_appointments_by_tg_id(self, customer_tg_id: str) -> List[Dict[str, Any]]:
        response = await self._send_request("GET", f"/appointment/get/by_tg_id/{customer_tg_id}")
        return response

    async def get_service_by_id(self, service_id: int) -> Dict[str, Any] | None:
        response = await self._send_request("GET", f"/service/get/by_id/{service_id}")
        return response
    

api_client = ApiClient()
