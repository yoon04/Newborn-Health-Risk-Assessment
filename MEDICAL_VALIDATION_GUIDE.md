# How to verify the newborn dashboard

## What the software checks establish

Passing tests establish that the implementation follows its stated rules. They do not establish clinical accuracy, calibrated disease probability or conformity of every project rule with a medical standard.

The current system is knowledge-based AI (Mamdani fuzzy inference plus explicit safety policy). It has no trained supervised ML model. Unexpected scores can result from a rule, component override or membership design; missing training is not automatically the cause. The numeric output cutoffs 30/70 and the maternal-age multiplier 0.25 are project heuristics, not guideline thresholds.

## Your APGAR-8 case

The latest 5-minute components are **Appearance 2 / Pulse 1 / Grimace 2 / Activity 2 / Respiration 1**. They total 8/10. Pulse 1 records heart rate below 100 bpm; respiration 1 records weak/irregular breathing. Both trigger the conservative heartbeat/breathing override before the reassuring total can cancel it.

- APGAR total: **8/10**, green total category.
- Immediate output memberships after override: **Low 0, Moderate 0, High 1**.
- Centroid of the clipped High output curve: **80.6/100**, High.
- Immediate action priority: **Urgent evaluation** of the recorded component findings.
- Repeat-scoring button: **not shown from this 5-minute total alone**, because repeat scoring is prompted by total below 7. This does not dismiss component concerns; a clinician can reassess clinically outside that scheduled scoring prompt.
- Heuristic rule clarity: **High**, because the output activation is entirely in one set. This is not a measured accuracy or clinically validated confidence. A hard-coded override produces clear rule activation without proving clinical validity.
- The complete 5-minute observation supplies inference; the 1-minute total is not averaged with it. These are historical recorded findings, not continuous monitoring of the baby's condition now.

The need to assess abnormal heart rate/breathing is supported by neonatal guidance. **Mapping either component score 1 to numeric High is the project's conservative policy**, not a statement that ACOG defines an APGAR-8 newborn as having a High numeric risk. APGAR respiration score 1 is broad; persistent respiratory distress, support and actual observations matter, and the app is not a resuscitation algorithm.

## Manual cases to test

Start a new assessment for every row. Use 39 weeks, 3200 g, maternal age 29, vaginal delivery, no delivery complication and no family history. Leave 1 minute blank unless testing the timeline specifically. Scores are A/P/G/A/R.

| 5-minute scores | Total | Expected immediate index/level | What to verify |
|---|---|---|---|
| 1/2/1/2/2 | 8 | 19.4 / Low | No heartbeat/breathing override; limited reflex notice remains |
| 2/1/2/2/1 | 8 | 80.6 / High | Both pulse and breathing reasons visible; total stays green |
| 2/0/2/2/2 | 8 | 80.6 / High | No-heartbeat reason visible |
| 0/2/2/2/2 | 8 | 19.4 / Low | Colour notice raises action priority without forcing numeric High |
| 1/2/1/2/2, complication Yes | 8 | 50.0 / Moderate | Complication affects fuzzy output; no heartbeat/breathing override |
| 1/1/1/1/2 | 6 | 80.6 / High | Pulse override and a +5-minute scoring button |

For a timeline test, record a synthetic 1-minute 2/0/2/2/2 and 5-minute 1/2/1/2/2 (both totals 8). The final immediate index must be Low from the latest complete scores, and the earlier pulse concern must remain documented. Reverse the component patterns and the final index must become High. The same total can hide different clinical components.

Birth example: **39 weeks, 3628.74 g, maternal age 29, complication Yes** gives about **52.6/100 Moderate**. The reported complication fully activates Moderate (1.00). The project's high-weight fuzzy set starts overlapping above 3600 g, so the complication-plus-weight concern weakly activates High (0.07185, displayed 0.07). This is fuzzy overlap; the recorded weight is not classified as low, and a weak High membership is not a diagnosis or a probability. This breakpoint also requires clinical review.

Run automated checks safely:

```powershell
.venv\Scripts\python.exe tests\run_tests.py
node tests/repeat_observation_ui.cjs
```

The isolated runner uses an in-memory database. Tests cover all 243 APGAR component combinations, all 15 APGAR-8 patterns with and without complication, latest-observation selection, birth boundaries, independent modules and saved/PDF explanations.

## Checking alignment with medical guidance

1. **Define the intended use.** Currently: an educational dashboard recording observations and prompting neonatal review. Do not claim diagnosis, individual outcome probability or independent treatment selection.
2. **Create a traceability table.** For every rule distinguish a clinical definition, a guideline-supported assessment concern and a project heuristic. Record the exact source, population, version/date and reviewer decision.
3. **Ask an OBGYN and a neonatal clinician to review independent case vignettes.** Include preterm infants, normal totals with abnormal components, maternal medications, resuscitation/support and complications of different types. The clinician writes expected concerns and actions before seeing the app output.
4. **Compare actions, not an invented standard risk index.** There is no guideline-ground-truth value of 52.6 or 80.6 to compare against. Record missed urgent findings, unnecessary alerts, disagreements and rationale; revise policy only after review. Keep numerical/category tests distinct from clinical action assessment.
5. **Evaluate against real outcome-labelled records.** Specify the endpoint and when the prediction is made. Report sensitivity, specificity, PPV, AUROC/AUPRC, reliability plots and Brier score with uncertainty intervals. Review missingness and performance by gestation, weight, sex, maternal age and relevant population groups where valid data exist.
6. **Require external/local validation.** U.S. records can support a research model but do not establish accuracy in your hospital/country. Review prospectively under clinical oversight before use in patient decisions. Record clinical sign-off and unresolved risks; do not fabricate approval.

| App behaviour | Evidence basis | Status |
|---|---|---|
| APGAR is five component scores at standard time points; repeat low 5-minute totals | AAP/ACOG APGAR guidance | Definitions/recording checked; timing and clinical context still matter |
| Reassuring APGAR total cannot replace direct clinical assessment | AAP/ACOG guidance | App shows separate component concerns |
| Assess abnormal heartbeat/breathing without waiting for APGAR | AHA/AAP neonatal guidance | Assessment concern supported; app does not prescribe resuscitation |
| Pulse/respiration below 2 forces numeric High | Conservative project policy | Requires neonatal review; not a guideline-defined index |
| Preterm, term subcategories, low-weight labels | WHO and NICHD definitions | Definition boundaries tested |
| Fuzzy membership ramps, 30/70 output cutoffs, 0.25 age multiplier, confidence grade | Project heuristics | Not clinically calibrated or outcome validated |

References:

- [AAP/ACOG: The Apgar Score (2015)](https://publications.aap.org/pediatrics/article/136/4/819/73821/The-Apgar-Score)
- [AHA/AAP: Neonatal resuscitation guidelines (2025)](https://publications.aap.org/pediatrics/article/157/1/e2025074352/205237/Part-5-Neonatal-Resuscitation-2025-American-Heart)
- [WHO preterm/low birth weight](https://www.who.int/teams/maternal-newborn-child-adolescent-health-and-ageing/newborn-health/preterm-and-low-birth-weight)
- [NICHD gestational terms](https://www.nichd.nih.gov/ncmhep/initiatives/know-your-terms/health-care-providers)

For the national project show, present the current system as an **explainable neonatal monitoring research prototype**, demonstrate the rule trace and safety cases, show actual measured validation results when available, and state what still needs clinician and local outcome review.
