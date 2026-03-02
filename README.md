# Newborn Health Risk Assessment

A Flask web application that estimates newborn health risk using fuzzy logic from:
- APGAR score components
- Gestational age (birth week)
- Birth weight
- Maternal age
- Delivery type
- Optional inherited family conditions

The app generates a detailed result page with:
- Birth-factor risk score
- Inherited risk score
- Combined final risk score
- Visual charts saved in `static/`

Important: This tool is educational only and is not a medical diagnosis.

## Features

- Multi-step form for complete newborn input
- APGAR score breakdown with per-component meaning
- Fuzzy logic inference for birth-factor risk
- Genetic history modeling with multiple inheritance modes
- X-linked logic adjustment by child gender and parent status
- Auto-generated charts:
  - APGAR membership chart
  - Gestational-age chart
  - Birth-weight chart
  - Maternal-age chart
  - Genetic risk chart (when diseases are provided)
  - Final risk defuzzification chart

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
- Step 2: Birth info (week, weight + unit, maternal age, child gender, delivery type)
- Step 3: Family genetic conditions (optional)
- Step 4: Review and submit

7. Read results.
- Birth Risk Score (%): from APGAR + week + weight + age + delivery
- Inherited Risk (%): from selected disease inheritance modes
- Final Risk (%): weighted combination
- Charts are saved/updated in `static/`

## How Risk is Calculated (High Level)

1. APGAR component scores are summed (0 to 10).
2. Inputs are fuzzified into linguistic sets (for example: low/medium/high, preterm/term/postterm).
3. Rule-based fuzzy inference estimates birth-factor risk levels.
4. Genetic conditions are processed with selected inheritance modes.
5. X-linked selections further adjust inherited probability by child gender + parent side/status.
6. Defuzzification converts fuzzy outputs into percentages.
7. Final risk is computed as:

```text
final_risk = 0.7 * birth_factor_risk + 0.3 * inherited_risk
```

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
- Delivery type: vaginal or C-section

### Genetic inputs (optional)
For each condition:
- Disease name (from common list or custom)
- Inheritance mode
- If X-linked is selected, parent side and status are required

## Inheritance Modes Supported

- dominant_both_parents
- dominant_one_parent
- dominant_none_parents_grandparent_yes
- recessive_both_parents_carriers
- recessive_one_parent_carrier
- recessive_none_parents_grandparent_yes
- xlinked
- complex
- unknown

(Displayed labels and explanations come from `INHERITANCE_MODES` in `fuzzy_logic.py`.)

## Generated Files

When you run assessments, the app writes/overwrites chart images in `static/`:
- `apgar_fuzzy.png`
- `week_fuzzy.png`
- `weight_fuzzy.png`
- `age_fuzzy.png`
- `genetic_risks.png` (only when genetic conditions are added)
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
