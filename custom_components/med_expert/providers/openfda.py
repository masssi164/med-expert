"""
OpenFDA medication provider (stub).

TODO: Implement OpenFDA API integration for medication lookup.
https://open.fda.gov/apis/drug/

This is a placeholder for future implementation.
"""

from __future__ import annotations

from .base import MedicationCandidate, MedicationDetails, MedicationProvider


class OpenFDAProvider(MedicationProvider):
    """
    Provider for OpenFDA medication database.

    TODO: Implement OpenFDA API integration.
    - Search: /drug/label.json?search=openfda.brand_name:{query}
    - Resolve: /drug/label.json?search=openfda.product_ndc:{ndc}
    """

    @property
    def name(self) -> str:
        """Get the provider name."""
        return "openfda"

    @property
    def display_name(self) -> str:
        """Get the human-readable name."""
        return "OpenFDA (US)"

    async def search(
        self,
        query: str,
        limit: int = 10,
    ) -> list[MedicationCandidate]:
        """
        Search for medications in OpenFDA.

        TODO: Implement OpenFDA API search.

        Args:
            query: Search term.
            limit: Maximum results.

        Returns:
            List of medication candidates.

        Raises:
            NotImplementedError: This provider is not yet implemented.

        """
        msg = (
            "OpenFDA provider is not yet implemented. "
            "Use the 'manual' provider for now."
        )
        raise NotImplementedError(msg)

    async def resolve(
        self,
        external_id: str,
    ) -> MedicationDetails | None:
        """
        Resolve medication details from OpenFDA.

        TODO: Implement OpenFDA API resolve.

        Args:
            external_id: NDC or product identifier.

        Returns:
            Medication details or None.

        Raises:
            NotImplementedError: This provider is not yet implemented.

        """
        msg = (
            "OpenFDA provider is not yet implemented. "
            "Use the 'manual' provider for now."
        )
        raise NotImplementedError(msg)
