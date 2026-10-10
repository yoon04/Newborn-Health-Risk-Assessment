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
- User registration and login with Flask-Login sessions
- Private assessment history for each signed-in user
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
|-- extensions.py
|-- fuzzy_logic.py
|-- models.py
|-- newborn_risk_assessment.py
|-- persistence.py
|-- requirements.txt
|-- synthetic_newborn_data.csv
|-- migrations/
|-- templates/
|   |-- assessments.html
|   |-- assessment_detail.html
|   |-- form.html
|   |-- login.html
|   |-- register.html
|   `-- results.html
`-- static/
    `-- (generated chart images)
```

## Requirements

- Python 3.10+ recommended
- pip

Python packages used by the app:
- Flask
- Flask-Login
- Flask-SQLAlchemy
- Flask-Migrate
- psycopg (PostgreSQL driver)
- numpy
- scipy
- matplotlib
- pandas

The project now uses `requirements.txt`. The older misspelled `requiremens.txt` file was removed.

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
pip install -r requirements.txt
```

4. Run the Flask app.

```bash
python app.py
```

5. Open in your browser.

```text
http://127.0.0.1:5000
```

## PostgreSQL configuration

Create a project-local `.env` file from the example and replace the placeholder values:

```powershell
Copy-Item .env.example .env
notepad .env
```

The application automatically loads `.env` at startup, so you do not need to enter `DATABASE_URL` or `SECRET_KEY` in every terminal session. Explicit environment variables still take precedence over `.env`. The application accepts the simpler `postgresql://...` form as well and normalizes it for psycopg. Without `DATABASE_URL`, a local SQLite fallback keeps development and tests importable; production deployments should always configure PostgreSQL.

Create the database if needed:

```powershell
psql -U postgres -c "CREATE DATABASE newborn_health;"
```

## Authentication

Assessment creation and saved assessment history require an account. Use:

- `/register` to create an account with a name, email, and password
- `/login` to start a session
- `/logout` to end the session

Passwords are stored only as Werkzeug password hashes. New assessments are automatically associated with the signed-in user's `user_id`; name and email do not need to be entered again on the assessment form. Each user can view only their own assessment history and saved results.

## Database migrations

The initial migration is included in the repository. After configuring `DATABASE_URL`, apply it with:

```powershell
flask db upgrade
```

If you are setting up migrations in a copy that does not yet contain the `migrations/` directory, initialize and generate the schema first:

```powershell
flask db init
flask db migrate -m "Initial database schema"
flask db upgrade
```

For later model changes:

```powershell
flask db migrate -m "Describe the schema change"
flask db upgrade
```

The application does not call `db.create_all()` and does not delete or recreate tables automatically.

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
- Open `/assessments` to view saved assessments, or select **Assessment History** from a result.
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
pip install -r requirements.txt
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

## Disclaimer

This project is intended for educational decision support. It does not replace professional medical evaluation, diagnosis, or treatment.


### Priority 1: APGAR component safety overrides

Before adding the APGAR total, the server validates all five component scores as integers from 0 to 2 and checks heartbeat and breathing independently. Absent heartbeat (pulse 0), heart rate below 100 bpm (pulse 1), absent breathing (respiration 0), or weak/irregular breathing (respiration 1) activate an urgent alert, regardless of total. The form shows the alert even before every field is completed.

For these alerts, the immediate and final fuzzy output memberships become High only. Their displayed indices and charts therefore agree with the overridden classification; the indices are not outcome probabilities or calibrated severity measurements. Original fuzzy indices are retained in `unoverridden_immediate_risk_index` and `unoverridden_final_risk_index`, and `safety_override` records the triggering components and policy version. Alerts appear in recommendations, rule traces, stored result snapshots, and PDF reports. Birth and family modules still describe their own inputs.

This is a conservative educational safety policy, not a validated clinical prediction or resuscitation algorithm. Respiration 1 is broad, so it triggers direct professional assessment rather than a specific treatment instruction. Other component abnormalities remain in the APGAR breakdown and fuzzy assessment; absence of an override does not establish safety. Never delay clinical assessment or resuscitation to complete an APGAR score or this application.

Clinical reference: [2025 AHA/AAP neonatal resuscitation guidance](https://publications.aap.org/pediatrics/article/157/1/e2025074352/205237/Part-5-Neonatal-Resuscitation-2025-American-Heart). The existing fuzzy expert system is knowledge-based AI; this safety layer does not train or clinically validate a machine learning model.


### Priority 2: separate assessment domains (fuzzy-v3-separate)

New results show Immediate Condition, Birth-Related Monitoring, Family-History Follow-up, and Overall Triage. Family-history rules HR-04 and HR-07 have been removed from acute inference. Family history cannot change immediate/birth outputs, acute guidance, or triage. Its follow-up plan is separate and may suggest discussing genetic counselling or disease-specific screening with the clinician. Unknown history is displayed as Unknown, not as reassuring low risk.

Triage is an educational action policy: High immediate condition or a component safety override means Urgent evaluation; Moderate immediate condition or Moderate/High birth-related monitoring means Closer monitoring and professional review; otherwise Routine care and observation. High birth-related monitoring alone is not labelled an acute emergency. Symptoms still require direct clinical assessment regardless of these classifications.

The old overall index fields remain internally for schema/backward compatibility, but new result pages, saved details, history rows and PDFs do not present a combined Overall Risk Index. Separate module indices are heuristic fuzzy indices, not disease probabilities. New saved snapshots include the triage and follow-up plan and use algorithm version `fuzzy-v3-separate`. Older saved results are labelled legacy and remain unchanged; downloading their PDF recomputes using the current algorithm, so it can differ from the original snapshot.

Reference: [CDC: Family Health History and Your Child](https://www.cdc.gov/family-health-history/family-health-history-and-you/family-health-history-and-your-child.html).


### Colour notice and maternal-age review (fuzzy-v3.1-colour-age)

Appearance 0 (blue/pale all over) now generates a separate direct-assessment notice before APGAR summation. It is visible as soon as selected on the form, in results, saved snapshots, and PDF reports. The notice sets Overall Triage to Urgent evaluation independently of the numeric immediate index; it does not force fuzzy High memberships or prescribe oxygen/treatment. Heartbeat and breathing overrides still take precedence. Colour alone cannot establish oxygenation, and a reassuring total cannot dismiss the notice. Appearance 1 (blue hands/feet only) does not trigger this notice.

Maternal-age memberships are heuristic context curves: very-young (-0.1, 0, 15, 18), adolescent (15, 18, 18, 20), typical (18, 20, 35, 40), older (35, 40, 45, 50), very-advanced (40, 45, 60, 60.1). These are trapezoid parameters, with overlapping ramps; age 20–34 has only typical membership. Age 23 no longer activates BR-13. The ramps remain unvalidated project assumptions, not clinical cut-offs or calibrated probabilities. Charts use the same membership function as inference to avoid drift.

For the reported example (APGAR 0/2/1/2/2, 38 weeks, 3200 g, age 23, no complication), immediate index stays 28.6, birth monitoring becomes Low (19.4), and the separate colour notice sets triage to Urgent evaluation. Family-history follow-up remains separate. Older stored snapshots are unchanged; charts are regenerated only for snapshots using this policy, and saved PDF downloads identify recalculation with the current policy.

Sources: [WHO adolescent pregnancy](https://www.who.int/en/news-room/fact-sheets/detail/adolescent-pregnancy), [ACOG pregnancy at age 35 or older](https://www.acog.org/clinical/clinical-guidance/obstetric-care-consensus/articles/2022/08/pregnancy-at-age-35-years-or-older), [AAP APGAR limitations](https://publications.aap.org/pediatrics/article/136/4/819/73821/The-Apgar-Score).


### Timed APGAR observations (fuzzy-v4-timed-apgar)

The web form has a 1-minute column (optional when not recorded), a required 5-minute column, and optional fresh observations at 10/15/20 minutes. Birth and family inputs are entered once. Each recorded time point requires all five components and includes support/resuscitation status (none, provided, or unknown). Blank optional observations are displayed as Not recorded; no copying, interpolation, or averaging occurs. This is documentation of clinical observations, not an automated monitor or a delivery-room treatment algorithm.

The latest recorded observation supplies the immediate-condition fuzzy input and component notices; every earlier total, component set, alert, and support status remains in the timeline. The result and PDF show the reference minute, change from 1 minute to the latest recording, and a reminder that historical observations do not establish the baby's current condition or resolve earlier concerns. Birth-related monitoring and family follow-up remain separate.

When the 5-minute status is not green, the form and report suggest fresh repeat observations. The ACOG/AAP guideline criterion is total below 7 at 5 minutes; this app also suggests clinician reassessment when component notices make the status non-green despite a higher total. Grimace/activity 0 generate urgent direct-assessment notices; score 1 generates professional-reassessment notices; score 2 generates no additional notice. These notices affect triage without forcing the numeric fuzzy output to High. Heartbeat/breathing overrides retain precedence. Exact software notice and inference rules remain heuristic and require clinical review.

Timed observations are stored in the existing JSON result snapshot and raw input fields; no database schema migration is needed. Saved PDF recalculation reuses the full timeline. Legacy single-observation submissions remain supported as untimed records, and older snapshots are not relabelled as timed. Run a new assessment to use the new form.

Reference: [ACOG: The Apgar Score](https://www.acog.org/clinical/clinical-guidance/committee-opinion/articles/2015/10/the-apgar-score).


### Staff UI correction (fuzzy-v4.1-total-status)

The compact component table now shows matching 1-minute and 5-minute columns. APGAR total colour reflects only the numeric total: 7–10 green, 4–6 amber, 0–3 red. Safety overrides and component review notices are separate; they do not recolour the total or trigger scheduled repeat scoring by themselves. The prior “non-green” repeat rule is superseded: only a 5-minute total below 7 indicates repeat scoring. Once a recorded repeat reaches at least 7, the report describes recorded improvement rather than prompting another scheduled repeat; current component concerns still require clinical assessment. At 20 minutes the recording window is complete.

The result and PDF explain that the latest complete recorded component set supplies the APGAR sum used by immediate fuzzy inference, alongside delivery complication. Previous observations supply history and trend. Numeric risk indices and triage are outputs; they are not entered back as APGAR inputs. This remains an educational decision-support prototype requiring clinical validation before routine clinical use.


### Immediate-condition results by time (fuzzy-v5-module-actions)

Each recorded APGAR observation has a separate result card: nominal time after birth, five components, APGAR total, immediate fuzzy index/level, support status, component concerns and recommended action. The latest complete observation is marked as the inference reference. Additional observations are shown only if recorded; empty 10/15/20-minute slots are not printed in normal results or PDF. On the form, additional rows are hidden unless the 5-minute total is below 7, a repeat has already been entered, or the clinician explicitly adds an observation.

The assessment path no longer performs hierarchical combined-risk inference or creates a combined-risk chart. It returns three separate module action plans. Immediate recommendations depend only on immediate inputs and component safety checks; birth monitoring and family follow-up have their own recommendations. For compatibility with existing non-null database columns and older clients, `overall_risk_index`, `risk_level` and `final_risk_levels` mirror the immediate module, while `overall_triage` mirrors the immediate action label; they are not combined results and are not displayed as an overall score. Existing schemas require no migration. New code should use module fields and `module_actions`.

Per-time outputs are heuristic decision-support results, not trained outcome predictions. Support status is documented for clinical interpretation; it does not yet have a validated numeric adjustment. Machine learning is deferred until outcome-labelled data, prediction time and clinical validation are defined.


### Shared staff dashboard and concise immediate summary

Authentication is removed from the dashboard workflow. Staff can create assessments, view shared history, open any saved record and download PDFs without an account. New assessments have a nullable owner; existing user-linked records remain accessible in shared history. Old login/register/logout URLs redirect to the dashboard without creating accounts; existing user records are retained for database compatibility. No schema migration is required. Access to this deployment now grants access to its assessment data, so the intended deployment is a staff-accessible local/internal environment.

All observation inputs now have clinical option descriptions and matching total rings for 1, 5, 10, 15 and 20 minutes. Repeat inputs remain conditional. The final immediate module presents its graph explanation followed by one paragraph covering the observations recorded, latest inference reference, final immediate index and recommended action. The complete timeline is retained in the saved snapshot; the final results and PDF use a concise summary rather than repeating every observation card.


### APGAR dashboard presentation

Results and saved assessments use a wider responsive layout. Each module graph has a short caption; the immediate module separates recorded facts and its final index, care concerns, and recommended actions. The latest complete observation remains the fuzzy inference input, without averaging timed scores.

Additional inputs start hidden. A complete 5-minute APGAR below 7 enables **+ 5 minutes**, which opens only the 10-minute observation. Complete that observation before adding 15 minutes, then 20 minutes if the preceding total remains below 7. A repeat total of 7 or more stops further prompts; recorded observations and component concerns remain available. This form records fresh observations and does not schedule or perform clinical reassessment automatically.

UI control regression check: `node tests/repeat_observation_ui.cjs`.


### Birth-related monitoring explanations (v6)

The birth module now presents recorded findings, monitoring concerns and recommended actions separately in new results, saved assessments and PDFs. Its expandable explanation shows input memberships and active rule strengths; the centroid is a heuristic index, not a probability. Clinical birth categories are separate from fuzzy sets, and no SGA/LGA classification is inferred without a growth reference.

Maternal-age Moderate rules use an explicit project scale of 0.25; age alone no longer activates High or the complication-plus-High rule. The redundant reassuring age rule was removed so a reported complication cannot simultaneously activate a reassuring birth rule. Very-low-weight membership now has a left shoulder, correcting a small reversal around 940–1000 g. Exact categories can trigger a monitoring review even when fuzzy overlap yields a lower numeric level.

The policy and saved algorithm version are `fuzzy-v6-birth-monitoring`. These changes have software regression checks, but are awaiting neonatal clinical review and outcome validation. See [birth validation cases](BIRTH_VALIDATION_CASES.md) for examples and reference sources. Run the full suite with `.venv\Scripts\python.exe tests\run_tests.py`; the runner uses an isolated in-memory SQLite database before importing the app.


Birth results now show one concise paragraph of recorded findings and the final index, followed by a reason generated from the strongest active rule in each output group. Monitoring concerns and actions follow separately. Detailed input explanations remain expandable. A High rule activation does not automatically make the final label High: the label follows the centroid of all aggregated outputs. This limited screen omits examination, vital signs, feeding and maternal/infection detail and cannot estimate an individual baby's real disease probability. Adding inputs requires a defined outcome, clinician-designed pathways and outcome-labelled validation, rather than assuming more fields establish accuracy.


### Fact-based results, APGAR-8 verification and research training

Birth findings and result reasons are displayed line by line. Immediate facts explain when a heartbeat/breathing component safety override sets High despite a reassuring APGAR total. The confidence label is displayed as **Rule clarity (heuristic)** because it reflects activation separation, not clinical accuracy or calibrated uncertainty. Numeric rules are unchanged by this presentation update.

See [medical/software validation guide](MEDICAL_VALIDATION_GUIDE.md) for cases and clinician-review steps, and [Colab training guide](research/COLAB_TRAINING_GUIDE.md) with the [research notebook](research/CDC_NICU_Baseline_Colab.ipynb). The notebook targets recorded NICU admission in CDC 2024 singleton U.S. birth records; it is not deployed and has not been trained/evaluated here. CDC aggregate APGAR totals cannot validate individual component safety checks. The current dashboard remains a research prototype awaiting clinical and local outcome validation.
