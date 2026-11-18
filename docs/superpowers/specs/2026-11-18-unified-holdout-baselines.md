# Unified comparison: isolated profiles and baselines

Extend `notebooks/Corrosion_Unified_22_Feature_Comparison.ipynb` without addressing unrelated notebook issues.

- Add a scenario that uses the existing composition-profile groups. Represent each group in the 16-element composition space, divide values by 100, rank groups by Euclidean distance to their nearest other profile, and separately hold out the five most isolated profiles. Display each selected profile, its isolation distance, and its test-row count.
- Add linear regression and random forest as baselines in the existing comparison. All enabled models use identical external splits, source features, targets, and reported metrics.
- Keep the existing scenarios and Colab-compatible notebook workflow. Inspect the large notebook in targeted sections.
