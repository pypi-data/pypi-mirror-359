from typing import List

from src.nodesty_api_client.models.shared import ApiResponse

from src.nodesty_api_client.models.user import (
    Service,
    Ticket,
    User,
    Invoice,
    Session,
)

from src.nodesty_api_client.services.base_service import BaseApiService


class UserApiService(BaseApiService):

    async def get_services(self) -> ApiResponse[List[Service]]:
        return await self._get("/services", List[Service])

    async def get_ticket_by_id(self, ticket_id: str) -> ApiResponse[Ticket]:
        return await self._get(f"/tickets/{ticket_id}", Ticket)

    async def get_tickets(self) -> ApiResponse[List[Ticket]]:
        return await self._get("/tickets", List[Ticket])

    async def get_current_user(self) -> ApiResponse[User]:
        return await self._get("/users/@me", User)

    async def get_invoice_by_id(self, invoice_id: str) -> ApiResponse[Invoice]:
        return await self._get(f"/users/@me/invoices/{invoice_id}", Invoice)

    async def get_invoices(self) -> ApiResponse[List[Invoice]]:
        return await self._get("/users/@me/invoices", List[Invoice])

    async def get_sessions(self) -> ApiResponse[List[Session]]:
        return await self._get("/users/@me/sessions", List[Session])
