Upgrade my existing Python model repo, but keep it minimal and thesis-focused.

The repo supports Chapter 3 of my Master thesis:

Applied Simulation of Tokenized Treasury Collateral and Financial Market Efficiency

The goal is not to turn the repo into a big research platform. I am already writing the thesis paper separately. The repo should only support the thesis by generating clean tables, clean charts, and clear documentation of assumptions.

Preserve the main thesis interpretation:

Tokenized collateral is tested as a collateral and liquidity infrastructure improvement. The strongest expected result is liquidity efficiency and capital liberated. WACC and ROE are secondary and conditional effects.

Do not present tokenization as automatically reducing WACC or automatically increasing profitability.

==================================================
1. KEEP THE EXISTING MODEL WORKING
==================================================

Do not break the current model, formulas, CLI, outputs, or charts.

Only improve structure, exports, documentation, and thesis-ready outputs.

Do not add unnecessary complexity.

==================================================
2. ADD A SHORT README SECTION
==================================================

Update the README with a short section called:

"Thesis Context"

Include:

- This repo supports the applied chapter of a Master thesis on RWA tokenization and financial market efficiency.
- The model uses Apple as a real-company baseline to test a counterfactual collateral mechanism.
- The repo does not predict Apple’s actual treasury strategy.
- The model compares a traditional collateral framework with a tokenized RWA collateral framework.
- The main outputs are usable collateral, capital liberated, WACC change, and ROE change.
- The key interpretation is that liquidity efficiency is more robust than WACC reduction.

Keep it concise.

==================================================
3. ADD A SIMPLE METHODOLOGY NOTE
==================================================

Create:

docs/methodology_note.md

Keep it short, around 1–2 pages.

Include:

1. Purpose of the model
2. Counterfactual logic
3. Transmission mechanism
4. Book-value vs market-value WACC treatment
5. Reinvestment channel
6. Monte Carlo and sensitivity purpose
7. Interpretation rule

Use this mechanism:

Marketable securities
→ tokenized collateral pool
→ haircut adjustment
→ usable collateral
→ liquidity buffer reduction
→ capital liberated
→ cost of debt, WACC, and ROE effects

Make clear:

- Apple is a baseline case, not an assumed adopter.
- Tokenization does not create new capital.
- Capital liberated means reduced liquidity buffer requirement.
- WACC change is conditional on funding-cost assumptions.
- ROE change is conditional on reinvestment of liberated capital.
- Book vs market WACC is a capital-structure layer, not a separate model.

==================================================
4. ADD A SIMPLE SOURCE MAP
==================================================

Create:

docs/source_map.md

Include one table:

| Variable Group | Variables | Source Type | Thesis Treatment |
|---|---|---|---|

Rows:

1. Apple accounting data
Variables:
cash, marketable securities, debt, net income, shareholders’ equity, tax rate
Source Type:
Apple Form 10-K
Thesis Treatment:
Observed company data

2. Market inputs
Variables:
risk-free rate, beta, market risk premium, market capitalization, legacy cost of debt
Source Type:
Public market / valuation sources
Thesis Treatment:
Market inputs

3. Scenario assumptions
Variables:
adoption levels, haircuts, buffer ratios, collateral efficiency spread, technology risk premium, reinvestment return
Source Type:
Author calibration
Thesis Treatment:
Scenario assumptions

4. Model outputs
Variables:
usable collateral, additional usable collateral, capital liberated, WACC change, ROE change
Source Type:
Python calculations
Thesis Treatment:
Simulation results

Add one note:

Calibrated assumptions should not be presented as directly observed Apple data.

==================================================
5. CREATE THESIS-READY OUTPUTS
==================================================

Create:

outputs/thesis_ready/

Inside it, export only the tables and charts I will likely use in the thesis.

Tables:

table_3_1_company_data.csv
table_3_2_variable_definitions.csv
table_3_3_scenario_assumptions.csv
table_3_4_baseline_results.csv
table_3_5_adoption_results.csv
table_3_6_stress_results.csv
table_3_7_monte_carlo_summary.csv
table_3_8_sensitivity_summary.csv
table_3_9_reinvestment_sensitivity.csv

Do not delete existing outputs. Just create this clean thesis-ready folder.

==================================================
6. CREATE THESIS-READY CHARTS
==================================================

Create:

outputs/thesis_ready/charts/png
outputs/thesis_ready/charts/svg

Export only the most important charts:

1. transmission_mechanism
2. cost_of_debt_bridge
3. capital_liberated_by_adoption
4. capital_liberated_under_stress
5. wacc_change_under_stress_book_vs_market
6. monte_carlo_distribution
7. sensitivity_tornado
8. reinvestment_sensitivity

Use a clean academic finance style:

- white background
- dark navy text
- muted blue accents
- gray gridlines
- clear titles
- clear axis labels
- no neon
- no crypto-style visuals

Do not remove the full chart folder. This is just the curated chart set for the thesis.

==================================================
7. ADD FIGURE CAPTIONS
==================================================

Create:

outputs/thesis_ready/figure_captions.md

Add short captions for the thesis-ready charts.

Example:

Figure 3.X: Cost of Debt Bridge  
This figure decomposes the transition from the legacy cost of debt to the tokenized cost of debt. The collateral efficiency spread reduces borrowing cost, while the technology risk premium offsets part of the benefit.

Figure 3.X: Capital Liberated by Adoption Level  
This figure shows how capital liberated changes as the tokenized share of marketable securities increases under normal market conditions.

Figure 3.X: WACC Change under Stress Scenarios  
This figure compares WACC changes under book-value and market-value capital structure weights across stress scenarios.

Keep captions concise and academic.

==================================================
8. ADD A SHORT EXECUTIVE SUMMARY
==================================================

Create:

outputs/thesis_ready/executive_summary.md

It should include:

- baseline result summary
- adoption result summary
- stress result summary
- Monte Carlo summary
- sensitivity summary
- main interpretation

Main interpretation:

The model suggests that tokenized collateral has its most robust effect through liquidity efficiency and capital liberated. WACC effects are conditional on funding-cost assumptions and capital-structure weights. ROE effects depend on whether liberated capital is productively redeployed.

Keep it short. This is only to help me write the thesis, not to replace the thesis.

==================================================
9. KEEP MATRIX / GRID OUTPUTS AS OPTIONAL
==================================================

If the repo currently generates adoption-stress grids, matrices, or heatmaps, keep them in the full outputs folder.

But do not include them in thesis_ready unless I explicitly ask.

The written thesis will focus on:

- baseline results
- adoption results
- stress results
- robustness and sensitivity results

The full grid can stay as an auxiliary output.

==================================================
10. ADD BASIC TESTS ONLY
==================================================

Add minimal pytest tests:

1. tokenized haircut <= legacy haircut in base scenario
2. tokenized buffer ratio <= legacy buffer ratio in base scenario
3. market cap affects WACC but not capital liberated
4. ROE uses book equity only
5. changing adoption changes tokenized pool and capital liberated
6. Monte Carlo with same seed is reproducible

Do not overbuild tests.

==================================================
11. UPDATE EXPORT ZIP
==================================================

If the repo already creates a ZIP file, make sure it includes:

- full outputs
- thesis_ready folder
- docs/methodology_note.md
- docs/source_map.md

==================================================
12. FINAL RULES
==================================================

Do not make the repo bigger than necessary.

Do not add a dashboard.

Do not add a long report generator unless it already exists.

Do not introduce new financial assumptions.

Do not change the model logic unless needed to fix bugs.

The final repo should feel like:

Python repo = clean research engine
Thesis paper = main written analysis

The repo should mainly help me produce reliable tables, clean charts, and clear documentation for Chapter 3.