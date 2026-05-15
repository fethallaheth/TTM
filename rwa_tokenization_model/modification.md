You are working on my Python financial simulation repo for my Master’s thesis applied chapter.

IMPORTANT:
Do NOT make it paper-style.
Do NOT create abstract, introduction, literature review, conclusion, or full paper draft.
Do NOT create outputs/paper_ready/.
Do NOT use journal/manuscript language.

The goal is to make the repo produce thesis-ready and defense-ready outputs for Chapter 3:

“Applied Simulation of Tokenized Treasury Collateral and Financial Market Efficiency”

The applied chapter studies how tokenizing part of Apple Inc.’s marketable securities may affect:

- usable collateral
- liquidity buffer requirements
- capital liberated
- cost of debt
- WACC under book-value and market-value weights
- ROE under conditional reinvestment
- adoption scenarios
- stress scenarios
- Monte Carlo robustness
- sensitivity analysis
- model plausibility

Apple must be treated only as a computational baseline, not as a forecast that Apple will tokenize its assets.

Do not rebuild the model.
Do not change the core financial logic.
Do not remove existing outputs.
Do not add unrelated quant-finance outputs such as efficient frontier, trading P&L VaR backtesting, or portfolio drawdown.

The objective is to make the repo outputs easier to use directly in Chapter 3 and easier to defend in front of a jury.

TASK 1 — Keep or improve the thesis-ready output folder

Use:

outputs/thesis_ready/

Inside it, organize outputs as:

outputs/thesis_ready/tables/
outputs/thesis_ready/charts/
outputs/thesis_ready/reports/
outputs/thesis_ready/appendix/

If the repo already has outputs/thesis_ready/, update it cleanly.
Do not create outputs/paper_ready/.

TASK 2 — Add missing defensive tables

Create the following files:

outputs/thesis_ready/tables/parameter_justification.csv
outputs/thesis_ready/reports/parameter_justification.md

The table should include:

- tokenized_asset_share
- legacy_haircut
- tokenized_haircut
- legacy_buffer_ratio
- tokenized_buffer_ratio
- collateral_efficiency_spread
- technology_risk_premium
- reinvestment_return
- debt_cost_floor
- adoption scenario levels
- stress scenario parameters

Columns:

- Parameter
- Symbol
- Baseline value
- Conservative / lower value
- Aggressive / upper value
- Source type
- Financial justification
- Model channel affected

Source type must be one of:

- Observed company data
- Market input
- Scenario-calibrated assumption
- Model output

Do not invent fake citations.
If a parameter is not directly observed, classify it honestly as “Scenario-calibrated assumption.”

TASK 3 — Add plausibility check table

Create:

outputs/thesis_ready/tables/plausibility_checks.csv
outputs/thesis_ready/reports/plausibility_checks.md

Include these checks:

1. tokenized_haircut <= legacy_haircut
2. tokenized_buffer_ratio <= legacy_buffer_ratio
3. adoption share remains partial and realistic
4. tokenized cost of debt respects the debt cost floor
5. book-value WACC and market-value WACC are both reported
6. ROE effect is conditional on reinvestment
7. capital liberated is not treated as newly created capital
8. technology risk premium can offset collateral efficiency spread
9. stress scenarios increase financial friction consistently
10. Monte Carlo outputs remain within reasonable bounds

Columns:

- Check
- Rule
- Result: PASS / WARNING / FAIL
- Explanation
- Affected output

This table should be written for thesis defense purposes, meaning it should help answer the jury question:
“Is the model financially consistent?”

TASK 4 — Add interpretation hierarchy report

Create:

outputs/thesis_ready/reports/interpretation_hierarchy.md

Write it in clear academic finance language, but not paper-style.

Use this structure:

1. Robust results
   - additional usable collateral
   - capital liberated

Explain that these are the strongest results because they follow directly from lower haircuts and lower effective liquidity buffer requirements.

2. Conditional results
   - cost of debt change
   - WACC change

Explain that these depend on whether the collateral efficiency spread is larger than the technology, legal, custody, and oracle risk premium. Also explain the role of the debt cost floor.

3. Highly conditional results
   - ROE change

Explain that ROE improvement depends on whether liberated capital is reinvested productively. Do not present ROE improvement as an automatic result of tokenization.

The tone should be suitable for Chapter 3 results interpretation, not a journal article.

TASK 5 — Add model logic diagram

Create:

outputs/thesis_ready/charts/model_logic_diagram.png
outputs/thesis_ready/reports/model_logic_diagram.md

The diagram should show:

Marketable Securities
→ Tokenized Asset Share
→ Tokenized Collateral Pool
→ Haircut Reduction
→ Additional Usable Collateral
→ Liquidity Buffer Reduction
→ Capital Liberated
→ Funding Cost Adjustment
→ WACC Change
→ Conditional ROE Change

Also add a risk-offset channel:

Technology / Legal / Custody / Oracle Risk Premium
→ increases tokenized cost of debt
→ may reduce or reverse WACC benefit

The diagram should be simple, clean, and thesis-ready.

TASK 6 — Improve executive summary formatting

If outputs/thesis_ready/executive_summary.md already exists, improve its formatting.

It should include:

1. Purpose of the simulation
2. Case company and why Apple is used
3. Baseline result
4. Adoption scenario result
5. Stress scenario result
6. Monte Carlo and sensitivity result
7. Main interpretation

The writing must be direct and useful for Chapter 3.
Do not make it sound like a paper abstract.
Do not overclaim.
Do not say tokenization automatically improves firm value.

TASK 7 — Add Chapter 3 ready report

Create:

outputs/thesis_ready/reports/chapter_3_results_pack.md

This should combine the thesis-ready outputs in the same order as my Chapter 3 structure:

3.1 Research Design
- short note pointing to the model logic diagram

3.2 Data and Sample Construction
- company baseline table
- variable definition table
- parameter justification table

3.3 Methodology
- scenario design table
- model assumptions
- plausibility check table

3.4 Results
- baseline results
- adoption scenario results
- stress scenario results
- Monte Carlo robustness results
- sensitivity results
- financial interpretation

3.5 Discussion
- implications for financial market efficiency
- implications for firms
- implications for investors and market infrastructure
- regulatory and practical considerations
- limitations
- future research

This file should not rewrite the whole thesis chapter.
It should be a practical results pack that helps me copy tables, figures, captions, and interpretation into my thesis.

TASK 8 — Improve figure captions

Create or update:

outputs/thesis_ready/figure_captions.md

Each caption should explain:

- what the figure shows
- why it matters
- how to interpret it
- whether the result is robust or conditional

Keep captions short and academic.

TASK 9 — Add appendix-style files

Create:

outputs/thesis_ready/appendix/variables_and_equations.md
outputs/thesis_ready/appendix/assumptions_and_limits.md
outputs/thesis_ready/appendix/reproducibility.md

variables_and_equations.md:
- list all variables
- symbols
- definitions
- equations

assumptions_and_limits.md:
- list calibrated assumptions
- explain why they are used
- explain that they are not directly observed market facts

reproducibility.md:
- how to run the model
- Python command
- required files
- output folders

TASK 10 — Add or update CLI command

If the repo already has a thesis-ready command, update it.

The command should generate:

- thesis-ready tables
- thesis-ready charts
- parameter justification table
- plausibility checks
- interpretation hierarchy
- chapter_3_results_pack.md
- appendix files

Use the existing CLI style.

Example command:

python -m rwa_model.cli thesis-ready

Do not create a paper-ready command.

TASK 11 — Update README

Update README.md with a short section:

“Generating thesis-ready outputs”

Include:

- command to run
- output folder
- what files are generated
- warning that these outputs are for thesis Chapter 3 and not a journal paper

STYLE RULES

- Write in academic finance language, but keep it readable.
- Keep the tone serious and balanced.
- Do not make it journal-paper style.
- Do not create abstract/introduction/literature/conclusion sections.
- Do not overclaim.
- Do not say “this proves.”
- Use wording like:
  - “the simulation suggests”
  - “under the calibrated assumptions”
  - “the result is conditional”
  - “the result is robust within the tested range”
- Separate robust results from conditional results.
- Treat Apple as a computational baseline.
- Be honest about scenario-calibrated assumptions.
- Do not invent citations.

FINAL RESPONSE AFTER IMPLEMENTATION

After editing the repo, summarize:

- files added
- files modified
- how to run the thesis-ready output
- where the Chapter 3 results pack is saved
- any warnings or missing assumptions