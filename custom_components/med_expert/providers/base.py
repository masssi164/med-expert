"""
Base provider interface and DTOs.

Providers are responsible for medication lookup/search functionality.
This allows for future integration with external medication databases.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class MedicationCandidate:
    """
    A candidate medication from a search result.

    Represents a medication that can be selected by the user.
    """

    provider: str
    external_id: str
    display_name: str
    description: str | None = None
    dosage_form: str | None = None  # e.g., "tablet", "capsule", "liquid"
    strength: str | None = None  # e.g., "100mg", "500mg"
    manufacturer: str | None = None
    meta: dict[str, Any] | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "provider": self.provider,
            "external_id": self.external_id,
            "display_name": self.display_name,
            "description": self.description,
            "dosage_form": self.dosage_form,
            "strength": self.strength,
            "manufacturer": self.manufacturer,
            "meta": self.meta,
        }


@dataclass
class MedicationDetails:
    """
    Detailed information about a medication.

    Extended information retrieved when resolving a specific medication.
    """

    provider: str
    external_id: str
    display_name: str
    description: str | None = None
    dosage_form: str | None = None
    strength: str | None = None
    manufacturer: str | None = None
    active_ingredients: list[str] | None = None
    warnings: list[str] | None = None
    interactions: list[str] | None = None
    default_dose_unit: str | None = None
    meta: dict[str, Any] | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "provider": self.provider,
            "external_id": self.external_id,
            "display_name": self.display_name,
            "description": self.description,
            "dosage_form": self.dosage_form,
            "strength": self.strength,
            "manufacturer": self.manufacturer,
            "active_ingredients": self.active_ingredients,
            "warnings": self.warnings,
            "interactions": self.interactions,
            "default_dose_unit": self.default_dose_unit,
            "meta": self.meta,
        }


class MedicationProvider(ABC):
    """
    Abstract base class for medication providers.

    Providers implement medication search and resolution functionality.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Get the provider name/identifier."""

    @property
    @abstractmethod
    def display_name(self) -> str:
        """Get the human-readable provider name."""

    @abstractmethod
    async def search(
        self,
        query: str,
        limit: int = 10,
    ) -> list[MedicationCandidate]:
        """
        Search for medications matching a query.

        Args:
            query: Search term.
            limit: Maximum number of results.

        Returns:
            List of matching medication candidates.

        """

    @abstractmethod
    async def resolve(
        self,
        external_id: str,
    ) -> MedicationDetails | None:
        """
        Resolve detailed information for a medication.

        Args:
            external_id: The provider-specific medication ID.

        Returns:
            Medication details or None if not found.

        """


class ProviderRegistry:
    """Registry for medication providers."""

    def __init__(self) -> None:
        """Initialize the registry."""
        self._providers: dict[str, MedicationProvider] = {}

    def register(self, provider: MedicationProvider) -> None:
        """
        Register a provider.

        Args:
            provider: The provider to register.

        """
        self._providers[provider.name] = provider

    def get(self, name: str) -> MedicationProvider | None:
        """
        Get a provider by name.

        Args:
            name: The provider name.

        Returns:
            The provider or None.

        """
        return self._providers.get(name)

    def get_all(self) -> list[MedicationProvider]:
        """
        Get all registered providers.

        Returns:
            List of all providers.

        """
        return list(self._providers.values())

    async def search_all(
        self,
        query: str,
        limit: int = 10,
    ) -> list[MedicationCandidate]:
        """
        Search all providers.

        Args:
            query: Search term.
            limit: Maximum results per provider.

        Returns:
            Combined list of candidates from all providers.

        """
        results: list[MedicationCandidate] = []
        for provider in self._providers.values():
            try:
                candidates = await provider.search(query, limit)
                results.extend(candidates)
            except Exception:
                # Log error but continue with other providers
                pass
        return results
