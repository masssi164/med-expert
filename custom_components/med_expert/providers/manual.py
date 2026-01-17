"""
Manual medication provider.

Provides a simple provider for manually entered medications.
No external API calls - medications are defined locally.
"""

from __future__ import annotations

from .base import MedicationCandidate, MedicationDetails, MedicationProvider


class ManualProvider(MedicationProvider):
    """
    Provider for manually entered medications.

    This provider doesn't perform any external lookups.
    Medications are created directly by the user with their own data.
    """

    @property
    def name(self) -> str:
        """Get the provider name."""
        return "manual"

    @property
    def display_name(self) -> str:
        """Get the human-readable name."""
        return "Manual Entry"

    async def search(
        self,
        query: str,
        limit: int = 10,
    ) -> list[MedicationCandidate]:
        """
        Search for medications.

        For manual provider, this returns an empty list since
        there's no external database to search.
        Users create medications with their own data.

        Args:
            query: Search term (ignored).
            limit: Maximum results (ignored).

        Returns:
            Empty list.

        """
        # Manual provider doesn't have a searchable database
        # Users enter medication details directly
        return []

    async def resolve(
        self,
        external_id: str,
    ) -> MedicationDetails | None:
        """
        Resolve medication details.

        For manual provider, the external_id IS the medication,
        so we return a basic MedicationDetails.

        Args:
            external_id: The medication ID (same as display name for manual).

        Returns:
            Basic medication details.

        """
        # For manual entries, external_id is typically the display name
        return MedicationDetails(
            provider=self.name,
            external_id=external_id,
            display_name=external_id,
            default_dose_unit="tablet",
        )

    def create_candidate(
        self,
        display_name: str,
        dosage_form: str = "tablet",
        strength: str | None = None,
    ) -> MedicationCandidate:
        """
        Create a medication candidate from user input.

        Args:
            display_name: The medication name.
            dosage_form: Form of medication (tablet, capsule, etc.).
            strength: Optional strength (100mg, etc.).

        Returns:
            A medication candidate.

        """
        import uuid

        external_id = str(uuid.uuid4())
        return MedicationCandidate(
            provider=self.name,
            external_id=external_id,
            display_name=display_name,
            dosage_form=dosage_form,
            strength=strength,
        )
