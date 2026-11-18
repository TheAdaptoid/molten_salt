# Unified corrosion notebook cleanup

## Purpose

Make `notebooks/Corrosion_Unified_22_Feature_Comparison.ipynb` easier to read and run.
Keep the notebook self-contained.
Keep the scientific method and the intended full model comparison.

## Approach

Split the existing code into focused notebook cells.
Add Markdown cells that explain the main stages.
Keep the cleaning and model functions in the notebook.
Moving these functions into Python modules is an alternative.
That alternative adds files and changes the notebook workflow, so it is outside this cleanup.

## Scope

### Configuration and input

- Keep one configuration block near the start of the notebook.
- Use the settings from the current cell 2, including its `OUTPUT_DIR` selection.
- Remove the later `OUTPUT_DIR` assignment.
- Keep CSV as the only input format.
- Change setup instructions to name CSV only.
- Remove the PennyLane installation cell. `pyproject.toml` declares PennyLane.
- Keep the conditional PennyLane import and the quantum model.
- Remove unused setup variables only after a notebook-wide usage check.
- Do not remove a variable if a later cell or intended notebook workflow needs it.

### Cleaning and features

- Split the current cell 4 into focused code cells.
- Add short Markdown introductions for configuration of features, cleaning, data checks, and saved data.
- Keep the current execution order and dependencies.
- Keep the data-cleaning rules, validation, diagnostics, and output files.
- Combine the definitions in current cells 11 and 12.
- Define the final feature lists once.
- Use `log_time` in place of raw exposure time for every model.
- Check that the final list has 22 distinct features and that the cleaned data has each feature.
- Keep the same feature order that the models currently use after cell 12 runs.
- Keep the existing model preprocessing and fold boundaries.

### Notebook text

- Review Markdown and explanatory comments throughout the notebook.
- Apply the `ste-writing-style` skill to consolidate repeated text and make each section clear.
- Use short sentences, active voice, simple tenses, and consistent technical terms.
- Keep the details needed to interpret the experiment and reproduce it.
- Keep the caveats about censored values, the suspect temperature, holdouts, and scientific limitations.
- Describe the intended full comparison, including the quantum model.
- Do not present the temporary verification setting as the intended analysis.
- Use the available STE references and any applicable project dictionary.
- Record domain terms for review if no project dictionary exists.
- Do not claim full ASD-STE100 compliance without a complete dictionary audit.

## Verification and saved outputs

- Run Ruff on the notebook and validate its notebook format.
- Run the complete notebook from a fresh kernel with `RUN_QUANTUM = False`.
- Keep all other intended run settings unchanged for this verification.
- Do not overwrite existing result files without checking the destination.
- Use an isolated execution copy or temporary output location if necessary.
- Transfer refreshed cell outputs to the deliverable notebook without changing its intended configuration.
- Make sure no stale quantum results remain in saved outputs.
- Remove the old stale-output warning only after the full non-quantum run succeeds.
- Report that the verification run excluded the quantum model; this is not a change to the intended comparison.
- Check that the refreshed results cover the enabled scenarios and classical models.
- Compare the data rows, features, folds, and predictions with the existing behavior where practical.
- If execution fails or cannot finish, report the blocker and keep the stale-output warning.

## Out of scope

Do not change the model architectures, training settings, split definitions, targets, or scoring methods.
Do not correct source data without independent evidence.
Do not run the quantum model as part of this verification.
Do not add a project dictionary or change unrelated files as part of this cleanup.
