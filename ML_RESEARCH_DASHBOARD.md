# NICU research dashboard integration

The dashboard adds a separate frozen V2 probability panel alongside the existing three fuzzy modules. The probability predicts NICU admission recorded on U.S. birth certificates. It is not an acute-danger score, a validated local prediction, or a treatment recommendation. The result is not combined with fuzzy indices and cannot change module actions or APGAR alerts.

## Run

Use the existing project virtual environment:

```powershell
.venv\Scripts\python.exe -m pip install -r requirements-ml.txt
.venv\Scripts\python.exe app.py
```

Restart an already running Flask process after dependency installation. Open http://127.0.0.1:5000/ and choose New Assessment. No Colab connection or training is needed for inference.

## Inputs and limits

Birth plurality defaults to Unknown. Confirm Singleton to enable the research estimate. Multiple or unknown births produce Estimate unavailable. Bounds: recorded gestation 20–45 weeks, weight 227–5999 g, maternal age 13–49 whole years. Gestation is encoded for ML in completed weeks (floor): 38.5 becomes 38, not 39. The original clinical observation and fuzzy input remain unchanged. The UI and PDF disclose the recorded and encoded values. This matches CDC obstetric-estimate reporting: https://www.cdc.gov/nchs/nvss/facility-worksheets-guide/30.htm . This input-format correction does not retrain or clinically validate the model. Age 12 and 50 represent grouped/top-coded CDC ages and are excluded.

## Demonstration cases

- Singleton, 39 weeks, 3200 g, age 29: available probability approximately 3.5%; research label and evaluation evidence shown.
- Same birth inputs, pulse 1 and respiration 1: same ML probability; immediate module still has High component safety override and its actions.
- Multiple or Unknown birth: no probability; the module results remain available.
- Singleton, 38.5 weeks: ML uses 38 completed weeks; actual 38.5 remains the clinical and fuzzy input. Prediction matches otherwise-identical 38-week model input.
- Singleton, weight 200 g or maternal age 50: ML unavailable due to study scope.

The 0.10 threshold is documented only as a research comparison and never becomes a dashboard clinical risk label. Historical 2023 evaluation: 120,000 records; AUROC 0.782, AUPRC 0.514, Brier 0.0556; sensitivity at 0.10 was 53.8% overall and 10.2% for term births. No individual uncertainty interval is shown. Low probability cannot establish safety.

## Artifacts and replay

research_models/nicu_v2 contains the user's frozen model, card, 2023 evaluation report, and SHA-256 manifest. The loader accepts only this bundled local artifact, verifies checksums and feature/class order, and requires the export's matching numpy/pandas/scikit-learn/joblib versions before loading. Joblib artifacts are executable serialization; only the user's trusted export is bundled, with no model-upload route.

A missing dependency, changed artifact, unsupported input, or inference error yields an unavailable panel; fuzzy calculation continues. New assessments persist the exact ML result and scope in the existing JSON snapshot. Saved assessment views and PDFs retain that result; legacy assessments show no recorded ML result rather than silently recomputing it. No database migration is needed for plurality because it is stored in raw_inputs and result_snapshot.

Actions remain project rule summaries requiring clinician review. Next evidence work: neonatal/OBGYN review, local cases with clear prediction/outcome timestamps, subgroup calibration and uncertainty, and a separate evaluation set for changes informed by prior evaluation results.

## Twin names and separate assessment flow

Birth plurality appears before name fields. Selecting Twins reveals Twin 1 and Twin 2 names, plus a selector identifying the baby whose APGAR observations, weight and findings belong to the current form. Both names are validated. Each record stores the assessed baby's name, both twin names and the selected twin number; the second name alone does not create a clinical assessment. Results/history/PDF explicitly identify the assessed twin. The result offers a link to begin the other twin's separate form, prefilled only with names, plurality, maternal age and gestation. APGAR, weight, gender, complications and family entries are not copied by this link. Twins remain outside the singleton-trained ML model scope. Other multiple births can still be recorded individually.

Tests: tests/run_tests.py includes twin input, identity/persistence/report and fresh-form checks. tests/twin_names_ui.cjs verifies hidden/disabled/required state changes.
