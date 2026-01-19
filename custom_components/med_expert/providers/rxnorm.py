"""
RxNorm medication provider (stub).

TODO: Implement RxNorm API integration for US medication lookup.
https://lhncbc.nlm.nih.gov/RxNav/APIs/RxNormAPIs.html

This is a placeholder for future implementation.
"""

from __future__ import annotations

from .base import MedicationCandidate, MedicationDetails, MedicationProvider


class RxNormProvider(MedicationProvider):
    """
    Provider for RxNorm medication database.

    TODO: Implement RxNorm API integration.
    - Search: /REST/drugs?name={query}
    - Resolve: /REST/rxcui/{rxcui}/properties
    """

    @property
    def name(self) -> str:
        """Get the provider name."""
        return "rxnorm"

    @property
    def display_name(self) -> str:
        """Get the human-readable name."""
        return "RxNorm (US)"

    async def search(
        self,
        query: str,
        limit: int = 10,
    ) -> list[MedicationCandidate]:
        """
        Search for medications in RxNorm.

        TODO: Implement RxNorm API search.

        Args:
            query: Search term.
            limit: Maximum results.

        Returns:
            List of medication candidates.

        Raises:
            NotImplementedError: This provider is not yet implemented.

        """
        msg = (
            "RxNorm provider is not yet implemented. Use the 'manual' provider for now."
        )
        raise NotImplementedError(msg)

    async def resolve(
        self,
        external_id: str,
    ) -> MedicationDetails | None:
        """
        Resolve medication details from RxNorm.

        TODO: Implement RxNorm API resolve.

        Args:
            external_id: RxCUI identifier.

        Returns:
            Medication details or None.

        Raises:
            NotImplementedError: This provider is not yet implemented.

        """
        msg = (
            "RxNorm provider is not yet implemented. Use the 'manual' provider for now."
        )
        raise NotImplementedError(msg)
