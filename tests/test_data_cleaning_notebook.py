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
