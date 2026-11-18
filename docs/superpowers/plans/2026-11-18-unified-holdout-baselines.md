# Unified Holdout and Baselines Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add five isolated composition-profile holdouts and two baseline regressors to the unified notebook.

**Architecture:** Extend the existing scenario dictionary and benchmark dispatch rather than duplicating the evaluation. Keep preprocessing and fitting inside each training fold, and produce predictions in the same original units as existing models.

**Tech Stack:** Jupyter/Colab, pandas, NumPy, scikit-learn.

**Spec:** `docs/superpowers/specs/2026-11-18-unified-holdout-baselines.md`

## Global Constraints

- Modify only the unified notebook for functionality; do not fix unrelated issues.
- Preserve existing scenarios, their splits, and all 22 source features.
- Select five existing composition-profile groups using 16-element nearest-neighbor Euclidean distance after division by 100.
- Test each selected group separately and display its identity, isolation distance, and row count.
- Use the same outer splits, target, metrics, and result exports for every enabled model.
- Keep code usable in Google Colab and inspect notebook cells in targeted chunks.

## Review Focus

- Profiles with repeated rows or multiple unrounded compositions: represent a profile by the mean of its member composition vectors.
- Equal isolation distances: break ties deterministically by profile identifier.
- Fewer than five profiles: raise a clear error when the new scenario is enabled.
- One-row test profiles: preserve the existing undefined per-fold R² behavior.
- Original scenarios cover all rows; the new scenario covers only selected profiles and must not trigger the full-coverage assertion.

## File Structure

- Modify `notebooks/Corrosion_Unified_22_Feature_Comparison.ipynb`: scenario construction, baseline predictors, comparison dispatch, and relevant explanatory markdown.
- Use focused temporary verification scripts if needed; do not introduce runtime dependencies or require teammates to copy extra files.

### Task 1: Isolated composition-profile scenario

**Files:** Modify `notebooks/Corrosion_Unified_22_Feature_Comparison.ipynb`, scenario configuration and evaluation-plan cells.

**Interfaces:**
- Consumes `data`, `ELEMENTS`, and `data.composition_profile`.
- Produces `SCENARIOS['isolated_composition_top5']` as five `(train_indices, test_indices)` pairs and a displayed selection table with profile, nearest-profile distance, and row count.

- [ ] Write a focused failing test using six synthetic profiles, including repeated rows and two different raw compositions in one rounded profile. Verify group means, distances in fraction units, descending nearest-neighbor ranking, deterministic profile-ID tie breaks, five disjoint test groups, and complementary train indices.
- [ ] Verify fewer than five profiles raises a clear error, a single-row selected group is permitted, and original scenario coverage remains unchanged.
- [ ] Run the tests and confirm they fail because the scenario does not exist.
- [ ] Implement the new scenario using per-group means, with a separate enable flag. Treat it as composition-grouped in `internal_cv` so nested kernel tuning remains training-only and group-aware.
- [ ] Replace only the incompatible full-coverage assertion for this scenario with checks for disjoint test groups and complementary train/test indices. Update scenario descriptions to distinguish selected holdouts from full-coverage CV.
- [ ] Rerun the focused tests and confirm they pass.

### Task 2: Baseline models in the shared benchmark

**Files:** Modify `notebooks/Corrosion_Unified_22_Feature_Comparison.ipynb`, imports, model definitions, benchmark dispatch, and model descriptions.

**Interfaces:**
- Consumes `feature_frame`, `SEED`, and train/test frames from `run_benchmark`.
- Produces baseline predictions for `Linear Regression` and `Random Forest`, alongside the existing models, in the existing result tables and exports.

- [ ] Write a focused failing test on synthetic data that runs both baseline predictors, checks one finite nonnegative prediction per test row, checks deterministic random-forest results, and verifies each baseline is called on the same train/test indices as other enabled models.
- [ ] Test that baseline preprocessing is fit only on the training frame, both models use all 22 inputs, and one-row test folds produce undefined fold R² rather than failing.
- [ ] Run the tests and confirm they fail before implementation.
- [ ] Add scikit-learn linear regression and a seeded random forest with explicit default-compatible settings. Fit the same log1p target as the existing classical predictors and convert predictions back with their existing clipping convention; keep preprocessing inside each training fold.
- [ ] Register both baselines in `run_benchmark` and update model-count and scenario descriptions without changing unrelated behavior.
- [ ] Rerun the focused tests and confirm they pass.

### Task 3: Integrated verification

**Files:** Verify `notebooks/Corrosion_Unified_22_Feature_Comparison.ipynb`.

- [ ] Validate notebook JSON and compile changed Python cells, excluding notebook magics.
- [ ] Run a small representative benchmark with quantum and expensive tuning disabled where the available environment permits; verify five selected splits, seven models when quantum is enabled (six otherwise), matching test rows across models, and populated results.
- [ ] Inspect the notebook diff for unrelated changes, stale output implications, and Colab compatibility. Report any checks that cannot be run and do not claim saved outputs were regenerated unless they were.
