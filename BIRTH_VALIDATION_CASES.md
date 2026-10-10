# Birth-related monitoring validation cases

These synthetic cases verify the software policy `fuzzy-v6-birth-monitoring`; they do not establish clinical accuracy. All displayed indices are fuzzy centroids, not percentages of disease or admission probability.

For each case: start a new assessment, leave the optional 1-minute observation blank, enter **2/2/2/2/2 at 5 minutes**, support **Unknown / not recorded**, gender **male**, vaginal delivery and family history **No**. Use the birth inputs below and select weight unit **g**.

| Case | Gestation (weeks) | Weight (g) | Maternal age | Complication | Expected birth index / level | Expected monitoring priority |
|---|---|---|---|---|---|---|
| Full-term reference | 39 | 3200 | 28 | No | 19.4 / Low | Routine birth follow-up |
| Preterm with reference-range weight | 36 | 3200 | 28 | No | 35.4 / Moderate | Monitoring plan |
| Low weight at full term | 39 | 2400 | 28 | No | 33.4 / Moderate | Monitoring plan |
| Combined preterm and low weight | 34 | 2000 | 28 | No | 69.0 / Moderate | Monitoring plan |
| Very preterm and very low weight | 30 | 1300 | 28 | No | 71.4 / High | Prompt neonatal monitoring review |
| Very low-weight review despite Moderate index | 39 | 1499 | 28 | No | 63.7 / Moderate | Prompt neonatal monitoring review |
| Older maternal-age context only | 39 | 3200 | 48 | No | 25.1 / Low | Routine birth follow-up |
| Reported delivery complication | 39 | 3200 | 28 | Yes | 50.0 / Moderate | Monitoring plan |
| Clinical boundary: early term, not low weight | 37 | 2500 | 28 | No | 34.4 / Moderate | Monitoring plan |
| Post-term with higher weight | 42 | 4200 | 28 | No | 64.1 / Moderate | Monitoring plan |

## What to check in the UI

- The birth module has separate **Recorded birth findings and final result**, **Monitoring concerns**, and **Recommended monitoring actions** sections. Its graph caption remains short.
- Expand **How the birth monitoring index was calculated**. Verify the four input membership groups and active birth rules, including their activation strengths and output levels.
- Full-term reference: no physical birth-monitoring flag, routine birth follow-up.
- Preterm/low-weight cases: the concern and monitoring pathway remain visible regardless of the scalar fuzzy level. At 1499 g, the model can be Moderate while the categorical finding still prompts neonatal review.
- Maternal age 48 with otherwise reference inputs: a limited age-context contribution, no standalone High rule, no treatment or disease diagnosis based on age. Compare it with maternal age 28.
- A reported complication should disable the reassuring birth rule. The binary input does not identify the complication's nature or severity; the UI asks staff to clarify it.
- The exact clinical categories are displayed separately from fuzzy membership names. At 37 weeks the category is Early term, despite some overlap with the fuzzy preterm set. At 2500 g the category is Not low birth weight, despite some fuzzy low-weight membership.
- Saved assessments retain the explanations; PDFs include the findings, concerns and monitoring actions. Earlier-policy snapshots stay unchanged and are labelled as earlier policy; rerun assessment for the current result.
- Changing birth weight or gestational age alone must not change the immediate APGAR or family-history index. Delivery complication is a shared input used independently in the immediate and birth modules.

## Boundary and consistency checks

Compare 36.5 and 37 weeks, 2499 and 2500 g, 1499 and 1500 g, and maternal ages 34, 35, 36, 40 and 48. Clinical labels can change at a defined threshold while the overlapping fuzzy index changes gradually. The tests check all membership knots, valid-range coverage and monotonic improvement in preterm gestation and low birth weight. No input is silently assigned a zero index because of a missing active rule.

The original low-weight overlap had a slight reversal around 940–1000 g. The nested very-low-weight shoulder now keeps the High activation stable across this range; improving weight cannot raise the birth index in the tested low-weight range.

## Policy decisions awaiting neonatal review

- The maternal-age rule multiplier **0.25** is an explicit project heuristic, not a coefficient from a clinical guideline or trained model. It scales only contextual Moderate activation; age cannot activate a High birth rule or the complication/High interaction.
- The fuzzy membership breakpoints, the **4000 g** higher-weight review threshold, monitoring priorities and wording need neonatal clinical review and outcome validation before clinical deployment.
- Birth weight alone does not classify small/large for gestational age. A suitable gestational-age/sex growth reference is not yet included.
- This module prompts a clinician to determine monitoring under local protocols; it does not prescribe treatment, a screening frequency or admission.

Clinical references for terminology and review context:

- [WHO preterm and low-birth-weight definitions](https://www.who.int/teams/maternal-newborn-child-adolescent-health-and-ageing/newborn-health/preterm-and-low-birth-weight)
- [NICHD gestational-age terms for clinicians](https://www.nichd.nih.gov/ncmhep/initiatives/know-your-terms/health-care-providers)
- [WHO recommendations for care of preterm or low-birth-weight infants](https://www.who.int/publications/i/item/9789240058262/)
- [ACOG/SMFM maternal age and pregnancy outcomes](https://www.acog.org/clinical/clinical-guidance/obstetric-care-consensus/articles/2022/08/pregnancy-at-age-35-years-or-older)

Run the isolated regression suite from the project folder:

```powershell
.venv\Scripts\python.exe tests\run_tests.py
node tests/repeat_observation_ui.cjs
```
