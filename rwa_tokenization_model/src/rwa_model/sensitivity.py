"""One-way sensitivity analysis."""

from __future__ import annotations

from copy import deepcopy

import pandas as pd

from rwa_model.config import ModelConfig
from rwa_model.engine import LIQUIDITY_MARKETABLE, run_single_scenario


OUTPUTS = [
    "capital_liberated",
    "additional_usable_collateral",
    "book_wacc_change",
    "market_wacc_change",
    "roe_change",
]


def run_sensitivity(
    config: ModelConfig,
    liquidity_base_mode: str = LIQUIDITY_MARKETABLE,
) -> pd.DataFrame:
    """Run low/high one-way sensitivity tests for major model variables."""
    baseline_share = config.adoption_scenarios[config.baseline["adoption_scenario"]]
    stress_name = config.baseline["stress_scenario"]
    baseline_stress = dict(config.stress_scenarios[stress_name])
    ranges = _sensitivity_ranges(config, baseline_share, baseline_stress)
    rows = []

    for variable, low_value, high_value in ranges:
        low_result = _run_variable_case(
            config,
            variable,
            low_value,
            baseline_share,
            stress_name,
            baseline_stress,
            liquidity_base_mode,
        )
        high_result = _run_variable_case(
            config,
            variable,
            high_value,
            baseline_share,
            stress_name,
            baseline_stress,
            liquidity_base_mode,
        )
        for output in OUTPUTS:
            output_low = low_result[output]
            output_high = high_result[output]
            rows.append(
                {
                    "variable": variable,
                    "low_value": low_value,
                    "high_value": high_value,
                    "output": output,
                    "output_low": output_low,
                    "output_high": output_high,
                    "absolute_impact": abs(output_high - output_low),
                    "direction": "positive" if output_high >= output_low else "negative",
                }
            )
    return pd.DataFrame(rows)


def _run_variable_case(
    config: ModelConfig,
    variable: str,
    value: float,
    baseline_share: float,
    stress_name: str,
    baseline_stress: dict[str, float],
    liquidity_base_mode: str,
) -> dict[str, float]:
    tokenized_share = baseline_share
    stress = dict(baseline_stress)
    reinvestment_return = config.reinvestment["base_reinvestment_return"]
    run_config = config

    if variable == "tokenized_share":
        tokenized_share = value
    elif variable == "reinvestment_return":
        reinvestment_return = value
    elif variable == "market_cap":
        data = deepcopy(config.raw)
        data["company_data"]["market_cap"] = value
        run_config = ModelConfig.from_dict(data, config.source_path)
    else:
        stress[variable] = value

    return run_single_scenario(
        run_config,
        tokenized_share,
        stress_name,
        liquidity_base_mode=liquidity_base_mode,
        reinvestment_return=reinvestment_return,
        stress_override=stress,
    )


def _sensitivity_ranges(
    config: ModelConfig,
    baseline_share: float,
    baseline_stress: dict[str, float],
) -> list[tuple[str, float, float]]:
    mc = config.monte_carlo["distributions"]
    haircut_discount = mc["tokenized_haircut_discount"]
    buffer_discount = mc["tokenized_buffer_ratio_discount"]
    market_cap = config.company_data["market_cap"]
    reinvest_values = list(config.reinvestment["sensitivity_values"])
    return [
        ("tokenized_share", min(config.adoption_scenarios.values()), max(config.adoption_scenarios.values())),
        (
            "tokenized_haircut",
            max(0.0, baseline_stress["legacy_haircut"] - float(haircut_discount["high"])),
            max(0.0, baseline_stress["legacy_haircut"] - float(haircut_discount["low"])),
        ),
        (
            "tokenized_buffer_ratio",
            max(0.0, baseline_stress["legacy_buffer_ratio"] - float(buffer_discount["high"])),
            max(0.0, baseline_stress["legacy_buffer_ratio"] - float(buffer_discount["low"])),
        ),
        (
            "collateral_efficiency_spread",
            float(mc["collateral_efficiency_spread"]["low"]),
            float(mc["collateral_efficiency_spread"]["high"]),
        ),
        (
            "technology_risk_premium",
            float(mc["technology_risk_premium"]["low"]),
            float(mc["technology_risk_premium"]["high"]),
        ),
        ("reinvestment_return", min(reinvest_values), max(reinvest_values)),
        ("market_cap", market_cap * 0.75, market_cap * 1.25),
    ]
