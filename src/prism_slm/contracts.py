"""Typed contracts for heterogeneous host telemetry."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable


class SemanticGroup(str, Enum):
    COMPUTE = "compute"
    MEMORY = "memory"
    IO = "io"
    THERMAL_POWER = "thermal_power"
    ACCELERATOR = "accelerator"
    AVAILABILITY = "availability"


@dataclass(frozen=True)
class ChannelSpec:
    native_name: str
    unit: str
    semantic_group: SemanticGroup
    source: str
    sampling_period_seconds: float
    cumulative: bool = False
    description: str = ""

    def __post_init__(self) -> None:
        if not self.native_name.strip():
            raise ValueError("native_name must be non-empty")
        if not self.unit.strip():
            raise ValueError("unit must be non-empty")
        if not self.source.strip():
            raise ValueError("source must be non-empty")
        if self.sampling_period_seconds <= 0:
            raise ValueError("sampling_period_seconds must be positive")


@dataclass(frozen=True)
class PlatformSpec:
    platform_id: str
    architecture: str
    operating_system: str
    observability: str
    channels: tuple[ChannelSpec, ...] = field(default_factory=tuple)

    @classmethod
    def from_channels(
        cls,
        *,
        platform_id: str,
        architecture: str,
        operating_system: str,
        observability: str,
        channels: Iterable[ChannelSpec],
    ) -> "PlatformSpec":
        return cls(
            platform_id=platform_id,
            architecture=architecture,
            operating_system=operating_system,
            observability=observability,
            channels=tuple(channels),
        )

    def __post_init__(self) -> None:
        values = {
            "platform_id": self.platform_id,
            "architecture": self.architecture,
            "operating_system": self.operating_system,
            "observability": self.observability,
        }
        for name, value in values.items():
            if not value.strip():
                raise ValueError(f"{name} must be non-empty")

        names = [channel.native_name for channel in self.channels]
        if len(names) != len(set(names)):
            raise ValueError("channel native_name values must be unique per platform")

    @property
    def available_groups(self) -> frozenset[SemanticGroup]:
        return frozenset(channel.semantic_group for channel in self.channels)
