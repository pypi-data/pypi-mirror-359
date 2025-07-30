from typing import List, Dict

from httpx import AsyncClient

from src.nodesty_api_client.models.shared import ApiResponse
from src.nodesty_api_client.models.vps import (
    VpsBackup,
    VpsAction,
    VpsChangePasswordData,
    VpsDetails,
    VpsGraphs,
    VpsOsTemplate,
    VpsReinstallData,
    VpsTask
)


class VpsApiService:
    def __init__(self, client: AsyncClient, base_url: str, access_token: str):
        self._client = client
        self._base_url = base_url
        self._access_token = access_token

    def _get_headers(self) -> Dict[str, str]:
        return {"Authorization": f"PAT {self._access_token}"}

    async def perform_action(self, id: str, action: VpsAction) -> ApiResponse[tuple]:
        url = f"{self._base_url}/services/{id}/vps/action"
        body = {"action": action.value}
        response = await self._client.post(url, headers=self._get_headers(), json=body)
        response.raise_for_status()
        return ApiResponse[tuple].model.validate(response.json() if response.content else {})

    async def restore_backup(self, id: str, data: VpsBackup) -> ApiResponse[None]:
        url = f"{self._base_url}/services/{id}/vps/backup/restore"
        response = await self._client.post(url, headers=self._get_headers(), json=data.model_dump(by_alias=True))
        response.raise_for_status()
        return ApiResponse[tuple].model.validate(response.json() if response.content else {})

    async def get_backups(self, id: str) -> ApiResponse[List[VpsBackup]]:
        url = f"{self._base_url}/services/{id}/vps/backups"
        response = await self._client.get(url, headers=self._get_headers())
        response.raise_for_status()
        return ApiResponse[List[VpsBackup]].model_validate(response.json())

    async def change_password(self, id: str, data: VpsChangePasswordData) -> ApiResponse[tuple]:
        url = f"{self._base_url}/services/{id}/vps/change-password"
        response = await self._client.put(url, headers=self._get_headers(), json=data.model_dump(by_alias=True))
        response.raise_for_status()
        return ApiResponse[tuple].model.validate(response.json() if response.content else {})

    async def get_details(self, id: str) -> ApiResponse[VpsDetails]:
        url = f"{self._base_url}/services/{id}/vps/info"
        response = await self._client.get(url, headers=self._get_headers())
        response.raise_for_status()
        return ApiResponse[VpsDetails].model.validate(response.json())

    async def get_graphs(self, id: str) -> ApiResponse[VpsGraphs]:
        url = f"{self._base_url}/services/{id}/vps/graphs"
        response = await self._client.get(url, headers=self._get_headers())
        response.raise_for_status()
        return ApiResponse[VpsGraphs].model.validate(response.json())

    async def get_os_templates(self, id: str) -> ApiResponse[List[VpsOsTemplate]]:
        url = f"{self._base_url}/services/{id}/vps/os-templates"
        response = await self._client.get(url, headers=self._get_headers())
        response.raise_for_status()
        return ApiResponse[List[VpsOsTemplate]].model.validate(response.json())

    async def reinstall(self, id: str, data: VpsReinstallData) -> ApiResponse[tuple]:
        url = f"{self._base_url}/services/{id}/vps/reinstall"
        response = await self._client.post(url, headers=self._get_headers(), json=data.model_dump(by_alias=True))
        response.raise_for_status()
        return ApiResponse[tuple].model_validate(response.json() if response.content else {})

    async def get_tasks(self, id: str) -> ApiResponse[List[VpsTask]]:
        url = f"{self._base_url}/services/{id}/vps/tasks"
        response = await self._client.get(url, headers=self._get_headers())
        response.raise_for_status()
        return ApiResponse[List[VpsTask]].model_validate(response.json())
