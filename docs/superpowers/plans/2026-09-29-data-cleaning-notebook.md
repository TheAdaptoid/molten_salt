# Data Cleaning Notebook Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the existing cleaning notebook with an executable, validated pipeline that produces reviewed CSV and Parquet datasets for later EDA.

**Architecture:** Keep the cleaning logic in a compact seven-stage notebook, with executable assertions as close as possible to each transformation. Add one integration test that executes the notebook in a fresh kernel and verifies the persisted artifacts against the approved schema and key source-data cases.

**Tech Stack:** Python 3.13, pandas 3, Jupyter nbformat/nbclient, pytest, PyArrow, uv

## Global Constraints

- Implement only `src/molten_salt/data_cleaning.ipynb`; defer EDA until the user reviews the cleaning result.
- Use the rules in `docs/superpowers/specs/2026-09-29-data-cleaning-notebook-design.md` without adding inferred cleaning behavior.
- Preserve `4765` as a source value and report it; do not correct or remove it.
- Preserve exact duplicates and report their count.
- Recompute composition totals only after all elemental columns are numeric.
- Use the inclusive composition filter `95 <= total <= 105`.
- Export both `data/processed/corrosion_data_clean.csv` and `data/processed/corrosion_data_clean.parquet`.
- Do not implement EDA or commit changes unless the user explicitly requests a commit.

---

### Task 1: Add Executable Notebook Acceptance Test

**Files:**
- Modify: `pyproject.toml`
- Modify: `uv.lock`
- Create: `tests/test_data_cleaning_notebook.py`

**Interfaces:**
- Consumes: `src/molten_salt/data_cleaning.ipynb` and `data/corrosion_data.csv`.
- Produces: A pytest integration test that executes the notebook from the repository root and verifies the two cleaned artifacts.

- [ ] **Step 1: Add runtime and test dependencies**

Run:

```powershell
uv add pyarrow
uv add --dev nbclient nbformat pytest
```

Expected: `pyproject.toml` lists `pyarrow`; the development dependency group lists `nbclient`, `nbformat`, and `pytest`; `uv.lock` is updated.

- [ ] **Step 2: Write the failing integration test**

Create `tests/test_data_cleaning_notebook.py` with this behavior:

```python
from pathlib import Path

import nbformat
import pandas as pd
from nbclient import NotebookClient
from pandas.testing import assert_frame_equal


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_PATH = ROOT / "src" / "molten_salt" / "data_cleaning.ipynb"
CSV_PATH = ROOT / "data" / "processed" / "corrosion_data_clean.csv"
PARQUET_PATH = ROOT / "data" / "processed" / "corrosion_data_clean.parquet"

EXPECTED_COLUMNS = [
    "paper_id",
    "alloy",
    "temperature_c",
    "exposure_time_h",
    "flow_m_per_s",
    "corrosion_rate_um_per_year",
    "headgas_air",
    "headgas_n2",
    "headgas_o2_sealed_loop",
    "ni_wt_pct",
    "cr_wt_pct",
    "fe_wt_pct",
    "c_wt_pct",
    "mn_wt_pct",
    "si_wt_pct",
    "n_wt_pct",
    "nb_wt_pct",
    "co_wt_pct",
    "mo_wt_pct",
    "al_wt_pct",
    "ti_wt_pct",
    "cu_wt_pct",
    "w_wt_pct",
    "p_wt_pct",
    "s_wt_pct",
]


def test_cleaning_notebook_executes_and_exports_contract():
    notebook = nbformat.read(NOTEBOOK_PATH, as_version=4)
    client = NotebookClient(notebook, timeout=180, kernel_name="python3")
    client.execute(cwd=str(ROOT))

    assert CSV_PATH.exists()
    assert PARQUET_PATH.exists()

    csv_data = pd.read_csv(CSV_PATH)
    parquet_data = pd.read_parquet(PARQUET_PATH)

    assert csv_data.shape == (109, 25)
    assert csv_data.columns.tolist() == EXPECTED_COLUMNS
    assert not csv_data.isna().any().any()
    assert csv_data.duplicated().sum() == 0
    assert 4765 in csv_data["temperature_c"].values

    headgas_columns = [
        "headgas_air",
        "headgas_n2",
        "headgas_o2_sealed_loop",
    ]
    assert set(csv_data[headgas_columns].stack().unique()) <= {0, 1}
    assert csv_data[headgas_columns].sum(axis=1).eq(1).all()

    floored = csv_data.loc[
        (csv_data["paper_id"] == "P008")
        & (csv_data["temperature_c"] == 445)
        & (csv_data["alloy"] == "Type 316 Stainless Steel"),
        "corrosion_rate_um_per_year",
    ]
    assert floored.tolist() == [3.0]

    bounded = csv_data.loc[
        (csv_data["paper_id"] == "P008")
        & (csv_data["temperature_c"] == 600)
        & (csv_data["alloy"] == "Type 304/304L stainless steel")
        & (csv_data["corrosion_rate_um_per_year"] == 5),
        "c_wt_pct",
    ]
    assert bounded.tolist() == [0.03]

    assert "A516 Gr70 Carbon Steel" not in set(csv_data["alloy"])
    assert not csv_data["alloy"].str.startswith(" ").any()
    assert not csv_data["alloy"].str.endswith(" ").any()

    assert_frame_equal(
        csv_data,
        parquet_data,
        check_dtype=False,
        check_exact=False,
        rtol=1e-12,
        atol=1e-12,
    )
```

- [ ] **Step 3: Run the test and confirm the expected failure**

Run:

```powershell
$env:PYTHONUTF8='1'; uv run pytest tests/test_data_cleaning_notebook.py -v
```

Expected: FAIL because the current two-cell notebook neither exports the approved artifacts nor implements the schema.

- [ ] **Step 4: Review the test failure**

Confirm the failure originates from the existing notebook behavior rather than test setup, kernel startup, or a missing dependency. If setup fails, correct only the test harness and rerun until it reaches a product-behavior failure.

---

### Task 2: Replace The Cleaning Notebook

**Files:**
- Modify: `src/molten_salt/data_cleaning.ipynb`

**Interfaces:**
- Consumes: `data/corrosion_data.csv` with the 25 required source columns defined below.
- Produces: `clean_data: pandas.DataFrame` with the 25-column schema in Task 1 and the two files under `data/processed/`.

- [ ] **Step 1: Replace the notebook with a valid nbformat 4 document**

Use `apply_patch` to replace the notebook. Keep one title/contract markdown cell and seven focused code cells. Use a Python 3 kernelspec. Do not retain stale execution counts or outputs while authoring.

- [ ] **Step 2: Implement setup and project-root resolution**

The setup cell must import `Path`, `re`, `pandas as pd`, and `assert_frame_equal`. Resolve the project root by walking from `Path.cwd()` through its parents until finding `pyproject.toml`; raise `FileNotFoundError` if no root is found. Define:

```python
RAW_PATH = PROJECT_ROOT / "data" / "corrosion_data.csv"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"
CSV_PATH = OUTPUT_DIR / "corrosion_data_clean.csv"
PARQUET_PATH = OUTPUT_DIR / "corrosion_data_clean.parquet"
```

- [ ] **Step 3: Implement loading and source inspection**

Define the complete required-source-column list and raise `ValueError` listing any missing columns. Load `raw_data` with `pd.read_csv(RAW_PATH)`. Display:

- Raw shape.
- `raw_data.dtypes`.
- Missing counts greater than zero.
- Exact duplicate count without removing rows.
- Unique values for `Salt`, `Headgas`, and `Alloy`.

The required source columns are:

```python
[
    "Paper ID", "Salt", "Temperature (celcius)", "Exposure Time (hours)",
    "Headgas", "Flow (m/s)", "Corrosion Rate (μm/yr)", "Alloy",
    "Ni (wt.%)", "Cr (wt.%)", "Fe (wt.%)", "C (wt.%)", "Mn (wt.%)",
    "Si (wt.%)", "N (wt.%)", "Nb (wt.%)", "Co (wt.%)", "Mo (wt.%)",
    "Al (wt.%)", "Ti (wt.%)", "Cu (wt.%)", "W (wt.%)", "P (wt.%)",
    "S (wt.%)", "Composition Check",
]
```

- [ ] **Step 4: Implement value normalization**

Create `data = raw_data.copy()` and define `ELEMENT_COLUMNS` as the 16 wt.% columns from Task 1. Implement a parser with these exact semantics:

```python
def parse_composition_value(value):
    if pd.isna(value):
        return float("nan")

    text = str(value).strip()
    if text.startswith("≤"):
        text = text[1:].strip()
    elif text.startswith("<="):
        text = text[2:].strip()

    range_match = re.fullmatch(
        r"([0-9]+(?:\.[0-9]+)?)\s*-\s*([0-9]+(?:\.[0-9]+)?)",
        text,
    )
    if range_match:
        lower, upper = map(float, range_match.groups())
        return (lower + upper) / 2

    return float(text)
```

Add immediate executable checks:

```python
assert parse_composition_value("≤0.27") == 0.27
assert parse_composition_value("<=0.025") == 0.025
assert parse_composition_value("0.85-1.2") == 1.025
```

Apply the parser to all elemental columns. Convert corrosion rates by stripping whitespace, removing only a leading `<`, and calling `pd.to_numeric(..., errors="raise")`. Trim only surrounding whitespace from `Alloy`.

- [ ] **Step 5: Implement row filtering after normalization**

Treat temperature, exposure time, headgas, flow, corrosion rate, alloy, and every elemental column as essential. Report and remove rows with a missing essential value. On the remaining rows:

```python
data["recomputed_composition_total"] = data[ELEMENT_COLUMNS].sum(axis=1)
composition_mask = data["recomputed_composition_total"].between(95, 105, inclusive="both")
```

Display the paper ID, alloy, and recomputed total for rejected rows. Filter to passing rows only. Do not use the source `Composition Check` values to make this decision.

- [ ] **Step 6: Implement feature shaping and final schema**

Verify `Salt` has exactly one non-null unique value; otherwise raise `ValueError`. Report that value and drop `Salt`, `Composition Check`, and `recomputed_composition_total`.

Require the exact headgas categories `{"air", "N2", "O2 (sealed loop)"}`. Raise a `ValueError` that shows expected and actual sets if they differ. Replace `Headgas` with `pd.get_dummies(..., dtype="int8")`, renamed and ordered as:

```python
[
    "headgas_air",
    "headgas_n2",
    "headgas_o2_sealed_loop",
]
```

Rename all remaining columns to the `EXPECTED_COLUMNS` names in Task 1, then reorder `clean_data` to exactly that list. Keep `paper_id` and `alloy` as string columns, the three headgas columns as integers, and all scientific measurements as numeric columns.

- [ ] **Step 7: Implement validation and non-blocking reports**

Raise clear assertion failures unless all of these hold:

```python
assert clean_data.columns.tolist() == EXPECTED_COLUMNS
assert not clean_data.isna().any().any()
assert clean_data[[
    "headgas_air", "headgas_n2", "headgas_o2_sealed_loop"
]].sum(axis=1).eq(1).all()
```

Use pandas dtype predicates to assert every non-string column is numeric. Report `clean_data.duplicated().sum()` without dropping duplicates. Display rows where `temperature_c > 1000`, preserving them in `clean_data`. Display final shape and data types.

- [ ] **Step 8: Implement export and round-trip verification**

Create the output directory, export with `index=False`, reload both files, and compare them:

```python
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
clean_data.to_csv(CSV_PATH, index=False)
clean_data.to_parquet(PARQUET_PATH, index=False)

csv_reloaded = pd.read_csv(CSV_PATH)
parquet_reloaded = pd.read_parquet(PARQUET_PATH)
assert_frame_equal(
    csv_reloaded,
    parquet_reloaded,
    check_dtype=False,
    check_exact=False,
    rtol=1e-12,
    atol=1e-12,
)
```

Report both output paths and the exported shape.

- [ ] **Step 9: Run the targeted acceptance test**

Run:

```powershell
$env:PYTHONUTF8='1'; uv run pytest tests/test_data_cleaning_notebook.py -v
```

Expected: PASS, with one test confirming the notebook execution and artifact contract.

---

### Task 3: Final Notebook And Artifact Verification

**Files:**
- Verify: `src/molten_salt/data_cleaning.ipynb`
- Verify: `data/processed/corrosion_data_clean.csv`
- Verify: `data/processed/corrosion_data_clean.parquet`
- Verify: `tests/test_data_cleaning_notebook.py`

**Interfaces:**
- Consumes: The completed notebook, integration test, and generated artifacts.
- Produces: Evidence that the notebook is reproducible and ready for the user's review before EDA begins.

- [ ] **Step 1: Execute all tests in a fresh process**

Run:

```powershell
$env:PYTHONUTF8='1'; uv run pytest -v
```

Expected: All tests pass.

- [ ] **Step 2: Execute the notebook and persist reviewed outputs**

Run this command from the repository root:

```powershell
$env:PYTHONUTF8='1'; uv run jupyter execute "src/molten_salt/data_cleaning.ipynb" --inplace
```

If this Jupyter installation does not provide `jupyter execute`, use the already tested `NotebookClient` path from Task 1 to execute in memory, then save the executed notebook with `nbformat.write`. Do not change notebook code during this verification step.

Expected: Execution completes without an exception and refreshes both processed artifacts.

- [ ] **Step 3: Inspect the executed notebook output**

Confirm the visible audit reports include:

- Raw shape `(116, 25)`.
- Two incomplete rows removed.
- Five composition-total failures removed.
- Final shape `(109, 25)`.
- Duplicate count `0`, reported without a drop operation.
- A temperature review row containing `4765`.
- Both processed output paths.

- [ ] **Step 4: Inspect repository changes without altering unrelated files**

Run:

```powershell
git status --short
git diff -- pyproject.toml uv.lock tests/test_data_cleaning_notebook.py src/molten_salt/data_cleaning.ipynb
```

Confirm no unrelated user files were modified. Do not stage or commit.

- [ ] **Step 5: Present the completed cleaning notebook for user review**

Report the notebook path, output paths, row-removal counts, final shape, and exact verification commands. Stop before designing or modifying `eda.ipynb` so the user can complete the requested review pass.
