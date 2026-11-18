# Unified Notebook Cleanup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Simplify the unified corrosion notebook and refresh its classical-model outputs without changing the intended experiment.

**Architecture:** Keep analysis code in the notebook. Parallel Luna subagents prepare independent, cell-scoped proposals; one integrator applies them to the original notebook and performs the final execution. Use temporary execution and result paths so existing result files remain untouched.

**Tech Stack:** Python, Jupyter/nbformat/nbclient, Ruff, NumPy, pandas, scikit-learn, PyTorch, PennyLane.

**Spec:** `docs/superpowers/specs/2026-11-18-unified-notebook-cleanup-design.md`

## Global Constraints

- Read the large notebook in targeted cells; do not print embedded outputs.
- The target notebook is untracked user work. Preserve its contents and all unrelated changes.
- Use `openai/gpt-6-luna` for implementation subagents and reviewers; this model was available when this plan was written. Recheck availability at execution time; ask the user if unavailable.
- Do not let parallel workers modify the same notebook. Workers produce proposals in separate temporary files; the integrator alone edits the notebook.
- Use the current cell 2 configuration, CSV input, and the current post-cell-12 feature order with `log_time`.
- Preserve cleaning rules, models, training settings, folds, metrics, intended quantum workflow, and source-data caveats.
- Do not add a project dictionary, install packages, commit changes, or overwrite existing result files without separate authorization.
- Apply `ste-writing-style` to notebook prose and comments. Do not claim full STE compliance without a complete dictionary audit.
- Full verification uses a fresh kernel and `RUN_QUANTUM = False`; it does not redefine the intended experiment.

## Review Focus

- A source CSV path relative to the notebooks directory must still resolve during the isolated execution (Task 4).
- A pre-existing output directory must not be overwritten by verification (Task 4).
- The final model feature list must use `log_time`, preserve ordering, and reject missing columns (Task 2).
- Failed or incomplete execution must not remove the stale-output warning or replace saved outputs (Task 4).
- Saved outputs must not show obsolete quantum results after a classical-only execution (Task 4).

---

### Task 1: Parallel proposals for cleanup and prose

**Files:**
- Read: `notebooks/Corrosion_Unified_22_Feature_Comparison.ipynb`
- Read: `pyproject.toml`
- Read: `docs/superpowers/specs/2026-11-18-unified-notebook-cleanup-design.md`
- Create: separate proposal files under `C:/Users/mhwkm/AppData/Local/Temp/opencode/`

**Interfaces:**
- Consumes: the current notebook, including its existing configuration and cell IDs.
- Produces: two UTF-8 proposals, each identifying original cell IDs and exact replacement source or suggested splits. Neither worker edits the notebook.

- [ ] **Step 1:** Launch two independent Luna subagents in parallel.
  - **Structure worker:** Propose the configuration cleanup, removal of the install cell, CSV-only setup, cell 4 splits, and one final feature definition. Search the entire notebook for each candidate unused variable; document all reads before proposing removal. Preserve side effects and code order.
  - **Prose worker:** Load `ste-writing-style`, inspect the notebook's Markdown and comments, and propose concise replacements and descriptive Markdown for the proposed cell 4 sections. Preserve all scientific caveats and the intended quantum comparison. Check for an existing STE dictionary; do not create one. List technical terms that need dictionary review.
- [ ] **Step 2:** Have each worker include a focused check: the structure proposal must identify the current 22-feature order and all uses of candidate removed variables; the prose proposal must identify every caveat and model description retained.
- [ ] **Step 3:** Review both proposals for overlap and conflicting source edits. Resolve prose placement and code boundaries before integration. Do not dispatch concurrent edits to the notebook.

### Task 2: Integrate structure and feature definitions

**Files:**
- Modify: `notebooks/Corrosion_Unified_22_Feature_Comparison.ipynb`
- Test: temporary validation script under `C:/Users/mhwkm/AppData/Local/Temp/opencode/`

**Interfaces:**
- Consumes: Task 1 structure proposal.
- Produces: one configuration block; `CHEM`, `CONDITIONS`, `ALL`, and `feature_frame(frame)` with the same runtime feature order as the original cell 12.

- [ ] **Step 1:** Write a temporary notebook-level regression check using `nbformat` and `ast`. Assert there is one `OUTPUT_DIR` assignment, no executable `pip install pennylane`, one definition of `feature_frame`, and one final definition each of `CHEM`, `CONDITIONS`, and `ALL`. Execute only the feature-definition statements with representative `ELEMENTS`, `GASES`, and a pandas frame: assert `ALL == ELEMENTS + ['temperature_c', 'log_time', 'flow_m_per_s'] + GASES`, length 22, uniqueness, correct selected column order, and an error for a missing column.
- [ ] **Step 2:** Run the check against the original notebook and confirm it fails on the duplicate configuration or feature definitions.
- [ ] **Step 3:** Integrate the structure proposal. Split cell 4 without changing statement order; retain the original cell 2 settings; remove the redundant configuration and install cell. Remove only variables proven unused. Consolidate feature definitions and validate the final list against `data.columns`.
- [ ] **Step 4:** Rerun the temporary regression check, `uv run --no-sync ruff check notebooks/Corrosion_Unified_22_Feature_Comparison.ipynb`, and `uv run --no-sync python -c \"import nbformat; n=nbformat.read('notebooks/Corrosion_Unified_22_Feature_Comparison.ipynb',as_version=4); nbformat.validate(n); print('valid')\"`. Expect all checks to pass.
- [ ] **Step 5:** Give a fresh Luna reviewer the changes and spec. Fix any confirmed violations before Task 4.

### Task 3: Integrate prose

**Files:**
- Modify: `notebooks/Corrosion_Unified_22_Feature_Comparison.ipynb`

**Interfaces:**
- Consumes: Task 1 prose proposal and Task 2 cell structure.
- Produces: concise Markdown and comments that describe the intended complete experiment.

- [ ] **Step 1:** Integrate the prose proposal, including descriptive Markdown for the split cleaning cells. Describe CSV input only. Keep all assumptions, censoring and temperature caveats, split limitations, and the quantum model's role.
- [ ] **Step 2:** Review sentence lengths, active voice, tense, noun stacks, and terminology against the STE skill references. Check that no text describes the non-quantum verification run as the intended experiment. Keep the existing stale-output warning until Task 4 succeeds.
- [ ] **Step 3:** Run Ruff and notebook validation using the commands in Task 2. Give a fresh Luna reviewer the prose and spec; fix confirmed omissions or scientific changes.

### Task 4: Execute and verify

**Files:**
- Modify: `notebooks/Corrosion_Unified_22_Feature_Comparison.ipynb` only after successful execution.
- Create: temporary notebook and result directory under `C:/Users/mhwkm/AppData/Local/Temp/opencode/`.

**Interfaces:**
- Consumes: integrated notebook from Tasks 2 and 3.
- Produces: refreshed saved outputs for all enabled non-quantum scenarios and models; original configuration and intended prose remain intact.

- [ ] **Step 1:** Confirm the configured CSV exists relative to `notebooks/`, and inspect its configured output destination. If the source or environment is unavailable, stop and report the blocker; keep the stale warning and existing outputs.
- [ ] **Step 2:** Create an execution copy with all prior outputs and execution counts cleared. Insert a temporary cell immediately after configuration to set `RUN_QUANTUM = False` and `OUTPUT_DIR` to a new, empty temporary directory. Run with `nbclient` and working directory `notebooks/`, with sufficient timeout for all enabled folds. Do not change any other flag or install dependencies.
- [ ] **Step 3:** Check that execution reached the last cell without errors. Check exported predictions and summaries in the temporary directory: each enabled scenario and each of `Random Forest`, `SVR`, `GPR`, `MLP`, and `Fusion ANN` appear; no `Fusion VQC` rows appear. Check fold coverage against the scenario definitions and check the source-row and feature invariants. Confirm pre-existing output files were not changed.
- [ ] **Step 4:** Only after every check passes, remove the injected cell and transfer outputs and execution counts from the execution copy to corresponding deliverable cells. Make sure no old quantum outputs survive. Remove the stale-output warning; retain text describing the intended quantum comparison. If the run fails or is incomplete, do not transfer outputs or remove the warning.
- [ ] **Step 5:** Run the Task 2 regression check, Ruff, and notebook validation again. Run `uv run --no-sync pytest`; report any unavailable tool or failure. Inspect the final notebook changes without printing image data. Have a fresh Luna reviewer check the full spec, especially feature order, output provenance, and no unintended model changes.
- [ ] **Step 6:** Report the verification commands and results, including that the full notebook run used `RUN_QUANTUM = False`. Do not claim quantum execution or full STE compliance.
