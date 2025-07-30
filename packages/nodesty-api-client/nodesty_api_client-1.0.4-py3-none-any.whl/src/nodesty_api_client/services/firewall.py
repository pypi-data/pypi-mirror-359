from typing import List

from src.nodesty_api_client.models.firewall import (
    AttackNotificationSettings,
    FirewallAttackLog,
    FirewallCreateRuleData,
    FirewallReverseDns,
    FirewallRule,
    FirewallStatistics,
)

from src.nodesty_api_client.models.shared import ApiResponse
from src.nodesty_api_client.services.base_service import BaseApiService

class FirewallApiService(BaseApiService):

    async def get_attack_logs(self, service_id: str, ip: str) -> ApiResponse[List[FirewallAttackLog]]:
        return await self._get(f"/services/{service_id}/firewall/{ip}/attack-logs", List[FirewallAttackLog])

    async def get_attack_notification_settings(self, service_id: str, ip: str) -> ApiResponse[AttackNotificationSettings]:
        return await self._get(f"/services/{service_id}/firewall/{ip}/attack-notification", AttackNotificationSettings)

    async def update_attack_notification_settings(
        self,
        service_id: str,
        ip: str,
        settings: AttackNotificationSettings
    ) -> ApiResponse[AttackNotificationSettings]:
        data = settings.model_dump(by_alias=True, exclude_unset=True)
        return await self._put(f"/services/{service_id}/firewall/{ip}/attack-notification", AttackNotificationSettings, data)

    async def reset_reverse_dns(self, service_id: str, ip: str) -> ApiResponse[tuple]:
        return await self._delete(f"/services/{service_id}/firewall/{ip}/rdns", tuple)

    async def get_reverse_dns(self, service_id: str, ip: str) -> ApiResponse[FirewallReverseDns]:
        return await self._get(f"/services/{service_id}/firewall/{ip}/rdns", FirewallReverseDns)

    async def upsert_reverse_dns(self, service_id: str, ip: str, rdns: str) -> ApiResponse[tuple]:
        data = {"rdns": rdns}
        return await self._put(f"/services/{service_id}/firewall/{ip}/rdns", tuple, data)

    async def delete_rule(self, service_id: str, ip: str, rule_id: str) -> ApiResponse[tuple]:
        return await self._delete(f"/services/{service_id}/firewall/{ip}/rules/{rule_id}", tuple)

    async def get_rules(self, service_id: str, ip: str) -> ApiResponse[List[FirewallRule]]:
        return await self._get(f"/services/{service_id}/firewall/{ip}/rules", List[FirewallRule])

    async def create_rule(self, service_id: str, ip: str, rule_data: FirewallCreateRuleData) -> ApiResponse[tuple]:
        data = rule_data.model_dump(by_alias=True)
        return await self._post(f"/services/{service_id}/firewall/{ip}/rules", tuple, data)

    async def get_statistics(self, service_id: str, ip: str) -> ApiResponse[List[FirewallStatistics]]:
        return await self._get(f"/services/{service_id}/firewall/{ip}/stats", List[FirewallStatistics])