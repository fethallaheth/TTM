"""Configuration loading and validation."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from rwa_model import formulas


RATE_KEYS = {
    "effective_tax_rate",
    "risk_free_rate",
    "market_risk_premium",
    "cost_of_equity",
    "legacy_cost_of_debt",
    "debt_cost_floor",
    "base_reinvestment_return",
    "legacy_haircut",
    "tokenized_haircut",
    "legacy_buffer_ratio",
    "tokenized_buffer_ratio",
    "collateral_efficiency_spread",
    "technology_risk_premium",
}


@dataclass(frozen=True)
class ModelConfig:
    """Validated model configuration."""

    company_data: dict[str, float]
    market_inputs: dict[str, Any]
    reinvestment: dict[str, Any]
    adoption_scenarios: dict[str, float]
    baseline: dict[str, str]
    stress_scenarios: dict[str, dict[str, float]]
    monte_carlo: dict[str, Any]
    chart_settings: dict[str, Any]
    risk_adjusted_capacity: dict[str, float] = field(default_factory=dict)
    source_path: Path | None = None
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any], source_path: Path | None = None) -> "ModelConfig":
        """Build and validate config from a dictionary."""
        required = [
            "company_data",
            "market_inputs",
            "reinvestment",
            "adoption_scenarios",
            "baseline",
            "stress_scenarios",
            "monte_carlo",
            "chart_settings",
        ]
        missing = [key for key in required if key not in data]
        if missing:
            raise ValueError(f"Missing required config sections: {', '.join(missing)}")

        risk_capacity = data.get(
            "risk_adjusted_capacity",
            {"settlement_saving": 0.0, "technology_risk_cost": 0.0, "legal_custody_risk_cost": 0.0},
        )
        cfg = cls(
            company_data=dict(data["company_data"]),
            market_inputs=dict(data["market_inputs"]),
            reinvestment=dict(data["reinvestment"]),
            adoption_scenarios=dict(data["adoption_scenarios"]),
            baseline=dict(data["baseline"]),
            stress_scenarios={k: dict(v) for k, v in data["stress_scenarios"].items()},
            monte_carlo=dict(data["monte_carlo"]),
            chart_settings=dict(data["chart_settings"]),
            risk_adjusted_capacity=dict(risk_capacity),
            source_path=source_path,
            raw=deepcopy(data),
        )
        cfg.validate()
        return cfg

    def validate(self) -> None:
        """Validate required keys, rates, totals, and scenario relationships."""
        _require_keys(
            self.company_data,
            [
                "cash_and_equivalents",
                "current_marketable_securities",
                "non_current_marketable_securities",
                "total_liquid_assets",
                "total_marketable_securities",
                "commercial_paper",
                "current_term_debt",
                "non_current_term_debt",
                "total_debt",
                "net_income",
                "shareholders_equity",
                "effective_tax_rate",
                "market_cap",
            ],
            "company_data",
        )
        _require_keys(
            self.market_inputs,
            [
                "risk_free_rate",
                "beta",
                "market_risk_premium",
                "cost_of_equity",
                "legacy_cost_of_debt",
                "debt_cost_floor_enabled",
                "debt_cost_floor",
            ],
            "market_inputs",
        )
        _require_keys(self.reinvestment, ["base_reinvestment_return", "sensitivity_values"], "reinvestment")
        _require_keys(self.baseline, ["adoption_scenario", "stress_scenario"], "baseline")

        self._validate_numbers()
        self._validate_totals()
        self._validate_scenarios()
        self._validate_monte_carlo()

    def _validate_numbers(self) -> None:
        for section_name, section in [
            ("company_data", self.company_data),
            ("market_inputs", self.market_inputs),
            ("reinvestment", self.reinvestment),
            ("risk_adjusted_capacity", self.risk_adjusted_capacity),
        ]:
            for key, value in section.items():
                if isinstance(value, bool) or isinstance(value, list):
                    continue
                if not isinstance(value, (int, float)):
                    raise ValueError(f"{section_name}.{key} must be numeric")
                if key in RATE_KEYS:
                    _validate_rate(float(value), f"{section_name}.{key}")

        for name, share in self.adoption_scenarios.items():
            _validate_rate(float(share), f"adoption_scenarios.{name}")
        for value in self.reinvestment["sensitivity_values"]:
            _validate_rate(float(value), "reinvestment.sensitivity_values")

    def _validate_totals(self) -> None:
        company = self.company_data
        marketable = formulas.total_marketable_securities(
            company["current_marketable_securities"],
            company["non_current_marketable_securities"],
        )
        _validate_close(marketable, company["total_marketable_securities"], "total_marketable_securities")

        debt = formulas.total_debt(
            company["commercial_paper"],
            company["current_term_debt"],
            company["non_current_term_debt"],
        )
        _validate_close(debt, company["total_debt"], "total_debt")

    def _validate_scenarios(self) -> None:
        if self.baseline["adoption_scenario"] not in self.adoption_scenarios:
            raise ValueError("baseline.adoption_scenario must exist in adoption_scenarios")
        if self.baseline["stress_scenario"] not in self.stress_scenarios:
            raise ValueError("baseline.stress_scenario must exist in stress_scenarios")

        stress_keys = [
            "legacy_haircut",
            "tokenized_haircut",
            "legacy_buffer_ratio",
            "tokenized_buffer_ratio",
            "collateral_efficiency_spread",
            "technology_risk_premium",
        ]
        for name, stress in self.stress_scenarios.items():
            _require_keys(stress, stress_keys, f"stress_scenarios.{name}")
            for key in stress_keys:
                _validate_rate(float(stress[key]), f"stress_scenarios.{name}.{key}")
            if stress["tokenized_haircut"] > stress["legacy_haircut"]:
                raise ValueError(f"{name}: tokenized_haircut cannot exceed legacy_haircut")
            if stress["tokenized_buffer_ratio"] > stress["legacy_buffer_ratio"]:
                raise ValueError(f"{name}: tokenized_buffer_ratio cannot exceed legacy_buffer_ratio")

    def _validate_monte_carlo(self) -> None:
        _require_keys(self.monte_carlo, ["n_simulations", "seed", "distributions"], "monte_carlo")
        for name, dist in self.monte_carlo["distributions"].items():
            _require_keys(dist, ["type", "low", "high"], f"monte_carlo.distributions.{name}")
            if dist["type"] != "uniform":
                raise ValueError(f"Only uniform Monte Carlo distributions are supported: {name}")
            _validate_rate(float(dist["low"]), f"monte_carlo.distributions.{name}.low")
            _validate_rate(float(dist["high"]), f"monte_carlo.distributions.{name}.high")
            if dist["low"] > dist["high"]:
                raise ValueError(f"Distribution low cannot exceed high: {name}")

    def with_overrides(
        self,
        market_cap: float | None = None,
        adoption: float | None = None,
        stress: str | None = None,
    ) -> "ModelConfig":
        """Return a validated copy with CLI overrides applied."""
        data = deepcopy(self.raw)
        if market_cap is not None:
            data["company_data"]["market_cap"] = market_cap
        if adoption is not None:
            _validate_rate(adoption, "override adoption")
            data["adoption_scenarios"]["CLI Override"] = adoption
            data["baseline"]["adoption_scenario"] = "CLI Override"
        if stress is not None:
            if stress not in data["stress_scenarios"]:
                raise ValueError(f"Unknown stress scenario: {stress}")
            data["baseline"]["stress_scenario"] = stress
        return ModelConfig.from_dict(data, self.source_path)


def load_config(path: str | Path) -> ModelConfig:
    """Load a validated model config from YAML."""
    source = Path(path)
    with source.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError("params.yaml must contain a mapping")
    return ModelConfig.from_dict(data, source)


def _require_keys(section: dict[str, Any], keys: list[str], section_name: str) -> None:
    missing = [key for key in keys if key not in section]
    if missing:
        raise ValueError(f"Missing keys in {section_name}: {', '.join(missing)}")


def _validate_rate(value: float, label: str) -> None:
    if value < 0 or value > 1:
        raise ValueError(f"{label} must be a decimal rate between 0 and 1")


def _validate_close(derived: float, provided: float, label: str, tolerance: float = 1e-3) -> None:
    if abs(derived - provided) > tolerance:
        raise ValueError(f"{label} mismatch: derived {derived:.6f}, provided {provided:.6f}")
