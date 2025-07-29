from enum import Enum
from typing import List, Optional, Dict

from pydantic import BaseModel, Field


class VpsAction(str, Enum):
    START = "start"
    STOP = "stop"
    RESTART = "restart"
    POWER_OFF = "poweroff"


class VpsBackup(BaseModel):
    date: str
    file: str
    created_at: int = Field(alias="createdAt")


class VpsChangePasswordData(BaseModel):
    username: str
    password: str

class VpsCpuDetails(BaseModel):
    manu: str
    limit: int
    used: int
    free: int
    percent: float
    cores: int

class VpsRamDetails(BaseModel):
    limit: int
    used: int
    free: int
    percent: int

class VpsInodeDetails(BaseModel):
    limit: int
    used: int
    free: int
    percent: int

class VpsDiskDetails(BaseModel):
    limit: int
    used: int
    free: int
    percent: int

class VpsNetworkDetails(BaseModel):
    limit: int
    used: int
    free: int
    percent: int

class VpsVncDetails(BaseModel):
    enabled: bool
    port: int
    password: str
    url: str

class VpsOsInfo(BaseModel):
    name: str
    distro: str


class VpsBandwidthOverall(BaseModel):
    used: int
    bandwith_in: int

class VpsBandwidth(BaseModel):
    total: VpsBandwidthOverall
    usage: List[int]
    bandwidth_in: List[int] = Field(alias="in")
    out: List[int]
    categories: List[str]

class VpsDetails(BaseModel):
    vps_id: int = Field(alias="vpsId")
    proxmox_id: int = Field(alias="proxmoxId")
    hostname: str
    status: bool
    vnc: VpsVncDetails
    os: VpsOsInfo
    disk: VpsDiskDetails
    ips: List[str]
    cpu: VpsCpuDetails
    ram: VpsRamDetails
    inode: VpsInodeDetails
    netspeed: VpsNetworkDetails
    bandwidth: VpsBandwidth

class VpsOsTemplate(BaseModel):
    id: int
    name: str

class VpsReinstallData(BaseModel):
    os_id: int = Field(alias="osId")
    password: str

class VpsTask(BaseModel):
    action: str
    started_at: int = Field(alias="startedAt")
    updated_at: int = Field(alias="updatedAt")

class VpsGraphs(BaseModel):
    avg_download: int = Field(alias="avgDownload")
    avg_upload: int = Field(alias="avgUpload")
    avg_io_read: int = Field(alias="avgIoRead")
    avg_io_write: int = Field(alias="avgIoWrite")
    cpu_usage: Dict[str, float] = Field(alias="cpuUsage")
    inode_usage: Dict[str, int] = Field(alias="inodeUsage")
    ram_usage: Dict[str, int] = Field(alias="ramUsage")
    disk_usage: Dict[str, int] = Field(alias="diskUsage")
    io_speed: "VpsIoSpeed" = Field(alias="ioSpeed")
    network_speed: "VpsNetworkSpeedGraph" = Field(alias="networkSpeed")


class VpsIoSpeed(BaseModel):
    read: List[int]
    write: List[int]
    categories: List[int]

class VpsNetworkSpeedGraph(BaseModel):
    download: List[int]
    upload: List[int]
    categories: List[int]