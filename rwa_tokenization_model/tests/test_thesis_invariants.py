from __future__ import annotations

import pandas as pd
import pytest

from rwa_model.config import load_config
from rwa_model.engine import run_model
from rwa_model.monte_carlo import run_monte_carlo


def test_base_tokenized_haircut_not_greater_than_legacy() -> None:
    config = load_config("params.yaml")
    stress = config.stress_scenarios[config.baseline["stress_scenario"]]
    assert stress["tokenized_haircut"] <= stress["legacy_haircut"]


def test_base_tokenized_buffer_not_greater_than_legacy() -> None:
    config = load_config("params.yaml")
    stress = config.stress_scenarios[config.baseline["stress_scenario"]]
    assert stress["tokenized_buffer_ratio"] <= stress["legacy_buffer_ratio"]


def test_market_cap_affects_wacc_but_not_capital_liberated() -> None:
    config = load_config("params.yaml")
    low_market_cap = config.with_overrides(market_cap=2200.0)
    high_market_cap = config.with_overrides(market_cap=4400.0)

    low_run = run_model(low_market_cap).baseline
    high_run = run_model(high_market_cap).baseline

    assert low_run["capital_liberated"] == pytest.approx(high_run["capital_liberated"])
    assert low_run["market_wacc_change"] != pytest.approx(high_run["market_wacc_change"])


def test_roe_uses_book_equity_only() -> None:
    config = load_config("params.yaml")
    baseline = run_model(config).baseline

    book_roe = config.company_data["net_income"] / config.company_data["shareholders_equity"]
    market_earnings_yield = config.company_data["net_income"] / config.company_data["market_cap"]

    assert baseline["legacy_roe"] == pytest.approx(book_roe)
    assert baseline["legacy_roe"] != pytest.approx(market_earnings_yield)


def test_changing_adoption_changes_tokenized_pool_and_capital_liberated() -> None:
    config = load_config("params.yaml")
    results = run_model(config).adoption_scenarios.set_index("scenario")

    conservative = results.loc["Conservative"]
    aggressive = results.loc["Aggressive"]

    assert aggressive["tokenized_collateral_pool"] > conservative["tokenized_collateral_pool"]
    assert aggressive["capital_liberated"] > conservative["capital_liberated"]


def test_monte_carlo_same_seed_is_reproducible() -> None:
    config = load_config("params.yaml")
    first = run_monte_carlo(config, n=50, seed=123)
    second = run_monte_carlo(config, n=50, seed=123)
    pd.testing.assert_frame_equal(first, second)
