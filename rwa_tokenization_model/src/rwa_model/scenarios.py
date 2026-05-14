"""Scenario builders."""

from __future__ import annotations

import pandas as pd

from rwa_model.config import ModelConfig


def adoption_scenarios(config: ModelConfig) -> list[tuple[str, float]]:
    """Return configured adoption scenarios."""
    return list(config.adoption_scenarios.items())


def stress_scenarios(config: ModelConfig) -> list[tuple[str, dict[str, float]]]:
    """Return configured stress scenarios."""
    return list(config.stress_scenarios.items())


def adoption_stress_grid(config: ModelConfig) -> pd.DataFrame:
    """Return every adoption scenario crossed with every stress scenario."""
    rows = []
    for adoption_name, tokenized_share in adoption_scenarios(config):
        for stress_name in config.stress_scenarios:
            rows.append(
                {
                    "adoption_scenario": adoption_name,
                    "stress_scenario": stress_name,
                    "tokenized_share": tokenized_share,
                }
            )
    return pd.DataFrame(rows)
