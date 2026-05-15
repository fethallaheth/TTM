# Methodology Note

## Purpose of the Model

This repository supports the applied chapter of a Master thesis on tokenized treasury collateral and financial market efficiency. The model evaluates a counterfactual mechanism in which part of a company's marketable securities can be represented as tokenized real-world asset collateral. The purpose is not to forecast a company's actual treasury strategy, but to test how collateral infrastructure changes may affect usable collateral, liquidity buffers, funding cost, WACC, and ROE.

Apple is used as a baseline case because it provides a large, liquid, and well-documented treasury balance sheet. The model should be interpreted as an applied simulation using Apple data, not as an assumption that Apple will adopt tokenized collateral.

## Counterfactual Logic

The model compares two collateral frameworks:

1. A traditional collateral framework in which marketable securities remain fully subject to legacy haircuts and liquidity buffer assumptions.
2. A tokenized RWA collateral framework in which a selected share of marketable securities receives tokenized-collateral haircuts and buffer assumptions.

The difference between these two frameworks creates the simulated efficiency effect. Tokenization does not create new capital. It changes the modeled usability and liquidity treatment of existing marketable securities.

## Transmission Mechanism

The thesis mechanism is:

```text
Marketable securities
-> tokenized collateral pool
-> haircut adjustment
-> usable collateral
-> liquidity buffer reduction
-> capital liberated
-> cost of debt, WACC, and ROE effects
```

Capital liberated means a reduction in the modeled liquidity buffer requirement. It is not new cash, new earnings, or new equity. It represents balance-sheet capacity that could become available if collateral and liquidity requirements are lower under the tokenized framework.

## Book-Value vs Market-Value WACC

The model calculates both book-value and market-value WACC effects. This is a capital-structure treatment, not a separate model. Book-value WACC uses book debt and book shareholders' equity. Market-value WACC uses debt and market capitalization.

The market-value WACC effect is expected to be smaller for firms with very large market capitalization because debt receives a smaller capital-structure weight. This distinction is important for interpretation: a visible book-value WACC movement can translate into a much smaller market-value WACC movement.

## Reinvestment Channel

ROE remains based on book shareholders' equity. The model does not calculate ROE using market capitalization. Any ROE change comes from an assumed after-tax return on liberated capital.

Therefore, ROE effects are conditional. If liberated capital is not redeployed productively, tokenization does not automatically increase profitability. The reinvestment sensitivity table shows how the ROE effect changes under alternative reinvestment return assumptions.

## Monte Carlo and Sensitivity Purpose

Monte Carlo simulation tests whether model conclusions are robust across plausible ranges for adoption, haircuts, buffer ratios, collateral efficiency spreads, technology risk premia, and reinvestment returns.

One-way sensitivity analysis isolates which individual assumptions have the largest effect on key outputs. These robustness tools are used to support interpretation, not to claim precise prediction.

## Interpretation Rule

The main thesis interpretation is that tokenized collateral is tested as collateral and liquidity infrastructure. The strongest expected effect is liquidity efficiency and capital liberated. WACC effects are secondary and depend on funding-cost assumptions. ROE effects are secondary and depend on reinvestment of liberated capital.

Calibrated assumptions should not be presented as directly observed Apple data.
