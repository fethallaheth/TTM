"""Path, formatting, and small helper functions."""

from __future__ import annotations

from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
CHARTS_DIR = OUTPUTS_DIR / "charts"
TABLES_DIR = OUTPUTS_DIR / "tables"
REPORTS_DIR = OUTPUTS_DIR / "reports"


def ensure_output_dirs(base_dir: Path | None = None) -> dict[str, Path]:
    """Create and return output directories."""
    root = base_dir or OUTPUTS_DIR
    paths = {
        "outputs": root,
        "charts": root / "charts",
        "tables": root / "tables",
        "reports": root / "reports",
    }
    for path in paths.values():
        path.mkdir(parents=True, exist_ok=True)
    return paths


def pct(value: float) -> str:
    """Format a decimal rate as a percentage."""
    return f"{value * 100:.2f}%"


def bns(value: float) -> str:
    """Format a USD billions value."""
    return f"${value:,.3f}bn"


def flatten_dict(data: dict[str, Any], prefix: str = "") -> dict[str, Any]:
    """Flatten a nested dictionary using dotted keys."""
    rows: dict[str, Any] = {}
    for key, value in data.items():
        full_key = f"{prefix}.{key}" if prefix else str(key)
        if isinstance(value, dict):
            rows.update(flatten_dict(value, full_key))
        else:
            rows[full_key] = value
    return rows
