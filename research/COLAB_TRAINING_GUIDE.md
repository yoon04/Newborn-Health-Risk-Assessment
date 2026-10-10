# Step-by-step Colab training plan

## What the CDC data can support

The verified 2024 natality dictionary provides NICU admission (AB_NICU), immediate assisted ventilation (AB_AVEN1), ventilation over 6 hours (AB_AVEN6), total APGAR at 5/10 minutes, gestational age, birth weight, maternal age and other birth-certificate variables. The 2024 layout does not provide individual APGAR components or the project's family-history assessment. Do not construct missing components from a total, infer a generic delivery complication from unrelated fields, or claim the dataset validates all three dashboard modules.

Use the first notebook for **retrospective classification of recorded NICU admission in a restricted singleton U.S. birth population**. There is no timestamp establishing that NICU admission happened after a five-minute assessment. Admission reflects practice/access as well as illness. It is not a general newborn-health outcome, a diagnosis, a genetic-risk label, or an admission-within-24-hours endpoint. A birth file does not itself provide infant mortality linkage; use the linked birth–infant-death product for that different question.

## Start here

1. Download this repository's **CDC_NICU_Baseline_Colab.ipynb** to your computer.
2. Open [Google Colab](https://colab.research.google.com/), choose **File → Upload notebook**, and select that file.
3. Use a Python CPU runtime. Run **Step 1** to install/import libraries; a GPU is unnecessary for this baseline.
4. Read the intended-use notes and [CDC data-user agreement](https://www.cdc.gov/nchs/data_access/vitalstatsonline.htm) linked from the portal. In **Step 2**, keep `DATA_MODE='download'` to obtain the official U.S. 2024 ZIP (about 232 MB compressed). If downloading fails, choose `upload`, download the U.S. ZIP yourself from the portal and upload it. Do not rename another year's file to pass the filename check.
5. Run **Step 3**. Check the parser self-test, row counts, excluded/missing records, sample size and outcome prevalence. It scans the whole ZIP and takes a uniform sample, avoiding the bias of using only the first records. The raw fixed-width file is streamed, not extracted.
6. Run **Step 4** to create disjoint 60% training / 20% validation / 20% test sets. This is same-year internal validation, not temporal or external validation.
7. Run **Step 5** to train a scaled Logistic Regression baseline with calibration fitted within training folds. The initial features are obstetric gestational age, birth weight and maternal age. The code excludes APGAR/intervention fields to avoid unverified event-order leakage.
8. Review **Step 6** validation results. Do not report accuracy alone: rare outcomes can make an always-No classifier look accurate. Examine AUROC, AUPRC versus prevalence, Brier score, the reliability curve, sensitivity and specificity. The example threshold 0.5 is not a clinical threshold.
9. Run **Step 7** once for the untouched test report and subgroup checks. Keep any model/threshold selection on training and validation data. After using the test results to redesign the model, obtain a new untouched test set. Add bootstrap uncertainty intervals before final research claims.
10. Run **Step 8** to download the model, calibration plot and model-card JSON. Save the notebook with outputs too. Bring the model card and metrics back for review before integrating anything into the dashboard.

## Scope and coding details

The parsed fixed-width positions were checked in the official 2024 dictionary:

| Field | CDC positions | Treatment |
|---|---|---|
| MAGER | 75–76 | 12 groups ages 10–12; 50 means 50+; use exact-coded 13–49 only |
| DPLURAL | 454 | Use singleton code 1 |
| OEGest_Comb | 499–500 | 99 is missing; restrict 20–45 weeks |
| DBWT | 504–507 | 9999 is missing; restrict 227–5999 g |
| AB_NICU | 519 | Y=1, N=0; exclude U/blank |
| F_AB_NIUC | 526 | NICU reporting flag (guide spelling); retain code 1 |

Exclusion counts can overlap. Scope restrictions define the study population and can introduce selection bias. The resulting model would not apply to twins, grouped ages, out-of-domain cases or excluded non-reporting records. Complete-case analysis is an initial baseline, not the final missing-data strategy.

## Next research stages

- Verify a separate year's dictionary before building temporal validation, for example older-year training and later-year testing. Do not assume fixed-width locations are unchanged.
- Compare Logistic Regression with a nonlinear model under the same held-out split; add clinically justified predictors only when available at the declared prediction time.
- For a hybrid model, use fuzzy memberships/rule outputs as features and compare against raw-feature baselines. A fuzzy feature is an engineered summary, not new evidence or a true target. The CDC layout does not have a direct equivalent of the dashboard's generic delivery-complication input; define a separate common-feature model rather than silently treating missing complications as No.
- Do not train on fuzzy Low/Moderate/High labels as if they were clinical truth; that would reproduce your own rules, not validate them.
- Add a model card, uncertainty intervals, independent clinician review, local external validation and approved action thresholds. Then add a separate labelled ML research result; keep component safety overrides and module-specific recommendations independent.

## What has been verified here

The notebook's Python syntax and fixed-width parser are checked against invented rows, including unknown labels, non-reporting flags, grouped ages, plural births and invalid gestation/weight codes. **No CDC population file has been trained on or evaluated in this workspace, and no measured ML accuracy is claimed.** You must run the notebook and retain its actual outputs to obtain performance results.

References:

- [CDC data portal](https://www.cdc.gov/nchs/data_access/vitalstatsonline.htm)
- [Official 2024 natality guide](https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Dataset_Documentation/DVS/natality/UserGuide2024.pdf)
- [Official U.S. 2024 ZIP](https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/DVS/natality/Nat2024us.zip)
- [scikit-learn calibration](https://scikit-learn.org/stable/modules/calibration.html)

For your show, demonstrate real notebook metrics with a prevalence-only baseline and a clear population/target, alongside explainable rules and the component safety cases. Do not claim hospital-readiness or a diagnostic accuracy until independent validation supports it.

## ZIP decompression errors in Step 3

The current notebook uses 7-Zip to stream the CDC archive. Python's built-in reader does not support every ZIP method; the previously suggested zipfile64/inflate64 backend also failed on this user's archive. Its synthetic round-trip test did not establish compatibility with the complete CDC file. Non-ASCII errors during that failed decompression do not establish the source's text encoding.

For an existing Colab session, run a new cell:

```python
!apt-get -qq update
!apt-get -qq install -y p7zip-full
```

Replace the entire failed parsing cell with `CDC_STEP3_RECOVERY.py` from this research folder, then run it. Keep the existing ZIP, settings and successful parser-definition cell; no runtime restart or new download is required. The code uses Python zipfile only to inspect the ZIP directory, and 7-Zip for actual decompression. Latin-1 preserves byte positions. The 7-Zip process must finish successfully (including its archive integrity checks) before the sample becomes the training dataframe. A parser interruption stops the extraction process. If 7-Zip reports a CRC/data error, do not train on a partial sample; check the download and retain the full error for diagnosis.

Local tests verify process cleanup, failed-extraction rejection, notebook syntax and fixed-width handling. The full 2024 archive has not been parsed in this workspace; successful completion and the resulting audit must still be reviewed in Colab.
