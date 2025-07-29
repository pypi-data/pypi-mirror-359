from enum import Enum
from typing import List

from pydantic import BaseModel, Field


class DedicatedServerAction(str, Enum):
    START = "setPowerOn"
    STOP = "setPowerOff"
    RESTART = "setPowerReset"


class DedicatedServerCpuDetails(BaseModel):
    model: str
    speed: int
    turbo_speed: int = Field(alias="turboSpeed")
    cores: int
    threads: int


class DedicatedServerDetails(BaseModel):
    dedicated_id: str = Field(alias="dedicatedId")
    status: bool
    available_actions: List[DedicatedServerAction] = Field(alias="availableActions")
    mainboard: str
    ram: int
    disk: int
    cpu: DedicatedServerCpuDetails


class DedicatedServerOsTemplate(BaseModel):
    id: int
    name: str


class DedicatedServerReinstallData(BaseModel):
    password: str
    os_id: int = Field(alias="osId")


class DedicatedServerTask(BaseModel):
    action: str
    started_at: int = Field(alias="startedAt")
    updated_at: int = Field(alias="updatedAt")


class DedicatedServerHardwareComponent(BaseModel):
    component: str
    model: str
    value: int
    value_suffix: str = Field(alias="valueSuffix")


class DedicatedServerReinstallStep(int, Enum):
    REBOOTING_SERVER = 0
    PREPARING_BOOT_ENVIRONMENT = 1
    INSTALLING_OPERATING_SYSTEM = 2
    INSTALLATION_COMPLETED = 3


class DedicatedServerReinstallStatus(BaseModel):
    step: DedicatedServerReinstallStep
    completed: bool = Field(alias="isCompleted")
