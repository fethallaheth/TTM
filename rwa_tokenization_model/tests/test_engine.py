from __future__ import annotations

import pytest

from rwa_model.config import load_config
from rwa_model.engine import run_model


def test_baseline_engine_outputs_expected_core_values() -> None:
    config = load_config("params.yaml")
    run = run_model(config)
    baseline = run.baseline
    assert baseline["tokenized_share"] == pytest.approx(0.25)
    assert baseline["tokenized_collateral_pool"] == pytest.approx(96.486 * 0.25)
    assert baseline["additional_usable_collateral"] == pytest.approx(96.486 * 0.25 * (0.05 - 0.03))
    assert baseline["capital_liberated"] == pytest.approx(96.486 * 0.25 * (0.20 - 0.14))
    assert baseline["book_wacc_change"] <= 0
    assert abs(baseline["market_wacc_change"]) < abs(baseline["book_wacc_change"])
