"""Command-line interface."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from rwa_model.charts import save_all_charts
from rwa_model.config import load_config
from rwa_model.engine import LIQUIDITY_MARKETABLE, LIQUIDITY_TOTAL_LIQUID, run_model
from rwa_model.monte_carlo import run_monte_carlo
from rwa_model.sensitivity import run_sensitivity
from rwa_model.tables import build_tables, export_tables
from rwa_model.thesis_outputs import export_thesis_ready_outputs
from rwa_model.utils import bns, ensure_output_dirs, pct


app = typer.Typer(help="Tokenized Collateral Efficiency Model")


def _load_with_overrides(
    params: Path,
    market_cap: Optional[float],
    adoption: Optional[float],
    stress: Optional[str],
):
    config = load_config(params)
    return config.with_overrides(market_cap=market_cap, adoption=adoption, stress=stress)


@app.command()
def run(
    params: Path = typer.Option(Path("params.yaml"), "--params", help="Path to params.yaml"),
    market_cap: Optional[float] = typer.Option(None, "--market-cap", help="Override market cap"),
    adoption: Optional[float] = typer.Option(None, "--adoption", help="Override baseline adoption share"),
    stress: Optional[str] = typer.Option(None, "--stress", help="Override baseline stress scenario"),
    liquidity_base: str = typer.Option(
        LIQUIDITY_MARKETABLE,
        "--liquidity-base",
        help="marketable-securities or total-liquid-assets",
    ),
) -> None:
    """Run the full deterministic model, Monte Carlo, sensitivity, tables, and charts."""
    config = _load_with_overrides(params, market_cap, adoption, stress)
    paths = ensure_output_dirs()
    model_run = run_model(config, liquidity_base)
    mc_df = run_monte_carlo(config, liquidity_base_mode=liquidity_base)
    sensitivity_df = run_sensitivity(config, liquidity_base)
    tables = build_tables(config, model_run, mc_df, sensitivity_df)
    export_tables(tables, paths["tables"], paths["reports"])
    mc_df.to_csv(paths["tables"] / "monte_carlo_simulations.csv", index=False)
    save_all_charts(config, model_run, mc_df, sensitivity_df, paths["charts"])
    export_thesis_ready_outputs(config, model_run, mc_df, sensitivity_df, paths["outputs"] / "thesis_ready")
    _print_baseline(model_run.baseline)


@app.command()
def charts(
    params: Path = typer.Option(Path("params.yaml"), "--params", help="Path to params.yaml"),
    market_cap: Optional[float] = typer.Option(None, "--market-cap", help="Override market cap"),
    adoption: Optional[float] = typer.Option(None, "--adoption", help="Override baseline adoption share"),
    stress: Optional[str] = typer.Option(None, "--stress", help="Override baseline stress scenario"),
    liquidity_base: str = typer.Option(LIQUIDITY_MARKETABLE, "--liquidity-base"),
) -> None:
    """Generate charts only."""
    config = _load_with_overrides(params, market_cap, adoption, stress)
    paths = ensure_output_dirs()
    model_run = run_model(config, liquidity_base)
    mc_df = run_monte_carlo(config, liquidity_base_mode=liquidity_base)
    sensitivity_df = run_sensitivity(config, liquidity_base)
    save_all_charts(config, model_run, mc_df, sensitivity_df, paths["charts"])
    typer.echo(f"Charts saved to {paths['charts']}")


@app.command("monte-carlo")
def monte_carlo_command(
    params: Path = typer.Option(Path("params.yaml"), "--params", help="Path to params.yaml"),
    n: Optional[int] = typer.Option(None, "--n", help="Number of simulations"),
    seed: Optional[int] = typer.Option(None, "--seed", help="Random seed"),
    market_cap: Optional[float] = typer.Option(None, "--market-cap", help="Override market cap"),
    adoption: Optional[float] = typer.Option(None, "--adoption", help="Override baseline adoption share"),
    stress: Optional[str] = typer.Option(None, "--stress", help="Override baseline stress scenario"),
    liquidity_base: str = typer.Option(LIQUIDITY_MARKETABLE, "--liquidity-base"),
) -> None:
    """Run Monte Carlo only and export simulations plus summary."""
    config = _load_with_overrides(params, market_cap, adoption, stress)
    paths = ensure_output_dirs()
    mc_df = run_monte_carlo(config, n=n, seed=seed, liquidity_base_mode=liquidity_base)
    model_run = run_model(config, liquidity_base)
    sensitivity_df = run_sensitivity(config, liquidity_base)
    tables = build_tables(config, model_run, mc_df, sensitivity_df)
    mc_df.to_csv(paths["tables"] / "monte_carlo_simulations.csv", index=False)
    tables["monte_carlo_summary"].to_csv(paths["tables"] / "monte_carlo_summary.csv", index=False)
    typer.echo(f"Monte Carlo simulations saved to {paths['tables'] / 'monte_carlo_simulations.csv'}")


@app.command()
def sensitivity(
    params: Path = typer.Option(Path("params.yaml"), "--params", help="Path to params.yaml"),
    market_cap: Optional[float] = typer.Option(None, "--market-cap", help="Override market cap"),
    adoption: Optional[float] = typer.Option(None, "--adoption", help="Override baseline adoption share"),
    stress: Optional[str] = typer.Option(None, "--stress", help="Override baseline stress scenario"),
    liquidity_base: str = typer.Option(LIQUIDITY_MARKETABLE, "--liquidity-base"),
) -> None:
    """Run one-way sensitivity only and export the summary."""
    config = _load_with_overrides(params, market_cap, adoption, stress)
    paths = ensure_output_dirs()
    sensitivity_df = run_sensitivity(config, liquidity_base)
    sensitivity_df.to_csv(paths["tables"] / "sensitivity_summary.csv", index=False)
    typer.echo(f"Sensitivity summary saved to {paths['tables'] / 'sensitivity_summary.csv'}")


@app.command("thesis-ready")
def thesis_ready(
    params: Path = typer.Option(Path("params.yaml"), "--params", help="Path to params.yaml"),
    market_cap: Optional[float] = typer.Option(None, "--market-cap", help="Override market cap"),
    adoption: Optional[float] = typer.Option(None, "--adoption", help="Override baseline adoption share"),
    stress: Optional[str] = typer.Option(None, "--stress", help="Override baseline stress scenario"),
    liquidity_base: str = typer.Option(LIQUIDITY_MARKETABLE, "--liquidity-base"),
) -> None:
    """Generate curated thesis-ready tables, charts, captions, and summary."""
    config = _load_with_overrides(params, market_cap, adoption, stress)
    paths = ensure_output_dirs()
    model_run = run_model(config, liquidity_base)
    mc_df = run_monte_carlo(config, liquidity_base_mode=liquidity_base)
    sensitivity_df = run_sensitivity(config, liquidity_base)
    export_thesis_ready_outputs(config, model_run, mc_df, sensitivity_df, paths["outputs"] / "thesis_ready")
    typer.echo(f"Thesis-ready outputs saved to {paths['outputs'] / 'thesis_ready'}")


def _print_baseline(baseline: dict) -> None:
    typer.echo("")
    typer.echo("Baseline:")
    typer.echo(f"- tokenized pool: {bns(baseline['tokenized_collateral_pool'])}")
    typer.echo(f"- capital liberated: {bns(baseline['capital_liberated'])}")
    typer.echo(f"- additional usable collateral: {bns(baseline['additional_usable_collateral'])}")
    typer.echo(f"- book WACC change: {baseline['book_wacc_change'] * 100:.4f} percentage points")
    typer.echo(f"- market WACC change: {baseline['market_wacc_change'] * 100:.4f} percentage points")
    typer.echo(f"- ROE change: {baseline['roe_change'] * 100:.4f} percentage points")


def validate_liquidity_base(value: str) -> str:
    """Validate liquidity base option."""
    if value not in {LIQUIDITY_MARKETABLE, LIQUIDITY_TOTAL_LIQUID}:
        raise typer.BadParameter(f"Must be {LIQUIDITY_MARKETABLE} or {LIQUIDITY_TOTAL_LIQUID}")
    return value


if __name__ == "__main__":
    app()
