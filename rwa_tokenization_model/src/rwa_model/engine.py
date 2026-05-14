"""Model orchestration for deterministic scenarios."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd

from rwa_model import formulas
from rwa_model.config import ModelConfig


LIQUIDITY_MARKETABLE = "marketable-securities"
LIQUIDITY_TOTAL_LIQUID = "total-liquid-assets"


@dataclass(frozen=True)
class ModelRun:
    """Container for the deterministic model outputs."""

    baseline: dict[str, Any]
    adoption_scenarios: pd.DataFrame
    stress_scenarios: pd.DataFrame
    adoption_stress_grid: pd.DataFrame
    reinvestment_sensitivity: pd.DataFrame
    book_market_wacc: pd.DataFrame
    risk_adjusted_capacity: pd.DataFrame


def run_single_scenario(
    config: ModelConfig,
    tokenized_share: float,
    stress_name: str,
    liquidity_base_mode: str = LIQUIDITY_MARKETABLE,
    reinvestment_return: float | None = None,
    scenario_label: str | None = None,
    stress_override: dict[str, float] | None = None,
) -> dict[str, Any]:
    """Run one deterministic tokenization scenario."""
    company = config.company_data
    market = config.market_inputs
    stress = stress_override or config.stress_scenarios[stress_name]
    reinvestment = (
        config.reinvestment["base_reinvestment_return"]
        if reinvestment_return is None
        else reinvestment_return
    )

    total_ms = company["total_marketable_securities"]
    liquidity_base = _liquidity_base(company, liquidity_base_mode)

    tcp = formulas.tokenized_collateral_pool(total_ms, tokenized_share)
    legacy_portion, tokenized_portion = formulas.collateral_portions(total_ms, tokenized_share)
    full_legacy_usable = formulas.full_legacy_usable_collateral(total_ms, stress["legacy_haircut"])
    mixed_usable = formulas.mixed_usable_collateral(
        total_ms,
        tokenized_share,
        stress["legacy_haircut"],
        stress["tokenized_haircut"],
    )
    additional_usable = mixed_usable - full_legacy_usable
    legacy_ce = formulas.collateral_efficiency(full_legacy_usable, total_ms)
    mixed_ce = formulas.collateral_efficiency(mixed_usable, total_ms)

    legacy_buffer = formulas.legacy_liquidity_buffer(liquidity_base, stress["legacy_buffer_ratio"])
    mixed_buffer = formulas.mixed_liquidity_buffer(
        liquidity_base,
        tokenized_share,
        stress["legacy_buffer_ratio"],
        stress["tokenized_buffer_ratio"],
    )
    capital_liberated = legacy_buffer - mixed_buffer

    raw_debt_cost, final_debt_cost, floor_adjustment = formulas.tokenized_cost_of_debt(
        market["legacy_cost_of_debt"],
        stress["collateral_efficiency_spread"],
        stress["technology_risk_premium"],
        bool(market["debt_cost_floor_enabled"]),
        market["debt_cost_floor"],
    )
    capm_check = formulas.capm_cost_of_equity(
        market["risk_free_rate"],
        market["beta"],
        market["market_risk_premium"],
    )
    cost_of_equity_used = market.get("cost_of_equity", capm_check)

    book_legacy_wacc, book_debt_weight, book_equity_weight = formulas.wacc(
        company["total_debt"],
        company["shareholders_equity"],
        cost_of_equity_used,
        market["legacy_cost_of_debt"],
        company["effective_tax_rate"],
    )
    book_tokenized_wacc, _, _ = formulas.wacc(
        company["total_debt"],
        company["shareholders_equity"],
        cost_of_equity_used,
        final_debt_cost,
        company["effective_tax_rate"],
    )
    market_legacy_wacc, market_debt_weight, market_equity_weight = formulas.wacc(
        company["total_debt"],
        company["market_cap"],
        cost_of_equity_used,
        market["legacy_cost_of_debt"],
        company["effective_tax_rate"],
    )
    market_tokenized_wacc, _, _ = formulas.wacc(
        company["total_debt"],
        company["market_cap"],
        cost_of_equity_used,
        final_debt_cost,
        company["effective_tax_rate"],
    )

    legacy_roe = formulas.roe(company["net_income"], company["shareholders_equity"])
    adjusted_income = formulas.adjusted_net_income(
        company["net_income"],
        capital_liberated,
        reinvestment,
    )
    adjusted_roe = formulas.roe(adjusted_income, company["shareholders_equity"])

    capacity = config.risk_adjusted_capacity
    net_financial_capacity = (
        additional_usable
        + capital_liberated
        + capacity.get("settlement_saving", 0.0)
        - capacity.get("technology_risk_cost", 0.0)
        - capacity.get("legal_custody_risk_cost", 0.0)
    )

    return {
        "scenario": scenario_label or stress_name,
        "stress_scenario": stress_name,
        "total_marketable_securities": total_ms,
        "total_liquid_assets": company["total_liquid_assets"],
        "liquidity_base_mode": liquidity_base_mode,
        "liquidity_base": liquidity_base,
        "tokenized_share": tokenized_share,
        "tokenized_collateral_pool": tcp,
        "legacy_portion": legacy_portion,
        "tokenized_portion": tokenized_portion,
        "legacy_haircut": stress["legacy_haircut"],
        "tokenized_haircut": stress["tokenized_haircut"],
        "full_legacy_usable_collateral": full_legacy_usable,
        "mixed_usable_collateral": mixed_usable,
        "additional_usable_collateral": additional_usable,
        "legacy_collateral_efficiency": legacy_ce,
        "mixed_collateral_efficiency": mixed_ce,
        "legacy_buffer_ratio": stress["legacy_buffer_ratio"],
        "tokenized_buffer_ratio": stress["tokenized_buffer_ratio"],
        "legacy_liquidity_buffer": legacy_buffer,
        "mixed_liquidity_buffer": mixed_buffer,
        "capital_liberated": capital_liberated,
        "legacy_cost_of_debt": market["legacy_cost_of_debt"],
        "collateral_efficiency_spread": stress["collateral_efficiency_spread"],
        "technology_risk_premium": stress["technology_risk_premium"],
        "raw_tokenized_cost_of_debt": raw_debt_cost,
        "final_tokenized_cost_of_debt": final_debt_cost,
        "floor_adjustment": floor_adjustment,
        "cost_of_equity_used": cost_of_equity_used,
        "cost_of_equity_capm_check": capm_check,
        "book_debt_weight": book_debt_weight,
        "book_equity_weight": book_equity_weight,
        "book_legacy_wacc": book_legacy_wacc,
        "book_tokenized_wacc": book_tokenized_wacc,
        "book_wacc_change": book_tokenized_wacc - book_legacy_wacc,
        "market_debt_weight": market_debt_weight,
        "market_equity_weight": market_equity_weight,
        "market_legacy_wacc": market_legacy_wacc,
        "market_tokenized_wacc": market_tokenized_wacc,
        "market_wacc_change": market_tokenized_wacc - market_legacy_wacc,
        "reinvestment_return": reinvestment,
        "legacy_roe": legacy_roe,
        "additional_income": adjusted_income - company["net_income"],
        "adjusted_net_income": adjusted_income,
        "adjusted_roe": adjusted_roe,
        "roe_change": adjusted_roe - legacy_roe,
        "settlement_saving": capacity.get("settlement_saving", 0.0),
        "technology_risk_cost": capacity.get("technology_risk_cost", 0.0),
        "legal_custody_risk_cost": capacity.get("legal_custody_risk_cost", 0.0),
        "net_financial_capacity": net_financial_capacity,
    }


def run_model(config: ModelConfig, liquidity_base_mode: str = LIQUIDITY_MARKETABLE) -> ModelRun:
    """Run baseline, scenario tables, and deterministic sensitivities."""
    baseline_share = config.adoption_scenarios[config.baseline["adoption_scenario"]]
    baseline_stress = config.baseline["stress_scenario"]
    baseline = run_single_scenario(
        config,
        baseline_share,
        baseline_stress,
        liquidity_base_mode=liquidity_base_mode,
        scenario_label="Baseline",
    )

    adoption_rows = []
    for name, share in config.adoption_scenarios.items():
        row = run_single_scenario(
            config,
            share,
            baseline_stress,
            liquidity_base_mode=liquidity_base_mode,
            scenario_label=name,
        )
        adoption_rows.append(row)

    stress_rows = []
    for name in config.stress_scenarios:
        row = run_single_scenario(
            config,
            baseline_share,
            name,
            liquidity_base_mode=liquidity_base_mode,
            scenario_label=name,
        )
        stress_rows.append(row)

    grid_rows = []
    for adoption_name, share in config.adoption_scenarios.items():
        for stress_name in config.stress_scenarios:
            row = run_single_scenario(
                config,
                share,
                stress_name,
                liquidity_base_mode=liquidity_base_mode,
                scenario_label=f"{adoption_name} - {stress_name}",
            )
            row["adoption_scenario"] = adoption_name
            grid_rows.append(row)

    reinvestment_rows = []
    for value in config.reinvestment["sensitivity_values"]:
        row = dict(baseline)
        adjusted_income = formulas.adjusted_net_income(
            config.company_data["net_income"],
            baseline["capital_liberated"],
            value,
        )
        adjusted_roe = formulas.roe(adjusted_income, config.company_data["shareholders_equity"])
        row.update(
            {
                "reinvestment_return": value,
                "additional_income": adjusted_income - config.company_data["net_income"],
                "adjusted_net_income": adjusted_income,
                "adjusted_roe": adjusted_roe,
                "roe_change": adjusted_roe - baseline["legacy_roe"],
            }
        )
        reinvestment_rows.append(row)

    book_market_wacc = pd.DataFrame(
        [
            {"wacc_basis": "Book-value WACC", "wacc_change": baseline["book_wacc_change"]},
            {"wacc_basis": "Market-value WACC", "wacc_change": baseline["market_wacc_change"]},
        ]
    )
    risk_adjusted_capacity = pd.DataFrame(
        [
            {"component": "Additional usable collateral", "value": baseline["additional_usable_collateral"]},
            {"component": "Capital liberated", "value": baseline["capital_liberated"]},
            {"component": "Settlement saving", "value": baseline["settlement_saving"]},
            {"component": "Technology risk cost", "value": -baseline["technology_risk_cost"]},
            {"component": "Legal/custody risk cost", "value": -baseline["legal_custody_risk_cost"]},
            {"component": "Net financial capacity", "value": baseline["net_financial_capacity"]},
        ]
    )

    return ModelRun(
        baseline=baseline,
        adoption_scenarios=pd.DataFrame(adoption_rows),
        stress_scenarios=pd.DataFrame(stress_rows),
        adoption_stress_grid=pd.DataFrame(grid_rows),
        reinvestment_sensitivity=pd.DataFrame(reinvestment_rows),
        book_market_wacc=book_market_wacc,
        risk_adjusted_capacity=risk_adjusted_capacity,
    )


def _liquidity_base(company: dict[str, float], liquidity_base_mode: str) -> float:
    if liquidity_base_mode == LIQUIDITY_MARKETABLE:
        return company["total_marketable_securities"]
    if liquidity_base_mode == LIQUIDITY_TOTAL_LIQUID:
        return company["total_liquid_assets"]
    raise ValueError(
        f"liquidity_base_mode must be {LIQUIDITY_MARKETABLE!r} or {LIQUIDITY_TOTAL_LIQUID!r}"
    )
