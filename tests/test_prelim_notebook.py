from pathlib import Path

import nbformat
from nbclient import NotebookClient


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_PATH = ROOT / "notebooks" / "prelim.ipynb"


def test_prelim_notebook_compares_linear_regression_dataset_variants():
    notebook = nbformat.read(NOTEBOOK_PATH, as_version=4)
    notebook.cells.append(
        nbformat.v4.new_code_cell(
            """
expected_datasets = {
    "Unnormalized features / raw target",
    "Unnormalized features / log target",
    "Normalized features / raw target",
    "Normalized features / log target",
}

assert set(dataset_comparison["dataset"]) == expected_datasets
assert len(dataset_comparison) == 4
assert (dataset_comparison["mean_rmse"] > 0).all()
assert (dataset_comparison["rmse_std"] >= 0).all()
assert best_dataset_name == dataset_comparison.iloc[0]["dataset"]
assert dataset_comparison.equals(
    dataset_comparison.sort_values(
        ["mean_rmse", "rmse_std"], kind="stable"
    ).reset_index(drop=True)
)
assert len(dataset_comparison_ax.patches) == 4
"""
        )
    )

    client = NotebookClient(notebook, timeout=180, kernel_name="python3")
    client.execute(cwd=str(ROOT))
