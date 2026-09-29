# Data Cleaning Notebook Design

## Scope

Replace `src/molten_salt/data_cleaning.ipynb` with a compact, staged notebook that cleans `data/corrosion_data.csv`, validates the result, and exports stable inputs for a later EDA notebook. The EDA notebook is intentionally deferred until the cleaned output has received one complete user review.

## Data Flow

The notebook will contain seven stages:

1. Set up imports, project-relative paths, and display settings.
2. Load and inspect the raw CSV, including shape, data types, missingness, duplicate count, and categorical values.
3. Normalize corrosion-rate, elemental-composition, and alloy values.
4. Remove incomplete records and records whose recomputed elemental total is outside the accepted range.
5. Shape the final features, including column removal, one-hot encoding, and renaming.
6. Validate the cleaned dataset and report non-blocking quality concerns.
7. Export CSV and Parquet artifacts, reload them, and verify consistency.

The implementation will be completed as a whole and presented for one review pass rather than reviewed stage by stage.

## Transformation Rules

- Convert corrosion rates reported as `<3` to numeric `3.0` without adding a censoring flag.
- Convert elemental upper bounds such as `<=0.27` or the Unicode equivalent to their stated numeric bounds.
- Convert elemental ranges such as `0.85-1.2` to their midpoint.
- Convert every elemental composition field to a numeric type before calculating composition totals.
- Trim surrounding whitespace from alloy labels without merging or otherwise standardizing alloy names.
- Remove rows with a missing test condition, target, alloy label, headgas value, or elemental composition and report the count removed.
- Recompute the elemental wt.% total from the cleaned elemental columns.
- Retain only rows whose recomputed total is within the inclusive range `95 <= total <= 105`.
- Remove both the source `Composition Check` field and the temporary recomputed total from the final dataset.
- Report exact duplicate rows without removing them.
- Preserve the source temperature value `4765` and report it as a range warning.
- Verify that `Salt` has one unique value, report that value, and remove the column.
- Retain `Paper ID` as a provenance field.
- Replace `Headgas` with integer one-hot columns for `air`, `N2`, and `O2 (sealed loop)`.

## Output Schema

All output headers will use ASCII snake case with concise units.

Identifiers:

- `paper_id`
- `alloy`

Test conditions and target:

- `temperature_c`
- `exposure_time_h`
- `flow_m_per_s`
- `corrosion_rate_um_per_year`

Headgas indicators:

- `headgas_air`
- `headgas_n2`
- `headgas_o2_sealed_loop`

Elemental composition:

- `ni_wt_pct`
- `cr_wt_pct`
- `fe_wt_pct`
- `c_wt_pct`
- `mn_wt_pct`
- `si_wt_pct`
- `n_wt_pct`
- `nb_wt_pct`
- `co_wt_pct`
- `mo_wt_pct`
- `al_wt_pct`
- `ti_wt_pct`
- `cu_wt_pct`
- `w_wt_pct`
- `p_wt_pct`
- `s_wt_pct`

## Validation And Error Handling

The notebook will stop with a clear error when:

- A required raw column is absent.
- A bounded or ranged composition value cannot be parsed.
- Numeric conversion leaves an unexpected nonnumeric value.
- An unknown headgas category would change the agreed output schema.
- The exported CSV and Parquet artifacts cannot be reloaded consistently.

The notebook will report without stopping when:

- Exact duplicate rows exist.
- Temperatures exceed `1000 C`, which reports the retained `4765` value without modifying or removing it.
- Incomplete rows are removed.
- Rows fail the recomputed composition-total filter.

Exports will occur only after all blocking validation passes. The notebook will create `data/processed/` when necessary and write:

- `data/processed/corrosion_data_clean.csv`
- `data/processed/corrosion_data_clean.parquet`

Both files will be reloaded and checked for matching shapes, columns, and values, allowing only normal floating-point serialization tolerance. The project will add `pyarrow` as the Parquet engine.

## Verification

- Execute the notebook from a clean kernel from top to bottom.
- Confirm the input audit matches the raw source characteristics.
- Confirm all transformation counts are displayed.
- Confirm the final schema exactly matches the contract above.
- Confirm no required value is missing and all numeric columns are numeric.
- Confirm duplicates are reported but retained.
- Confirm the temperature warning includes `4765` without modifying the value.
- Confirm CSV and Parquet reload to equivalent data.

## Deferred EDA

The EDA notebook will load the approved cleaned artifact and will not duplicate cleaning logic. Its questions, plots, dependencies, and structure will be designed after the cleaning notebook and outputs pass the user's review.
