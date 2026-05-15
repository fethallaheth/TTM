from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from rwa_model.tables import validate_export_consistency


def test_validate_export_consistency_rejects_floor_adjustment_when_floor_disabled(tmp_path: Path) -> None:
    pd.DataFrame(
        [
            {
                "raw_tokenized_cost_of_debt": 0.0369,
                "final_tokenized_cost_of_debt": 0.0400,
                "floor_adjustment": 0.0031,
            }
        ]
    ).to_csv(tmp_path / "baseline_summary.csv", index=False)
    pd.DataFrame(
        [
            {"parameter": "market_inputs.debt_cost_floor_enabled", "value": "False"},
            {"parameter": "market_inputs.debt_cost_floor", "value": "0.0446"},
        ]
    ).to_csv(tmp_path / "parameters_used.csv", index=False)

    with pytest.raises(ValueError, match="floor_adjustment"):
        validate_export_consistency(tmp_path)


def test_validate_export_consistency_accepts_disabled_floor_with_matching_raw_and_final(tmp_path: Path) -> None:
    pd.DataFrame(
        [
            {
                "raw_tokenized_cost_of_debt": 0.0369,
                "final_tokenized_cost_of_debt": 0.0369,
                "floor_adjustment": 0.0,
            }
        ]
    ).to_csv(tmp_path / "baseline_summary.csv", index=False)
    pd.DataFrame(
        [{"parameter": "market_inputs.debt_cost_floor_enabled", "value": "False"}]
    ).to_csv(tmp_path / "parameters_used.csv", index=False)

    validate_export_consistency(tmp_path)
