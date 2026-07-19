from enum import Enum


class SleepState(str, Enum):
    AWAKE = "awake"
    ASLEEP = "asleep"


class NodeHealth(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    DEAD = "dead"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EMERGENCY = "emergency"