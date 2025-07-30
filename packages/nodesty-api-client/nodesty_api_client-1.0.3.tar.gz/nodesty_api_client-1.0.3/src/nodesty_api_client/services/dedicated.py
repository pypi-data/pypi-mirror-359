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


class DedicatedServerApiService:
    def __init__(self, client: AsyncClient, base_url: str, access_token: str):
        self._client = client
        self._base_url = base_url
        self._access_token = access_token

    def _get_headers(self) -> Dict[str, str]:
        return {"Authorization": f"PAT {self._access_token}"}

    async def perform_action(self, id: str, action: DedicatedServerAction) -> ApiResponse[tuple]:
        url = f"{self._base_url}/services/{id}/dedicated/action"
        body = {"action": action.value}
        response = await self._client.post(url, headers=self._get_headers(), json=body)
        response.raise_for_status()
        return ApiResponse[tuple].model_validate(response.json() if response.content else {})

    async def get_hardware_components(self, id: str) -> ApiResponse[List[DedicatedServerHardwareComponent]]:
        url = f"{self._base_url}/services/{id}/dedicated/hardware"
        response = await self._client.get(url, headers=self._get_headers())
        response.raise_for_status()
        return ApiResponse[List[DedicatedServerHardwareComponent]].model_validate(response.json())

    async def get_information(self, id: str) -> ApiResponse[DedicatedServerDetails]:
        url = f"{self._base_url}/services/{id}/dedicated/info"
        response = await self._client.get(url, headers=self._get_headers())
        response.raise_for_status()
        return ApiResponse[DedicatedServerDetails].model_validate(response.json())

    async def get_os_templates(self, id: str) -> ApiResponse[List[DedicatedServerOsTemplate]]:
        url = f"{self._base_url}/services/{id}/dedicated/os-templates"
        response = await self._client.get(url, headers=self._get_headers())
        response.raise_for_status()
        return ApiResponse[List[DedicatedServerOsTemplate]].model_validate(response.json())

    async def get_reinstall_status(self, id: str) -> ApiResponse[DedicatedServerReinstallStatus]:
        url = f"{self._base_url}/services/{id}/dedicated/reinstall-status"
        response = await self._client.get(url, headers=self._get_headers())
        response.raise_for_status()
        return ApiResponse[DedicatedServerReinstallStatus].model_validate(response.json())

    async def reinstall(self, id: str, data: DedicatedServerReinstallData) -> ApiResponse[tuple]:
        url = f"{self._base_url}/services/{id}/dedicated/reinstall"
        response = await self._client.post(url, headers=self._get_headers(), json=data.model_dump(by_alias=True))
        response.raise_for_status()
        return ApiResponse[tuple].model_validate(response.json() if response.content else {})

    async def get_tasks(self, id: str) -> ApiResponse[List[DedicatedServerTask]]:
        url = f"{self._base_url}/services/{id}/dedicated/tasks"
        response = await self._client.get(url, headers=self._get_headers())
        response.raise_for_status()
        return ApiResponse[List[DedicatedServerTask]].model_validate(response.json())
