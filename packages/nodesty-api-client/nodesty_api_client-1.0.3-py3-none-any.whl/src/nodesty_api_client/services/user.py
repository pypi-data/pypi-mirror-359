from typing import List, Dict

from httpx import AsyncClient

from src.nodesty_api_client.models.shared import ApiResponse
from src.nodesty_api_client.models.user import (
    Service,
    Ticket,
    User,
    Invoice,
    Session,
)


class UserApiService:
    def __init__(self, client: AsyncClient, base_url: str, access_token: str):
        self._client = client
        self._base_url = base_url
        self._access_token = access_token

    def _get_headers(self) -> Dict[str, str]:
        return {"Authorization": f"PAT {self._access_token}"}

    async def get_services(self) -> ApiResponse[List[Service]]:
        url = f"{self._base_url}/services"
        response = await self._client.get(url, headers=self._get_headers())
        response.raise_for_status()
        return ApiResponse[List[Service]].model_validate(response.json())

    async def get_ticket_by_id(self, ticket_id: str) -> ApiResponse[Ticket]:
        url = f"{self._base_url}/tickets/{ticket_id}"
        response = await self._client.get(url, headers=self._get_headers())
        response.raise_for_status()
        return ApiResponse[Ticket].model_validate(response.json())

    async def get_tickets(self) -> ApiResponse[List[Ticket]]:
        url = f"{self._base_url}/tickets"
        response = await self._client.get(url, headers=self._get_headers())
        response.raise_for_status()
        return ApiResponse[List[Ticket]].model_validate(response.json())

    async def get_current_user(self) -> ApiResponse[User]:
        url = f"{self._base_url}/users/@me"
        response = await self._client.get(url, headers=self._get_headers())
        response.raise_for_status()
        return ApiResponse[User].model_validate(response.json())

    async def get_invoice_by_id(self, invoice_id: str) -> ApiResponse[Invoice]:
        url = f"{self._base_url}/users/@me/invoices/{invoice_id}"
        response = await self._client.get(url, headers=self._get_headers())
        response.raise_for_status()
        return ApiResponse[Invoice].model_validate(response.json())

    async def get_invoices(self) -> ApiResponse[List[Invoice]]:
        url = f"{self._base_url}/users/@me/invoices"
        response = await self._client.get(url, headers=self._get_headers())
        response.raise_for_status()
        return ApiResponse[List[Invoice]].model_validate(response.json())

    async def get_sessions(self) -> ApiResponse[List[Session]]:
        url = f"{self._base_url}/users/@me/sessions"
        response = await self._client.get(url, headers=self._get_headers())
        response.raise_for_status()
        return ApiResponse[List[Session]].model_validate(response.json())
