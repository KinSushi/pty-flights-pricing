"""Pricing-signal business rules for the PTY flight pipeline.

This module is intentionally small and testable. It allows the public portfolio
repo to prove business-rule isolation instead of keeping every rule inside one
large operational script.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class DemandTier(StrEnum):
    """Demand signal used by downstream calendar/email outputs."""

    NORMAL = "NORMAL"
    MODERATE = "MODERATE"
    HIGH = "HIGH"


@dataclass(frozen=True)
class PricingSignal:
    """Computed demand signal from flight-arrival volume."""

    total_arrivals: int
    tier: DemandTier
    recommended_action: str


def compute_demand_tier(total_arrivals: int) -> DemandTier:
    """Compute a demand tier from the total number of arrivals.

    Thresholds mirror the operational README:
    - HIGH: 150+ arrivals
    - MODERATE: 80-149 arrivals
    - NORMAL: below 80 arrivals
    """

    if total_arrivals < 0:
        raise ValueError("total_arrivals must be non-negative")
    if total_arrivals >= 150:
        return DemandTier.HIGH
    if total_arrivals >= 80:
        return DemandTier.MODERATE
    return DemandTier.NORMAL


def build_pricing_signal(total_arrivals: int) -> PricingSignal:
    """Return a recruiter-readable, testable pricing signal object."""

    tier = compute_demand_tier(total_arrivals)
    action_by_tier = {
        DemandTier.HIGH: "Review pricing aggressively and check minimum-stay constraints.",
        DemandTier.MODERATE: "Review pricing and monitor booking pace.",
        DemandTier.NORMAL: "Keep baseline pricing and continue monitoring.",
    }
    return PricingSignal(
        total_arrivals=total_arrivals,
        tier=tier,
        recommended_action=action_by_tier[tier],
    )
