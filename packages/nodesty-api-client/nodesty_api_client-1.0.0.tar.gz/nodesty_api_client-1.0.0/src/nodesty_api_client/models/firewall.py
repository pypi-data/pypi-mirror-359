from typing import List, Optional

from pydantic import BaseModel, Field


class AttackNotificationSettings(BaseModel):
    email_notification: bool = Field(alias="emailNotification")
    discord_webhook_url: Optional[str] = Field(alias="discordWebhookURL", default=None)


class FirewallAttackLog(BaseModel):
    started_at: int = Field(alias="startedAt")
    ended_at: Optional[int] = Field(alias="endedAt")
    vectors: List[str]
    peak: int


class FirewallReverseDns(BaseModel):
    rdns: Optional[str] = None


class FirewallRule(BaseModel):
    id: int
    protocol: str
    service: str
    port: int


class FirewallCreateRuleData(BaseModel):
    port: int
    app_id: int = Field(alias="appId")


class FirewallStatistics(BaseModel):
    timestamp: str
    total_pass_traffic: str = Field(alias="totalPassTraffic")
    total_drop_traffic: str = Field(alias="totalDropTraffic")
