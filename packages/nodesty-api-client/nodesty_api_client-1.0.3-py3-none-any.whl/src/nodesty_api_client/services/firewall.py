from typing import List, Dict

from httpx import AsyncClient

from src.nodesty_api_client.models.firewall import (
    AttackNotificationSettings,
    FirewallAttackLog,
    FirewallCreateRuleData,
    FirewallReverseDns,
    FirewallRule,
    FirewallStatistics,
)
from src.nodesty_api_client.models.shared import ApiResponse


class FirewallApiService:
    def __init__(self, client: AsyncClient, base_url: str, access_token: str):
        self._client = client
        self._base_url = base_url
        self._access_token = access_token

    def _get_headers(self) -> Dict[str, str]:
        return {"Authorization": f"PAT {self._access_token}"}

    async def get_attack_logs(self, service_id: str, ip: str) -> ApiResponse[List[FirewallAttackLog]]:
        url = f"{self._base_url}/services/{service_id}/firewall/{ip}/attack-logs"
        response = await self._client.get(url, headers=self._get_headers())
        response.raise_for_status()
        return ApiResponse[List[FirewallAttackLog]].model_validate(response.json())

    async def get_attack_notification_settings(self, service_id: str, ip: str) -> ApiResponse[
        AttackNotificationSettings]:
        url = f"{self._base_url}/services/{service_id}/firewall/{ip}/attack-notification"
        response = await self._client.get(url, headers=self._get_headers())
        response.raise_for_status()
        return ApiResponse[AttackNotificationSettings].model_validate(response.json())

    async def update_attack_notification_settings(self, service_id: str, ip: str, data: AttackNotificationSettings) -> \
    ApiResponse[AttackNotificationSettings]:
        url = f"{self._base_url}/services/{service_id}/firewall/{ip}/attack-notification"
        response = await self._client.put(url, headers=self._get_headers(),
                                          json=data.model_dump(by_alias=True, exclude_unset=True))
        response.raise_for_status()
        return ApiResponse[AttackNotificationSettings].model_validate(response.json())

    async def reset_reverse_dns(self, service_id: str, ip: str) -> ApiResponse[tuple]:
        url = f"{self._base_url}/services/{service_id}/firewall/{ip}/rdns"
        response = await self._client.delete(url, headers=self._get_headers())
        response.raise_for_status()
        return ApiResponse[tuple].model_validate(response.json() if response.content else {})

    async def get_reverse_dns(self, service_id: str, ip: str) -> ApiResponse[FirewallReverseDns]:
        url = f"{self._base_url}/services/{service_id}/firewall/{ip}/rdns"
        response = await self._client.get(url, headers=self._get_headers())
        response.raise_for_status()
        return ApiResponse[FirewallReverseDns].model_validate(response.json())

    async def upsert_reverse_dns(self, service_id: str, ip: str, rdns: str) -> ApiResponse[tuple]:
        url = f"{self._base_url}/services/{service_id}/firewall/{ip}/rdns"
        body = {"rdns": rdns}
        response = await self._client.put(url, headers=self._get_headers(), json=body)
        response.raise_for_status()
        return ApiResponse[tuple].model_validate(response.json() if response.content else {})

    async def delete_rule(self, service_id: str, ip: str, rule_id: str) -> ApiResponse[tuple]:
        url = f"{self._base_url}/services/{service_id}/firewall/{ip}/rules/{rule_id}"
        response = await self._client.delete(url, headers=self._get_headers())
        response.raise_for_status()
        return ApiResponse[tuple].model_validate(response.json() if response.content else {})

    async def get_rules(self, service_id: str, ip: str) -> ApiResponse[List[FirewallRule]]:
        url = f"{self._base_url}/services/{service_id}/firewall/{ip}/rules"
        response = await self._client.get(url, headers=self._get_headers())
        response.raise_for_status()
        return ApiResponse[List[FirewallRule]].model_validate(response.json())

    async def create_rule(self, service_id: str, ip: str, data: FirewallCreateRuleData) -> ApiResponse[tuple]:
        url = f"{self._base_url}/services/{service_id}/firewall/{ip}/rules"
        response = await self._client.post(url, headers=self._get_headers(), json=data.model_dump(by_alias=True))
        response.raise_for_status()
        return ApiResponse[tuple].model_validate(response.json() if response.content else {})

    async def get_statistics(self, service_id: str, ip: str) -> ApiResponse[List[FirewallStatistics]]:
        url = f"{self._base_url}/services/{service_id}/firewall/{ip}/stats"
        response = await self._client.get(url, headers=self._get_headers())
        response.raise_for_status()
        return ApiResponse[List[FirewallStatistics]].model_validate(response.json())
