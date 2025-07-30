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
from src.nodesty_api_client.services.base_service import BaseApiService

class VpsApiService(BaseApiService):

    async def perform_action(self, id: str, action: VpsAction) -> ApiResponse[tuple]:
        data = {"action": action.value}
        return await self._post(f"/services/{id}/vps/action", tuple, data)

    async def restore_backup(self, id: str, backup_data: VpsBackup) -> ApiResponse[None]:
        data = backup_data.model_dump(by_alias=True)
        return await self._post(f"/services/{id}/vps/backup/restore", type(None), data)

    async def get_backups(self, id: str) -> ApiResponse[List[VpsBackup]]:
        return await self._get(f"/services/{id}/vps/backups", List[VpsBackup])

    async def change_password(self, id: str, password_data: VpsChangePasswordData) -> ApiResponse[tuple]:
        data = password_data.model_dump(by_alias=True)
        return await self._put(f"/services/{id}/vps/change-password", tuple, data)

    async def get_details(self, id: str) -> ApiResponse[VpsDetails]:
        return await self._get(f"/services/{id}/vps/info", VpsDetails)

    async def get_graphs(self, id: str) -> ApiResponse[VpsGraphs]:
        return await self._get(f"/services/{id}/vps/graphs", VpsGraphs)

    async def get_os_templates(self, id: str) -> ApiResponse[List[VpsOsTemplate]]:
        return await self._get(f"/services/{id}/vps/os-templates", List[VpsOsTemplate])

    async def reinstall(self, id: str, reinstall_data: VpsReinstallData) -> ApiResponse[tuple]:
        data = reinstall_data.model_dump(by_alias=True)
        return await self._post(f"/services/{id}/vps/reinstall", tuple, data)

    async def get_tasks(self, id: str) -> ApiResponse[List[VpsTask]]:
        return await self._get(f"/services/{id}/vps/tasks", List[VpsTask])