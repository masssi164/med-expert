"""Custom types for med_expert."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry

    from .runtime.manager import ProfileManager


type MedExpertConfigEntry = ConfigEntry[MedExpertData]


@dataclass
class MedExpertData:
    """Data for the Med Expert integration."""

    manager: ProfileManager
