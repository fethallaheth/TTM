from __future__ import annotations

import pytest

from rwa_model import formulas


def test_tokenized_collateral_pool() -> None:
    assert formulas.tokenized_collateral_pool(100.0, 0.25) == pytest.approx(25.0)


def test_mixed_usable_collateral() -> None:
    full_legacy = formulas.full_legacy_usable_collateral(100.0, 0.05)
    mixed = formulas.mixed_usable_collateral(100.0, 0.25, 0.05, 0.03)
    assert full_legacy == pytest.approx(95.0)
    assert mixed == pytest.approx(95.5)
    assert mixed - full_legacy == pytest.approx(0.5)


def test_wacc_formula() -> None:
    value, debt_weight, equity_weight = formulas.wacc(
        debt_value=40.0,
        equity_value=60.0,
        cost_of_equity=0.10,
        cost_of_debt=0.05,
        tax_rate=0.20,
    )
    assert debt_weight == pytest.approx(0.40)
    assert equity_weight == pytest.approx(0.60)
    assert value == pytest.approx(0.076)


def test_risk_free_floor() -> None:
    raw, final, adjustment = formulas.tokenized_cost_of_debt(
        legacy_cost_of_debt=0.0419,
        collateral_efficiency_spread=0.007,
        technology_risk_premium=0.002,
        floor_enabled=True,
        debt_cost_floor=0.0400,
    )
    assert raw == pytest.approx(0.0369)
    assert final == pytest.approx(0.0400)
    assert adjustment == pytest.approx(0.0031)


def test_roe_formula() -> None:
    assert formulas.roe(112.010, 73.733) == pytest.approx(112.010 / 73.733)
