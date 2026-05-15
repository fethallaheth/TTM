"""Curated thesis-ready exports.

This module intentionally sits beside the full model exports instead of replacing
them. It produces a compact Chapter 3 folder from existing model outputs.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd

from rwa_model.config import ModelConfig
from rwa_model.engine import ModelRun
from rwa_model.monte_carlo import monte_carlo_summary


NAVY = "#17324D"
BLUE = "#3B6EA8"
LIGHT_BLUE = "#8FB3D9"
GRAY = "#D6DCE2"
TEXT_GRAY = "#495057"


def export_thesis_ready_outputs(
    config: ModelConfig,
    model_run: ModelRun,
    monte_carlo_df: pd.DataFrame,
    sensitivity_df: pd.DataFrame,
    output_dir: Path,
) -> None:
    """Export curated thesis-ready tables, charts, captions, and summary."""
    output_dir.mkdir(parents=True, exist_ok=True)
    png_dir = output_dir / "charts" / "png"
    svg_dir = output_dir / "charts" / "svg"
    png_dir.mkdir(parents=True, exist_ok=True)
    svg_dir.mkdir(parents=True, exist_ok=True)

    tables = build_thesis_tables(config, model_run, monte_carlo_df, sensitivity_df)
    for filename, frame in tables.items():
        frame.to_csv(output_dir / filename, index=False)

    _set_thesis_style()
    _chart_transmission_mechanism(png_dir, svg_dir)
    _chart_cost_of_debt_bridge(model_run.baseline, png_dir, svg_dir)
    _chart_capital_liberated_by_adoption(model_run.adoption_scenarios, png_dir, svg_dir)
    _chart_capital_liberated_under_stress(model_run.stress_scenarios, png_dir, svg_dir)
    _chart_wacc_change_under_stress(model_run.stress_scenarios, png_dir, svg_dir)
    _chart_monte_carlo_distribution(monte_carlo_df, png_dir, svg_dir)
    _chart_sensitivity_tornado(sensitivity_df, png_dir, svg_dir)
    _chart_reinvestment_sensitivity(model_run.reinvestment_sensitivity, png_dir, svg_dir)

    _write_figure_captions(output_dir / "figure_captions.md")
    _write_executive_summary(
        output_dir / "executive_summary.md",
        model_run,
        monte_carlo_df,
        sensitivity_df,
    )


def build_thesis_tables(
    config: ModelConfig,
    model_run: ModelRun,
    monte_carlo_df: pd.DataFrame,
    sensitivity_df: pd.DataFrame,
) -> dict[str, pd.DataFrame]:
    """Build curated thesis-ready tables."""
    return {
        "table_3_1_company_data.csv": _company_data_table(config),
        "table_3_2_variable_definitions.csv": _variable_definitions_table(),
        "table_3_3_scenario_assumptions.csv": _scenario_assumptions_table(config),
        "table_3_4_baseline_results.csv": _baseline_results_table(model_run),
        "table_3_5_adoption_results.csv": _adoption_results_table(model_run),
        "table_3_6_stress_results.csv": _stress_results_table(model_run),
        "table_3_7_monte_carlo_summary.csv": monte_carlo_summary(
            monte_carlo_df,
            config.market_inputs["legacy_cost_of_debt"],
        ),
        "table_3_8_sensitivity_summary.csv": sensitivity_df.copy(),
        "table_3_9_reinvestment_sensitivity.csv": model_run.reinvestment_sensitivity[
            ["reinvestment_return", "additional_income", "adjusted_roe", "roe_change"]
        ].copy(),
    }


def _company_data_table(config: ModelConfig) -> pd.DataFrame:
    labels = {
        "cash_and_equivalents": "Cash and equivalents",
        "current_marketable_securities": "Current marketable securities",
        "non_current_marketable_securities": "Non-current marketable securities",
        "total_liquid_assets": "Total liquid assets",
        "total_marketable_securities": "Total marketable securities",
        "commercial_paper": "Commercial paper",
        "current_term_debt": "Current term debt",
        "non_current_term_debt": "Non-current term debt",
        "total_debt": "Total debt",
        "net_income": "Net income",
        "shareholders_equity": "Shareholders' equity",
        "effective_tax_rate": "Effective tax rate",
        "market_cap": "Market capitalization",
    }
    return pd.DataFrame(
        [
            {
                "variable": labels.get(key, key),
                "parameter": key,
                "value": value,
                "source_type": "Apple Form 10-K" if key != "market_cap" else "Public market / valuation source",
            }
            for key, value in config.company_data.items()
        ]
    )


def _variable_definitions_table() -> pd.DataFrame:
    rows = [
        ("tokenized_share", "Share of marketable securities modeled as tokenized collateral", "Scenario assumption"),
        ("tokenized_collateral_pool", "Marketable securities multiplied by tokenized share", "Simulation input"),
        ("additional_usable_collateral", "Mixed usable collateral less full legacy usable collateral", "Simulation result"),
        ("capital_liberated", "Reduction in modeled liquidity buffer requirement", "Simulation result"),
        ("book_wacc_change", "Tokenized book-value WACC less legacy book-value WACC", "Conditional result"),
        ("market_wacc_change", "Tokenized market-value WACC less legacy market-value WACC", "Conditional result"),
        ("roe_change", "Adjusted ROE less legacy ROE using book shareholders' equity", "Conditional result"),
    ]
    return pd.DataFrame(rows, columns=["variable", "definition", "thesis_treatment"])


def _scenario_assumptions_table(config: ModelConfig) -> pd.DataFrame:
    rows = []
    for scenario, value in config.adoption_scenarios.items():
        rows.append({"group": "Adoption", "scenario": scenario, "variable": "tokenized_share", "value": value})
    for scenario, values in config.stress_scenarios.items():
        for variable, value in values.items():
            rows.append({"group": "Stress", "scenario": scenario, "variable": variable, "value": value})
    for value in config.reinvestment["sensitivity_values"]:
        rows.append(
            {
                "group": "Reinvestment",
                "scenario": "Sensitivity",
                "variable": "reinvestment_return",
                "value": value,
            }
        )
    return pd.DataFrame(rows)


def _baseline_results_table(model_run: ModelRun) -> pd.DataFrame:
    baseline = model_run.baseline
    columns = [
        "tokenized_share",
        "tokenized_collateral_pool",
        "additional_usable_collateral",
        "capital_liberated",
        "legacy_cost_of_debt",
        "final_tokenized_cost_of_debt",
        "book_wacc_change",
        "market_wacc_change",
        "legacy_roe",
        "adjusted_roe",
        "roe_change",
    ]
    return pd.DataFrame([{column: baseline[column] for column in columns}])


def _adoption_results_table(model_run: ModelRun) -> pd.DataFrame:
    columns = [
        "scenario",
        "tokenized_share",
        "tokenized_collateral_pool",
        "additional_usable_collateral",
        "capital_liberated",
        "book_wacc_change",
        "market_wacc_change",
        "roe_change",
    ]
    return model_run.adoption_scenarios[columns].copy()


def _stress_results_table(model_run: ModelRun) -> pd.DataFrame:
    columns = [
        "scenario",
        "legacy_haircut",
        "tokenized_haircut",
        "legacy_buffer_ratio",
        "tokenized_buffer_ratio",
        "additional_usable_collateral",
        "capital_liberated",
        "book_wacc_change",
        "market_wacc_change",
        "roe_change",
    ]
    return model_run.stress_scenarios[columns].copy()


def _chart_transmission_mechanism(png_dir: Path, svg_dir: Path) -> None:
    labels = [
        "Marketable\nsecurities",
        "Tokenized\ncollateral pool",
        "Haircut\nadjustment",
        "Usable\ncollateral",
        "Liquidity buffer\nreduction",
        "Capital\nliberated",
        "WACC and ROE\nchannels",
    ]
    fig, ax = plt.subplots(figsize=(11, 3.2))
    ax.axis("off")
    xs = [i / (len(labels) - 1) for i in range(len(labels))]
    for idx, (x, label) in enumerate(zip(xs, labels)):
        ax.text(
            x,
            0.55,
            label,
            ha="center",
            va="center",
            color=NAVY,
            fontsize=9,
            bbox={"boxstyle": "round,pad=0.35", "facecolor": "white", "edgecolor": LIGHT_BLUE, "linewidth": 1.2},
            transform=ax.transAxes,
        )
        if idx < len(labels) - 1:
            ax.annotate(
                "",
                xy=(xs[idx + 1] - 0.055, 0.55),
                xytext=(x + 0.055, 0.55),
                arrowprops={"arrowstyle": "->", "color": BLUE, "lw": 1.4},
                xycoords=ax.transAxes,
                textcoords=ax.transAxes,
            )
    ax.set_title("Transmission Mechanism", color=NAVY)
    _save_dual(fig, "transmission_mechanism", png_dir, svg_dir)


def _chart_cost_of_debt_bridge(baseline: dict, png_dir: Path, svg_dir: Path) -> None:
    labels = ["Legacy", "Efficiency\nspread", "Technology\nrisk", "Floor\nadjustment", "Final"]
    values = [
        baseline["legacy_cost_of_debt"],
        -baseline["collateral_efficiency_spread"],
        baseline["technology_risk_premium"],
        baseline["floor_adjustment"],
        baseline["final_tokenized_cost_of_debt"],
    ]
    running = [values[0]]
    for value in values[1:4]:
        running.append(running[-1] + value)
    starts = [0, running[0], running[1], running[2], 0]

    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    colors = [BLUE, LIGHT_BLUE, "#7A869A", "#AAB4C0", NAVY]
    for idx, (start, value) in enumerate(zip(starts, values)):
        ax.bar(idx, value * 100, bottom=start * 100, color=colors[idx], width=0.58)
        end = start + value
        ax.text(idx, end * 100, f"{end * 100:.2f}%", ha="center", va="bottom", fontsize=8, color=NAVY)
    ax.axhline(0, color=TEXT_GRAY, linewidth=0.8)
    ax.set_xticks(range(len(labels)), labels)
    ax.set_ylabel("Cost of debt (%)")
    ax.set_title("Cost of Debt Bridge")
    _finish_axis(ax)
    _save_dual(fig, "cost_of_debt_bridge", png_dir, svg_dir)


def _chart_capital_liberated_by_adoption(df: pd.DataFrame, png_dir: Path, svg_dir: Path) -> None:
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.bar(df["scenario"], df["capital_liberated"], color=BLUE, width=0.55)
    _label_bars(ax, df["capital_liberated"])
    ax.set_ylabel("Capital liberated (USD billions)")
    ax.set_title("Capital Liberated by Adoption Level")
    _finish_axis(ax)
    _save_dual(fig, "capital_liberated_by_adoption", png_dir, svg_dir)


def _chart_capital_liberated_under_stress(df: pd.DataFrame, png_dir: Path, svg_dir: Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.bar(df["scenario"], df["capital_liberated"], color=BLUE, width=0.58)
    _label_bars(ax, df["capital_liberated"])
    ax.set_ylabel("Capital liberated (USD billions)")
    ax.set_title("Capital Liberated under Stress Scenarios")
    ax.tick_params(axis="x", rotation=20)
    _finish_axis(ax)
    _save_dual(fig, "capital_liberated_under_stress", png_dir, svg_dir)


def _chart_wacc_change_under_stress(df: pd.DataFrame, png_dir: Path, svg_dir: Path) -> None:
    x = range(len(df))
    width = 0.36
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    ax.bar([i - width / 2 for i in x], df["book_wacc_change"] * 100, width=width, label="Book-value", color=BLUE)
    ax.bar([i + width / 2 for i in x], df["market_wacc_change"] * 100, width=width, label="Market-value", color=LIGHT_BLUE)
    ax.axhline(0, color=TEXT_GRAY, linewidth=0.8)
    ax.set_xticks(list(x), df["scenario"], rotation=20, ha="right")
    ax.set_ylabel("WACC change (percentage points)")
    ax.set_title("WACC Change under Stress: Book vs Market")
    ax.legend(frameon=False)
    _finish_axis(ax)
    _save_dual(fig, "wacc_change_under_stress_book_vs_market", png_dir, svg_dir)


def _chart_monte_carlo_distribution(df: pd.DataFrame, png_dir: Path, svg_dir: Path) -> None:
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    ax.hist(df["capital_liberated"], bins=35, color=BLUE, alpha=0.9)
    ax.set_xlabel("Capital liberated (USD billions)")
    ax.set_ylabel("Simulation count")
    ax.set_title("Monte Carlo Distribution of Capital Liberated")
    _finish_axis(ax)
    _save_dual(fig, "monte_carlo_distribution", png_dir, svg_dir)


def _chart_sensitivity_tornado(df: pd.DataFrame, png_dir: Path, svg_dir: Path) -> None:
    subset = df[df["output"] == "capital_liberated"].sort_values("absolute_impact")
    fig, ax = plt.subplots(figsize=(7.5, 4.8))
    ax.barh(subset["variable"], subset["absolute_impact"], color=BLUE)
    ax.set_xlabel("Absolute impact on capital liberated (USD billions)")
    ax.set_title("Sensitivity Tornado: Capital Liberated")
    _finish_axis(ax)
    _save_dual(fig, "sensitivity_tornado", png_dir, svg_dir)


def _chart_reinvestment_sensitivity(df: pd.DataFrame, png_dir: Path, svg_dir: Path) -> None:
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    ax.plot(df["reinvestment_return"] * 100, df["roe_change"] * 100, marker="o", color=BLUE, linewidth=2)
    ax.axhline(0, color=TEXT_GRAY, linewidth=0.8)
    ax.set_xlabel("Reinvestment return (%)")
    ax.set_ylabel("ROE change (percentage points)")
    ax.set_title("ROE Reinvestment Sensitivity")
    _finish_axis(ax)
    _save_dual(fig, "reinvestment_sensitivity", png_dir, svg_dir)


def _write_figure_captions(path: Path) -> None:
    path.write_text(
        """# Figure Captions

Figure 3.X: Transmission Mechanism
This figure summarizes the model's counterfactual pathway from marketable securities to collateral, liquidity, WACC, and ROE effects.

Figure 3.X: Cost of Debt Bridge
This figure decomposes the transition from the legacy cost of debt to the tokenized cost of debt. The collateral efficiency spread reduces borrowing cost, while the technology risk premium offsets part of the benefit.

Figure 3.X: Capital Liberated by Adoption Level
This figure shows how capital liberated changes as the tokenized share of marketable securities increases under normal market conditions.

Figure 3.X: Capital Liberated under Stress Scenarios
This figure compares capital liberated across stress scenarios while holding adoption at the baseline level.

Figure 3.X: WACC Change under Stress Scenarios
This figure compares WACC changes under book-value and market-value capital structure weights across stress scenarios.

Figure 3.X: Monte Carlo Distribution
This figure shows the simulated distribution of capital liberated across randomized collateral, liquidity, funding-cost, and reinvestment assumptions.

Figure 3.X: Sensitivity Tornado
This figure ranks assumptions by their absolute effect on capital liberated in the one-way sensitivity analysis.

Figure 3.X: Reinvestment Sensitivity
This figure shows how adjusted ROE changes when liberated capital is redeployed at different after-tax returns.
""",
        encoding="utf-8",
    )


def _write_executive_summary(
    path: Path,
    model_run: ModelRun,
    monte_carlo_df: pd.DataFrame,
    sensitivity_df: pd.DataFrame,
) -> None:
    baseline = model_run.baseline
    adoption = model_run.adoption_scenarios
    stress = model_run.stress_scenarios
    mc_positive = (monte_carlo_df["capital_liberated"] > 0).mean()
    mc_wacc_down = (monte_carlo_df["book_wacc_change"] < 0).mean()
    top_sensitivity = (
        sensitivity_df[sensitivity_df["output"] == "capital_liberated"]
        .sort_values("absolute_impact", ascending=False)
        .iloc[0]
    )
    path.write_text(
        f"""# Executive Summary

## Baseline Result

The baseline scenario tokenizes {baseline['tokenized_share']:.0%} of marketable securities, creating a tokenized collateral pool of USD {baseline['tokenized_collateral_pool']:.3f} billion. Additional usable collateral is USD {baseline['additional_usable_collateral']:.3f} billion and capital liberated is USD {baseline['capital_liberated']:.3f} billion. Book-value WACC changes by {baseline['book_wacc_change'] * 100:.4f} percentage points, while market-value WACC changes by {baseline['market_wacc_change'] * 100:.4f} percentage points.

## Adoption Result

Across adoption scenarios, capital liberated ranges from USD {adoption['capital_liberated'].min():.3f} billion to USD {adoption['capital_liberated'].max():.3f} billion. Higher tokenization adoption increases the tokenized collateral pool and the modeled liquidity buffer reduction.

## Stress Result

Across stress scenarios, capital liberated ranges from USD {stress['capital_liberated'].min():.3f} billion to USD {stress['capital_liberated'].max():.3f} billion. Stress conditions reduce or offset funding-cost benefits, so WACC effects should be interpreted as conditional.

## Monte Carlo Summary

In the Monte Carlo simulation, capital liberated is positive in {mc_positive:.1%} of simulations. Book-value WACC declines in {mc_wacc_down:.1%} of simulations, reflecting the dependence of WACC effects on collateral efficiency spreads and technology risk premia.

## Sensitivity Summary

The largest one-way impact on capital liberated comes from `{top_sensitivity['variable']}`, with an absolute impact of {top_sensitivity['absolute_impact']:.3f}.

## Main Interpretation

The model suggests that tokenized collateral has its most robust effect through liquidity efficiency and capital liberated. WACC effects are conditional on funding-cost assumptions and capital-structure weights. ROE effects depend on whether liberated capital is productively redeployed.
""",
        encoding="utf-8",
    )


def _set_thesis_style() -> None:
    plt.rcParams.update(
        {
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "axes.edgecolor": NAVY,
            "axes.labelcolor": NAVY,
            "axes.titlecolor": NAVY,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "xtick.color": TEXT_GRAY,
            "ytick.color": TEXT_GRAY,
            "font.size": 10,
            "axes.titleweight": "bold",
        }
    )


def _finish_axis(ax: plt.Axes) -> None:
    ax.grid(True, axis="y", color=GRAY, linewidth=0.8, alpha=0.8)
    ax.set_axisbelow(True)


def _label_bars(ax: plt.Axes, values: pd.Series) -> None:
    for idx, value in enumerate(values):
        ax.text(idx, value, f"{value:.2f}", ha="center", va="bottom", fontsize=8, color=NAVY)


def _save_dual(fig: plt.Figure, filename: str, png_dir: Path, svg_dir: Path) -> None:
    fig.tight_layout()
    fig.savefig(png_dir / f"{filename}.png", dpi=300)
    fig.savefig(svg_dir / f"{filename}.svg", format="svg")
    plt.close(fig)
