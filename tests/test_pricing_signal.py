import pytest

from src.pricing_signal import DemandTier, build_pricing_signal, compute_demand_tier


@pytest.mark.parametrize(
    ("arrivals", "expected"),
    [
        (0, DemandTier.NORMAL),
        (79, DemandTier.NORMAL),
        (80, DemandTier.MODERATE),
        (149, DemandTier.MODERATE),
        (150, DemandTier.HIGH),
        (220, DemandTier.HIGH),
    ],
)
def test_compute_demand_tier(arrivals: int, expected: DemandTier) -> None:
    assert compute_demand_tier(arrivals) == expected


def test_compute_demand_tier_rejects_negative_values() -> None:
    with pytest.raises(ValueError, match="non-negative"):
        compute_demand_tier(-1)


def test_build_pricing_signal_contains_action() -> None:
    signal = build_pricing_signal(160)

    assert signal.total_arrivals == 160
    assert signal.tier == DemandTier.HIGH
    assert "Review pricing" in signal.recommended_action
