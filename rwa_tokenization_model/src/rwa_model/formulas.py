"""Pure financial formulas for the RWA tokenization model."""

from __future__ import annotations


def total_marketable_securities(current: float, non_current: float) -> float:
    """Return total marketable securities."""
    return current + non_current


def total_debt(commercial_paper: float, current_term_debt: float, non_current_term_debt: float) -> float:
    """Return total debt."""
    return commercial_paper + current_term_debt + non_current_term_debt


def tokenized_collateral_pool(total_marketable: float, tokenized_share: float) -> float:
    """Return the tokenized collateral pool."""
    return total_marketable * tokenized_share


def collateral_portions(total_marketable: float, tokenized_share: float) -> tuple[float, float]:
    """Return legacy and tokenized collateral portions."""
    legacy_portion = total_marketable * (1.0 - tokenized_share)
    tokenized_portion = total_marketable * tokenized_share
    return legacy_portion, tokenized_portion


def full_legacy_usable_collateral(total_marketable: float, legacy_haircut: float) -> float:
    """Return usable collateral if the full portfolio remains legacy collateral."""
    return total_marketable * (1.0 - legacy_haircut)


def mixed_usable_collateral(
    total_marketable: float,
    tokenized_share: float,
    legacy_haircut: float,
    tokenized_haircut: float,
) -> float:
    """Return usable collateral for a mixed legacy/tokenized collateral portfolio."""
    legacy_portion, tokenized_portion = collateral_portions(total_marketable, tokenized_share)
    return legacy_portion * (1.0 - legacy_haircut) + tokenized_portion * (1.0 - tokenized_haircut)


def collateral_efficiency(usable_collateral: float, total_marketable: float) -> float:
    """Return usable collateral as a share of total marketable securities."""
    return usable_collateral / total_marketable


def legacy_liquidity_buffer(liquidity_base: float, legacy_buffer_ratio: float) -> float:
    """Return required liquidity buffer under a full legacy treasury policy."""
    return liquidity_base * legacy_buffer_ratio


def mixed_liquidity_buffer(
    liquidity_base: float,
    tokenized_share: float,
    legacy_buffer_ratio: float,
    tokenized_buffer_ratio: float,
) -> float:
    """Return required liquidity buffer under a mixed treasury policy."""
    return (
        liquidity_base * (1.0 - tokenized_share) * legacy_buffer_ratio
        + liquidity_base * tokenized_share * tokenized_buffer_ratio
    )


def tokenized_cost_of_debt(
    legacy_cost_of_debt: float,
    collateral_efficiency_spread: float,
    technology_risk_premium: float,
    floor_enabled: bool,
    debt_cost_floor: float,
) -> tuple[float, float, float]:
    """Return raw debt cost, final debt cost, and floor adjustment."""
    raw_cost = legacy_cost_of_debt - collateral_efficiency_spread + technology_risk_premium
    final_cost = max(raw_cost, debt_cost_floor) if floor_enabled else raw_cost
    return raw_cost, final_cost, final_cost - raw_cost


def capm_cost_of_equity(risk_free_rate: float, beta: float, market_risk_premium: float) -> float:
    """Return CAPM-implied cost of equity."""
    return risk_free_rate + beta * market_risk_premium


def wacc(
    debt_value: float,
    equity_value: float,
    cost_of_equity: float,
    cost_of_debt: float,
    tax_rate: float,
) -> tuple[float, float, float]:
    """Return WACC, debt weight, and equity weight."""
    invested_capital = debt_value + equity_value
    debt_weight = debt_value / invested_capital
    equity_weight = equity_value / invested_capital
    value = equity_weight * cost_of_equity + debt_weight * cost_of_debt * (1.0 - tax_rate)
    return value, debt_weight, equity_weight


def roe(net_income: float, shareholders_equity: float) -> float:
    """Return return on equity using book shareholders' equity."""
    return net_income / shareholders_equity


def adjusted_net_income(net_income: float, capital_liberated: float, reinvestment_return: float) -> float:
    """Return net income adjusted for after-tax reinvestment income."""
    return net_income + capital_liberated * reinvestment_return
