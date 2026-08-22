# Newborn Health Risk Assessment

A Flask web application that estimates newborn health risk using fuzzy logic from:
- APGAR score components
- Gestational age (birth week)
- Birth weight
- Maternal age
- Delivery type and reported delivery complications
- Simple known/unknown family disease history

The app generates a detailed result page with the APGAR breakdown, birth summary, module risk indices, overall assessment, confidence, contributing factors, fuzzy-rule traces, charts, and an educational-use reminder.

Important: This tool is educational only and is not a medical diagnosis.

## Features

- Multi-step form for complete newborn input
- APGAR score breakdown with per-component meaning
- Fuzzy logic inference for birth-factor risk
- Simple family-history input: Yes, No, or Unknown
- If a disease is known: disease name and who has it
- Family-history fuzzy indicator without an invented disease-specific probability
- Auto-generated charts:
  - APGAR membership chart
  - Gestational-age chart
  - Birth-weight chart
  - Maternal-age chart
  - Family-history indicator chart (when a disease is provided)
  - Final risk defuzzification chart
- Downloadable PDF matching the detailed results page, including APGAR details, birth information, module indices, family-history results, contributing factors, triggered rules, charts, and the final assessment

## Project Structure

```text
Newborn-Health-Risk-Assessment/
|-- app.py
|-- fuzzy_logic.py
|-- newborn_risk_assessment.py
|-- requiremens.txt
|-- synthetic_newborn_data.csv
|-- templates/
|   |-- form.html
|   `-- results.html
`-- static/
    `-- (generated chart images)
```

## Requirements

- Python 3.10+ recommended
- pip

Python packages used by the app:
- Flask
- numpy
- scipy
- matplotlib
- pandas

Note: The repo currently contains `requiremens.txt` (spelling as-is). The commands below use that filename.

## Step-by-Step Setup and Run

1. Clone the repository.

```bash
git clone <your-repo-url>
cd Newborn-Health-Risk-Assessment
```

2. Create and activate a virtual environment.

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Install dependencies.

```bash
pip install flask matplotlib -r requiremens.txt
```

4. Run the Flask app.

```bash
python app.py
```

5. Open in your browser.

```text
http://127.0.0.1:5000
```

6. Complete the 4 form steps in the UI:
- Step 1: APGAR components (Appearance, Pulse, Grimace, Activity, Respiration)
- Step 2: Birth info (week, weight + unit, maternal age, child gender, delivery type, delivery complication)
- Step 3: Family disease history (Yes, No, or Unknown)
- Step 4: Review and submit

7. Read results.
- Immediate Condition Risk Index (0-100): from APGAR + delivery complication
- Birth-Related Risk Index (0-100): from gestational age + weight + maternal age + delivery information
- Family-History Indicator (0-100): from known status and affected-relative information
- Overall Risk Index (0-100): hierarchical fuzzy inference across the three module indices
- Risk Level: Low, Moderate, or High
- Confidence: High, Moderate, or Low, based on input completeness, unknown family-history information, and fuzzy activation clarity
- The detailed result page shows module indices, contributing factors, important triggered rules, and charts
- Charts are saved/updated in `static/`
- Select **Download PDF Summary** on the results page to save the assessment report.
- PDF download tokens expire after one hour. For multi-worker or restarted deployments, set a shared `SECRET_KEY` environment variable so signed downloads remain valid.

## How Risk is Calculated (High Level)

1. APGAR component scores are summed (0 to 10).
2. Inputs are fuzzified into linguistic sets (for example: low/medium/high, preterm/term/postterm).
3. Separate fuzzy rule bases produce Immediate Condition Risk and Birth-Related Risk indices.
4. Simple family-history answers produce a Family-History Indicator. Disease names are stored for display but do not create disease-specific probabilities.
5. Each module produces a 0–100 index through fuzzy inference and defuzzification.
6. A final hierarchical fuzzy layer combines the three module indices using low/moderate/high rules. No fixed weighted-average formula is used.

## Input Guide

### APGAR inputs (0, 1, 2 each)
- Appearance
- Pulse
- Grimace
- Activity
- Respiration

### Birth inputs
- Gestational week: expected range in UI is 20 to 45
- Birth weight: accepts `g`, `kg`, or `lb` and converts internally to grams
- Maternal age: expected range in UI is 12 to 60
- Child gender: male or female
- Delivery type: vaginal, assisted, or Cesarean
- Delivery complication: yes or no; delivery type alone is not treated as a complication

### Family-history inputs
- Is there a known family disease? Yes, No, or Unknown
- If Yes: select from 20 common family-history diseases and conditions, or choose **Other disease / not listed**
- If Yes: who has it - Father, Mother, Both parents, Other family member, or Unknown

The user is not asked for inheritance mode, genotype, carrier status, chromosome type, or other technical genetic information.

## Generated Files

When you run assessments, the app writes/overwrites chart images in `static/`:
- `apgar_fuzzy.png`
- `week_fuzzy.png`
- `weight_fuzzy.png`
- `age_fuzzy.png`
- `genetic_risks.png` (family-history indicator when a disease is added)
- `final_risk.png`

## Troubleshooting

### 1) `ModuleNotFoundError: No module named 'flask'`
Install dependencies again:

```bash
pip install flask matplotlib -r requiremens.txt
```

### 2) App starts but no CSS/JS changes appear
Hard refresh browser cache and reload.

### 3) Charts are not updating
- Confirm the app is running from project root.
- Confirm the `static/` folder is writable.

### 4) Port already in use
Run Flask on a different port:

Windows PowerShell:

```powershell
$env:FLASK_APP = "app.py"
flask run --port 5001
```

macOS/Linux:

```bash
export FLASK_APP=app.py
flask run --port 5001
```

## Development Notes

- Main web entry: `app.py`
- Core fuzzy logic and plotting: `fuzzy_logic.py`
- Older CLI-style prototype: `newborn_risk_assessment.py`
- Templates: `templates/form.html` and `templates/results.html`

## Suggested Improvement (Optional)

Rename `requiremens.txt` to `requirements.txt` for standard tooling compatibility:

```bash
mv requiremens.txt requirements.txt
```

Then install with:

```bash
pip install -r requirements.txt
```

## Disclaimer

This project is intended for educational decision support. It does not replace professional medical evaluation, diagnosis, or treatment.
