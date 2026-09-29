from pathlib import Path

import nbformat
from nbclient import NotebookClient


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_PATH = ROOT / "notebooks" / "exploratory_data_analysis.ipynb"


def test_eda_notebook_executes_and_exposes_analysis_contract():
    notebook = nbformat.read(NOTEBOOK_PATH, as_version=4)
    notebook.cells.append(
        nbformat.v4.new_code_cell(
            """
assert data.shape == (109, 25)
assert TARGET == "corrosion_rate_um_per_year"
assert set(EXCLUDED_FROM_MODEL) == {"paper_id", "alloy"}
assert TARGET not in predictor_columns
assert not set(EXCLUDED_FROM_MODEL) & set(predictor_columns)

assert dataset_findings["paper_count"] == 6
assert dataset_findings["alloy_count"] == 26
assert dataset_findings["unique_composition_count"] == 29
assert dataset_findings["target_skew"] > 5
assert dataset_findings["maximum_temperature_c"] == 4765

assert model_recommendations["model_key"].tolist() == [
    "gradient_boosted_trees",
    "rbf_support_vector_regression",
    "gaussian_process_regression",
]
assert model_recommendations["fit_in_this_notebook"].eq(False).all()
assert validation_recommendation == "leave-one-alloy-out"
"""
        )
    )

    client = NotebookClient(notebook, timeout=180, kernel_name="python3")
    client.execute(cwd=str(ROOT))
