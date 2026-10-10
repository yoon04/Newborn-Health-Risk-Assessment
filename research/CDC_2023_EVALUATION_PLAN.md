# Frozen V2 historical evaluation

Training/development: CDC 2024. Evaluation: CDC 2023, restricted singleton population, same three features and NICU reporting criteria. This is backward-year historical transportability, not forward prediction or local hospital validation. Repeated mothers across years cannot be ruled out in these public files.

The 2023 guide was independently inspected: MAGER 75–76 (pages 10–11); DPLURAL 454 (page 31); OEGest_Comb 499–500 and DBWT 504–507 (page 33); AB_NICU 519 (page 34); F_AB_NIUC 526 (page 35). Guide: https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Dataset_Documentation/DVS/natality/UserGuide2023.pdf

Use frozen V2, feature order gestational_age_weeks/birth_weight_g/maternal_age, threshold 0.10 for the documented research comparison. No fitting, recalibration or threshold selection on 2023. Sample uniformly across all eligible rows, 120,000 records, seed 42. Retain SHA-256, overlapping exclusion counts, versions, metrics, calibration and subgroup outputs. Future changes informed by these results require another evaluation dataset.

The preparation script is self-contained with respect to the parser and 7-Zip helper, preserves 2024 variable names, and uses df_2023/audit_2023. Local syntax and invented-row parser checks do not constitute full population-file validation.
