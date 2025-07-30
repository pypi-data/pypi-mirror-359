from typing import List, Dict

from httpx import AsyncClient

from src.nodesty_api_client.models.dedicated import (
    DedicatedServerAction,
    DedicatedServerDetails,
    DedicatedServerHardwareComponent,
    DedicatedServerOsTemplate,
    DedicatedServerReinstallData,
    DedicatedServerReinstallStatus,
    DedicatedServerTask,
)
from src.nodesty_api_client.models.shared import ApiResponse
from src.nodesty_api_client.services.base_service import BaseApiService

class DedicatedServerApiService(BaseApiService):

    async def perform_action(self, id: str, action: DedicatedServerAction) -> ApiResponse[tuple]:
        data = {"action": action.value}
        return await self._post(f"/services/{id}/dedicated/action", tuple, data)

    async def get_hardware_components(self, id: str) -> ApiResponse[List[DedicatedServerHardwareComponent]]:
        return await self._get(f"/services/{id}/dedicated/hardware", List[DedicatedServerHardwareComponent])

    async def get_information(self, id: str) -> ApiResponse[DedicatedServerDetails]:
        return await self._get(f"/services/{id}/dedicated/info", DedicatedServerDetails)

    async def get_os_templates(self, id: str) -> ApiResponse[List[DedicatedServerOsTemplate]]:
        return await self._get(f"/services/{id}/dedicated/os-templates", List[DedicatedServerOsTemplate])

    async def get_reinstall_status(self, id: str) -> ApiResponse[DedicatedServerReinstallStatus]:
        return await self._get(f"/services/{id}/dedicated/reinstall-status", DedicatedServerReinstallStatus)

    async def reinstall(self, id: str, reinstall_data: DedicatedServerReinstallData) -> ApiResponse[tuple]:
        data = reinstall_data.model_dump(by_alias=True)
        return await self._post(f"/services/{id}/dedicated/reinstall", tuple, data)

    async def get_tasks(self, id: str) -> ApiResponse[List[DedicatedServerTask]]:
        return await self._get(f"/services/{id}/dedicated/tasks", List[DedicatedServerTask])
