"""Monte Carlo simulation."""

from __future__ import annotations

import numpy as np
import pandas as pd

from rwa_model.config import ModelConfig
from rwa_model.engine import LIQUIDITY_MARKETABLE, run_single_scenario


def run_monte_carlo(
    config: ModelConfig,
    n: int | None = None,
    seed: int | None = None,
    liquidity_base_mode: str = LIQUIDITY_MARKETABLE,
) -> pd.DataFrame:
    """Run Monte Carlo simulations from configured distributions."""
    n_sims = int(n or config.monte_carlo["n_simulations"])
    rng = np.random.default_rng(seed if seed is not None else int(config.monte_carlo["seed"]))
    distributions = config.monte_carlo["distributions"]
    baseline_stress_name = config.baseline["stress_scenario"]
    base_stress = config.stress_scenarios[baseline_stress_name]
    rows = []

    for _ in range(n_sims):
        tokenized_share = _sample(rng, distributions["tokenized_share"])
        legacy_haircut = _sample(rng, distributions["legacy_haircut"])
        haircut_discount = _sample(rng, distributions["tokenized_haircut_discount"])
        legacy_buffer_ratio = _sample(rng, distributions["legacy_buffer_ratio"])
        buffer_discount = _sample(rng, distributions["tokenized_buffer_ratio_discount"])
        spread = _sample(rng, distributions["collateral_efficiency_spread"])
        tech_premium = _sample(rng, distributions["technology_risk_premium"])
        reinvestment_return = _sample(rng, distributions["reinvestment_return"])

        tokenized_haircut = max(0.0, legacy_haircut - haircut_discount)
        tokenized_buffer_ratio = max(0.0, legacy_buffer_ratio - buffer_discount)
        stress_override = {
            **base_stress,
            "legacy_haircut": legacy_haircut,
            "tokenized_haircut": tokenized_haircut,
            "legacy_buffer_ratio": legacy_buffer_ratio,
            "tokenized_buffer_ratio": tokenized_buffer_ratio,
            "collateral_efficiency_spread": spread,
            "technology_risk_premium": tech_premium,
        }
        result = run_single_scenario(
            config,
            tokenized_share,
            baseline_stress_name,
            liquidity_base_mode=liquidity_base_mode,
            reinvestment_return=reinvestment_return,
            scenario_label="Monte Carlo",
            stress_override=stress_override,
        )
        rows.append(
            {
                "tokenized_share": tokenized_share,
                "legacy_haircut": legacy_haircut,
                "tokenized_haircut": tokenized_haircut,
                "legacy_buffer_ratio": legacy_buffer_ratio,
                "tokenized_buffer_ratio": tokenized_buffer_ratio,
                "collateral_efficiency_spread": spread,
                "technology_risk_premium": tech_premium,
                "reinvestment_return": reinvestment_return,
                "capital_liberated": result["capital_liberated"],
                "additional_usable_collateral": result["additional_usable_collateral"],
                "final_tokenized_cost_of_debt": result["final_tokenized_cost_of_debt"],
                "book_wacc_change": result["book_wacc_change"],
                "market_wacc_change": result["market_wacc_change"],
                "adjusted_roe": result["adjusted_roe"],
                "roe_change": result["roe_change"],
            }
        )

    return pd.DataFrame(rows)


def monte_carlo_summary(df: pd.DataFrame, legacy_cost_of_debt: float) -> pd.DataFrame:
    """Summarize Monte Carlo outputs and event probabilities."""
    outputs = [
        "capital_liberated",
        "additional_usable_collateral",
        "final_tokenized_cost_of_debt",
        "book_wacc_change",
        "market_wacc_change",
        "adjusted_roe",
        "roe_change",
    ]
    rows = []
    for column in outputs:
        series = df[column]
        rows.append(
            {
                "metric": column,
                "mean": series.mean(),
                "median": series.median(),
                "std": series.std(),
                "min": series.min(),
                "max": series.max(),
                "p05": series.quantile(0.05),
                "p95": series.quantile(0.95),
            }
        )

    probabilities = {
        "probability capital_liberated > 0": (df["capital_liberated"] > 0).mean(),
        "probability additional_usable_collateral > 0": (df["additional_usable_collateral"] > 0).mean(),
        "probability book_wacc_change < 0": (df["book_wacc_change"] < 0).mean(),
        "probability market_wacc_change < 0": (df["market_wacc_change"] < 0).mean(),
        "probability roe_change > 0": (df["roe_change"] > 0).mean(),
        "probability final_tokenized_cost_of_debt > legacy_cost_of_debt": (
            df["final_tokenized_cost_of_debt"] > legacy_cost_of_debt
        ).mean(),
    }
    for metric, value in probabilities.items():
        rows.append(
            {
                "metric": metric,
                "mean": value,
                "median": np.nan,
                "std": np.nan,
                "min": np.nan,
                "max": np.nan,
                "p05": np.nan,
                "p95": np.nan,
            }
        )
    return pd.DataFrame(rows)


def _sample(rng: np.random.Generator, distribution: dict[str, float | str]) -> float:
    return float(rng.uniform(float(distribution["low"]), float(distribution["high"])))
