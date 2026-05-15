"""Table builders and exporters."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from rwa_model.config import ModelConfig
from rwa_model.engine import ModelRun
from rwa_model.monte_carlo import monte_carlo_summary
from rwa_model.utils import flatten_dict


BASELINE_COLUMNS = [
    "total_marketable_securities",
    "total_liquid_assets",
    "tokenized_share",
    "tokenized_collateral_pool",
    "additional_usable_collateral",
    "capital_liberated",
    "legacy_cost_of_debt",
    "raw_tokenized_cost_of_debt",
    "final_tokenized_cost_of_debt",
    "floor_adjustment",
    "book_legacy_wacc",
    "book_tokenized_wacc",
    "book_wacc_change",
    "market_legacy_wacc",
    "market_tokenized_wacc",
    "market_wacc_change",
    "legacy_roe",
    "adjusted_roe",
    "roe_change",
]

ADOPTION_COLUMNS = [
    "scenario",
    "tokenized_share",
    "tokenized_collateral_pool",
    "additional_usable_collateral",
    "capital_liberated",
    "mixed_collateral_efficiency",
    "book_wacc_change",
    "market_wacc_change",
    "roe_change",
]

STRESS_COLUMNS = [
    "scenario",
    "legacy_haircut",
    "tokenized_haircut",
    "legacy_buffer_ratio",
    "tokenized_buffer_ratio",
    "additional_usable_collateral",
    "capital_liberated",
    "final_tokenized_cost_of_debt",
    "book_wacc_change",
    "market_wacc_change",
    "roe_change",
]

GRID_COLUMNS = [
    "adoption_scenario",
    "stress_scenario",
    "tokenized_share",
    "capital_liberated",
    "mixed_collateral_efficiency",
    "book_wacc_change",
    "market_wacc_change",
    "roe_change",
]


def build_tables(
    config: ModelConfig,
    model_run: ModelRun,
    monte_carlo_df: pd.DataFrame | None = None,
    sensitivity_df: pd.DataFrame | None = None,
) -> dict[str, pd.DataFrame]:
    """Build all export tables."""
    baseline = pd.DataFrame([{key: model_run.baseline[key] for key in BASELINE_COLUMNS}])
    mc_summary = (
        monte_carlo_summary(monte_carlo_df, config.market_inputs["legacy_cost_of_debt"])
        if monte_carlo_df is not None and not monte_carlo_df.empty
        else pd.DataFrame()
    )
    parameters = pd.DataFrame(
        [{"parameter": key, "value": value} for key, value in flatten_dict(config.raw).items()]
    )

    return {
        "baseline_summary": baseline,
        "adoption_scenarios": model_run.adoption_scenarios[ADOPTION_COLUMNS],
        "stress_scenarios": model_run.stress_scenarios[STRESS_COLUMNS],
        "adoption_stress_grid": model_run.adoption_stress_grid[GRID_COLUMNS],
        "book_market_wacc": model_run.book_market_wacc,
        "reinvestment_sensitivity": model_run.reinvestment_sensitivity[
            ["reinvestment_return", "adjusted_roe", "roe_change", "additional_income"]
        ],
        "monte_carlo_summary": mc_summary,
        "sensitivity_summary": sensitivity_df if sensitivity_df is not None else pd.DataFrame(),
        "parameters_used": parameters,
        "risk_adjusted_capacity": model_run.risk_adjusted_capacity,
    }


def export_tables(tables: dict[str, pd.DataFrame], tables_dir: Path, reports_dir: Path) -> None:
    """Export CSV tables and the Excel workbook."""
    tables_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    for name, frame in tables.items():
        frame.to_csv(tables_dir / f"{name}.csv", index=False)

    workbook = reports_dir / "model_results.xlsx"
    with pd.ExcelWriter(workbook, engine="openpyxl") as writer:
        _write_sheet(writer, tables["baseline_summary"], "Baseline Summary")
        _write_sheet(writer, tables["adoption_scenarios"], "Adoption Scenarios")
        _write_sheet(writer, tables["stress_scenarios"], "Stress Scenarios")
        _write_sheet(writer, tables["adoption_stress_grid"], "Adoption Stress Grid")
        _write_sheet(writer, tables["book_market_wacc"], "Book Market WACC")
        _write_sheet(writer, tables["reinvestment_sensitivity"], "Reinvestment Sensitivity")
        _write_sheet(writer, tables["monte_carlo_summary"], "Monte Carlo Summary")
        _write_sheet(writer, tables["sensitivity_summary"], "Sensitivity Summary")
        _write_sheet(writer, tables["parameters_used"], "Parameters Used")


def validate_export_consistency(tables_dir: Path) -> None:
    """Fail if exported parameter and baseline tables contradict each other."""
    baseline_path = tables_dir / "baseline_summary.csv"
    parameters_path = tables_dir / "parameters_used.csv"
    if not baseline_path.exists() or not parameters_path.exists():
        raise FileNotFoundError("baseline_summary.csv and parameters_used.csv are required for consistency checks")

    baseline = pd.read_csv(baseline_path)
    parameters = pd.read_csv(parameters_path)
    params = dict(zip(parameters["parameter"], parameters["value"]))
    floor_enabled = _parse_bool(params.get("market_inputs.debt_cost_floor_enabled"))
    floor_adjustment = float(baseline.loc[0, "floor_adjustment"])
    raw_cost = float(baseline.loc[0, "raw_tokenized_cost_of_debt"])
    final_cost = float(baseline.loc[0, "final_tokenized_cost_of_debt"])

    if floor_enabled is False and abs(floor_adjustment) > 1e-12:
        raise ValueError(
            "Output inconsistency: debt_cost_floor_enabled is false but baseline_summary.csv "
            f"shows floor_adjustment={floor_adjustment}"
        )
    if floor_enabled is False and abs(final_cost - raw_cost) > 1e-12:
        raise ValueError(
            "Output inconsistency: debt_cost_floor_enabled is false but final_tokenized_cost_of_debt "
            "does not equal raw_tokenized_cost_of_debt"
        )


def _write_sheet(writer: Any, frame: pd.DataFrame, sheet_name: str) -> None:
    frame.to_excel(writer, sheet_name=sheet_name, index=False)


def _parse_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized == "true":
            return True
        if normalized == "false":
            return False
    return None
