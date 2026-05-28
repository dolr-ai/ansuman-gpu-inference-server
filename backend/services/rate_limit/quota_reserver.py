"""Quota reservation service."""

from dataclasses import dataclass


@dataclass(frozen=True)
class TokenReservation:
    """Placeholder for Phase 8 token-per-minute reservation state."""

    api_key_id: str
    estimated_tokens: int


class QuotaReserver:
    """Phase 7 placeholder for TPM reservations implemented in Phase 8."""

    async def reserve_tpm_placeholder(
        self, *, api_key_id: str, estimated_tokens: int = 0
    ) -> TokenReservation:
        return TokenReservation(api_key_id=api_key_id, estimated_tokens=estimated_tokens)
