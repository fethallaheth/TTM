"""Chart generation for the model."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from rwa_model.config import ModelConfig
from rwa_model.engine import ModelRun


def save_all_charts(
    config: ModelConfig,
    model_run: ModelRun,
    monte_carlo_df: pd.DataFrame,
    sensitivity_df: pd.DataFrame,
    charts_dir: Path,
    wacc_axis: str = "book_wacc_change",
) -> None:
    """Save all model charts as PNG and PDF."""
    charts_dir.mkdir(parents=True, exist_ok=True)
    settings = config.chart_settings
    _set_style()
    collateral_efficiency_frontier(config, charts_dir, settings)
    cost_of_debt_bridge(model_run.baseline, charts_dir, settings)
    break_even_technology_risk_premium(config, model_run.baseline, charts_dir, settings)
    capital_liberated_matrix(model_run.adoption_stress_grid, charts_dir, settings)
    book_vs_market_wacc_change(model_run.book_market_wacc, charts_dir, settings)
    roe_reinvestment_sensitivity(model_run.reinvestment_sensitivity, charts_dir, settings)
    liquidity_funding_risk_quadrant(monte_carlo_df, charts_dir, settings, wacc_axis=wacc_axis)
    histogram(
        monte_carlo_df,
        "capital_liberated",
        "Monte Carlo Distribution of Capital Liberated",
        "Capital liberated (USD billions)",
        "08_mc_capital_liberated_distribution",
        charts_dir,
        settings,
    )
    histogram(
        monte_carlo_df,
        "book_wacc_change",
        "Monte Carlo Distribution of Book WACC Change",
        "Book WACC change (percentage points)",
        "09_mc_book_wacc_change_distribution",
        charts_dir,
        settings,
        percentage_points=True,
    )
    histogram(
        monte_carlo_df,
        "market_wacc_change",
        "Monte Carlo Distribution of Market WACC Change",
        "Market WACC change (percentage points)",
        "10_mc_market_wacc_change_distribution",
        charts_dir,
        settings,
        percentage_points=True,
    )
    for output in ["capital_liberated", "book_wacc_change", "market_wacc_change", "roe_change"]:
        sensitivity_tornado(sensitivity_df, output, charts_dir, settings)
    net_financial_capacity_waterfall(model_run.risk_adjusted_capacity, charts_dir, settings)


def collateral_efficiency_frontier(config: ModelConfig, charts_dir: Path, settings: dict) -> None:
    x = np.linspace(0, max(config.adoption_scenarios.values()), 60)
    fig, ax = plt.subplots(figsize=(8, 5))
    for stress_name, stress in config.stress_scenarios.items():
        y = (1.0 - x) * (1.0 - stress["legacy_haircut"]) + x * (1.0 - stress["tokenized_haircut"])
        ax.plot(x * 100.0, y * 100.0, label=stress_name, linewidth=2)
    ax.set_title("Collateral Efficiency Frontier")
    ax.set_xlabel("Tokenization adoption (%)")
    ax.set_ylabel("Portfolio collateral efficiency (%)")
    ax.legend(frameon=False, fontsize=8)
    ax.grid(True, alpha=0.25)
    _save(fig, charts_dir, "01_collateral_efficiency_frontier", settings)


def cost_of_debt_bridge(baseline: dict, charts_dir: Path, settings: dict) -> None:
    labels = [
        "Legacy",
        "Efficiency spread",
        "Technology risk",
        "Floor adjustment",
        "Final",
    ]
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
    heights = [values[0], values[1], values[2], values[3], values[4]]
    colors = ["#3B6EA8", "#4C9F70", "#C75C5C", "#8E8E8E", "#234E70"]

    fig, ax = plt.subplots(figsize=(8, 5))
    for idx, (start, height) in enumerate(zip(starts, heights)):
        ax.bar(idx, height * 100.0, bottom=start * 100.0, color=colors[idx], width=0.62)
        end = start + height
        ax.text(idx, end * 100.0, f"{end * 100:.2f}%", ha="center", va="bottom", fontsize=8)
    ax.axhline(0, color="#444444", linewidth=0.8)
    ax.set_xticks(range(len(labels)), labels)
    ax.set_ylabel("Cost of debt (%)")
    ax.set_title("Cost of Debt Bridge")
    _save(fig, charts_dir, "02_cost_of_debt_bridge", settings)


def break_even_technology_risk_premium(
    config: ModelConfig,
    baseline: dict,
    charts_dir: Path,
    settings: dict,
) -> None:
    market = config.market_inputs
    spread = baseline["collateral_efficiency_spread"]
    x = np.linspace(0, max(0.012, spread * 2.0), 100)
    raw = market["legacy_cost_of_debt"] - spread + x
    final = np.maximum(raw, market["debt_cost_floor"]) if market["debt_cost_floor_enabled"] else raw
    floor_stops = max(0.0, market["debt_cost_floor"] - market["legacy_cost_of_debt"] + spread)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(x * 100, raw * 100, label="Raw tokenized cost", linewidth=2)
    ax.plot(x * 100, final * 100, label="Final tokenized cost", linewidth=2)
    ax.axhline(market["legacy_cost_of_debt"] * 100, color="#444444", linestyle="--", label="Legacy cost")
    ax.axhline(market["debt_cost_floor"] * 100, color="#8E8E8E", linestyle=":", label="Risk-free floor")
    ax.axvline(spread * 100, color="#C75C5C", linewidth=1.5, label="Break-even risk premium")
    ax.axvline(floor_stops * 100, color="#4C9F70", linewidth=1.2, linestyle="--", label="Floor stops binding")
    ax.set_xlabel("Technology/legal/custody risk premium (%)")
    ax.set_ylabel("Cost of debt (%)")
    ax.set_title("Break-Even Technology Risk Premium")
    ax.legend(frameon=False, fontsize=8)
    ax.grid(True, alpha=0.25)
    _save(fig, charts_dir, "03_break_even_risk_premium", settings)


def capital_liberated_matrix(grid_df: pd.DataFrame, charts_dir: Path, settings: dict) -> None:
    matrix = grid_df.pivot(index="stress_scenario", columns="adoption_scenario", values="capital_liberated")
    fig, ax = plt.subplots(figsize=(8, 5))
    im = ax.imshow(matrix.values, cmap="Blues")
    ax.set_xticks(range(len(matrix.columns)), matrix.columns)
    ax.set_yticks(range(len(matrix.index)), matrix.index)
    for row in range(matrix.shape[0]):
        for col in range(matrix.shape[1]):
            ax.text(col, row, f"{matrix.iloc[row, col]:.2f}", ha="center", va="center", fontsize=8)
    ax.set_title("Capital Liberated Adoption-Stress Matrix")
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label("USD billions")
    _save(fig, charts_dir, "04_capital_liberated_matrix", settings)


def book_vs_market_wacc_change(wacc_df: pd.DataFrame, charts_dir: Path, settings: dict) -> None:
    fig, ax = plt.subplots(figsize=(7, 5))
    values = wacc_df["wacc_change"] * 100.0
    ax.bar(wacc_df["wacc_basis"], values, color=["#3B6EA8", "#4C9F70"], width=0.55)
    for idx, value in enumerate(values):
        ax.text(idx, value, f"{value:.3f} pp", ha="center", va="bottom" if value >= 0 else "top", fontsize=8)
    ax.axhline(0, color="#444444", linewidth=0.8)
    ax.set_ylabel("WACC change (percentage points)")
    ax.set_title("Book vs Market WACC Change")
    _save(fig, charts_dir, "05_book_vs_market_wacc_change", settings)


def roe_reinvestment_sensitivity(df: pd.DataFrame, charts_dir: Path, settings: dict) -> None:
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(df["reinvestment_return"] * 100, df["roe_change"] * 100, marker="o", linewidth=2)
    for _, row in df.iterrows():
        ax.text(row["reinvestment_return"] * 100, row["roe_change"] * 100, f"{row['roe_change'] * 100:.2f}", fontsize=8)
    ax.axhline(0, color="#444444", linewidth=0.8)
    ax.set_xlabel("Reinvestment return (%)")
    ax.set_ylabel("ROE change (percentage points)")
    ax.set_title("ROE Reinvestment Sensitivity")
    ax.grid(True, alpha=0.25)
    _save(fig, charts_dir, "06_roe_reinvestment_sensitivity", settings)


def liquidity_funding_risk_quadrant(
    df: pd.DataFrame,
    charts_dir: Path,
    settings: dict,
    wacc_axis: str = "book_wacc_change",
) -> None:
    fig, ax = plt.subplots(figsize=(8, 5))
    y_label = "Book WACC change" if wacc_axis == "book_wacc_change" else "Market WACC change"
    ax.scatter(df["capital_liberated"], df[wacc_axis] * 100, s=10, alpha=0.35, color="#3B6EA8")
    ax.axhline(0, color="#444444", linewidth=0.8)
    ax.axvline(0, color="#444444", linewidth=0.8)
    ax.set_xlabel("Capital liberated (USD billions)")
    ax.set_ylabel(f"{y_label} (percentage points)")
    ax.set_title("Liquidity-Funding Risk Quadrant")
    ax.grid(True, alpha=0.2)
    _save(fig, charts_dir, "07_liquidity_funding_risk_quadrant", settings)


def histogram(
    df: pd.DataFrame,
    column: str,
    title: str,
    xlabel: str,
    filename: str,
    charts_dir: Path,
    settings: dict,
    percentage_points: bool = False,
) -> None:
    values = df[column] * 100.0 if percentage_points else df[column]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(values, bins=40, color="#3B6EA8", alpha=0.85)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Simulation count")
    ax.grid(True, axis="y", alpha=0.2)
    _save(fig, charts_dir, filename, settings)


def sensitivity_tornado(df: pd.DataFrame, output: str, charts_dir: Path, settings: dict) -> None:
    subset = df[df["output"] == output].sort_values("absolute_impact")
    values = subset["absolute_impact"].copy()
    xlabel = "Absolute impact"
    if output in {"book_wacc_change", "market_wacc_change", "roe_change"}:
        values = values * 100.0
        xlabel = "Absolute impact (percentage points)"

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(subset["variable"], values, color="#3B6EA8")
    ax.set_xlabel(xlabel)
    ax.set_title(f"Sensitivity Tornado: {output}")
    ax.grid(True, axis="x", alpha=0.2)
    _save(fig, charts_dir, f"11_sensitivity_tornado_{output}", settings)


def net_financial_capacity_waterfall(df: pd.DataFrame, charts_dir: Path, settings: dict) -> None:
    components = df[df["component"] != "Net financial capacity"].copy()
    total = float(df.loc[df["component"] == "Net financial capacity", "value"].iloc[0])
    labels = list(components["component"]) + ["Net financial capacity"]
    values = list(components["value"]) + [total]
    starts = [0.0]
    running = 0.0
    for value in components["value"].iloc[:-1]:
        running += float(value)
        starts.append(running)
    starts.append(0.0)

    fig, ax = plt.subplots(figsize=(9, 5))
    colors = ["#4C9F70" if value >= 0 else "#C75C5C" for value in values[:-1]] + ["#234E70"]
    for idx, value in enumerate(values):
        ax.bar(idx, value, bottom=starts[idx], color=colors[idx], width=0.6)
        end = starts[idx] + value
        ax.text(idx, end, f"{end:.2f}", ha="center", va="bottom" if end >= 0 else "top", fontsize=8)
    ax.axhline(0, color="#444444", linewidth=0.8)
    ax.set_xticks(range(len(labels)), labels, rotation=25, ha="right")
    ax.set_ylabel("USD billions")
    ax.set_title("Net Financial Capacity Waterfall")
    _save(fig, charts_dir, "12_net_financial_capacity_waterfall", settings)


def _set_style() -> None:
    plt.rcParams.update(
        {
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "axes.spines.top": False,
            "axes.spines.right": False,
            "font.size": 10,
            "axes.titleweight": "bold",
        }
    )


def _save(fig: plt.Figure, charts_dir: Path, filename: str, settings: dict) -> None:
    fig.tight_layout()
    dpi = int(settings.get("dpi", 300))
    if settings.get("save_png", True):
        fig.savefig(charts_dir / f"{filename}.png", dpi=dpi)
    if settings.get("save_pdf", True):
        fig.savefig(charts_dir / f"{filename}.pdf")
    plt.close(fig)
