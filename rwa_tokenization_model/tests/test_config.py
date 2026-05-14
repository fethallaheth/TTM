from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest
import yaml

from rwa_model.config import ModelConfig, load_config


ROOT = Path(__file__).resolve().parents[1]


def test_load_config_validates_default_params() -> None:
    config = load_config(ROOT / "params.yaml")
    assert config.company_data["total_marketable_securities"] == pytest.approx(96.486)


def test_config_rejects_percentage_style_rate() -> None:
    with (ROOT / "params.yaml").open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    bad = deepcopy(data)
    bad["market_inputs"]["risk_free_rate"] = 4.0
    with pytest.raises(ValueError, match="decimal rate"):
        ModelConfig.from_dict(bad)


def test_config_rejects_inconsistent_total_marketable_securities() -> None:
    with (ROOT / "params.yaml").open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    bad = deepcopy(data)
    bad["company_data"]["total_marketable_securities"] = 999.0
    with pytest.raises(ValueError, match="total_marketable_securities mismatch"):
        ModelConfig.from_dict(bad)
