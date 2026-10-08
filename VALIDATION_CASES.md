# Dashboard validation examples

These synthetic cases test software behaviour; they are not clinical validation or patient care instructions.

Use the same birth inputs for every case: gestational age **39 weeks**, weight **3200 g** (select g), maternal age **28**, gender **male**, vaginal delivery, **no** delivery complication, family history **no**. Leave the optional 1-minute observation blank, and use support **Unknown / not recorded**. Start a new assessment for each case.

Scores below are ordered **Appearance / Pulse / Grimace (reflex response) / Activity (muscle tone) / Respiration**. Enter each value in its corresponding dropdown.

| Case | 5-minute components (total) | 10-minute components (total) | Expected final immediate index | Expected action priority | Expected repeat controls |
|---|---|---|---|---|---|
| Reassuring | 1/2/2/2/2 (9/10) | Leave blank | 19.4/100 — Low | Routine care and observation | No repeat button |
| Repeat and recovery | 1/1/1/1/2 (6/10) | 2/2/2/2/2 (10/10) | 19.4/100 — Low | Routine care and observation | Click + 5 minutes to open 10 minutes; no further repeat button |
| Repeat still below 7 | 1/1/1/1/2 (6/10) | 1/1/1/1/2 (6/10) | 80.6/100 — High | Urgent evaluation | Click + 5 minutes to open 10 minutes; 15-minute button appears |
| Exactly 7 | 1/2/1/1/2 (7/10) | Leave blank | 28.6/100 — Low | Closer monitoring and professional review | No repeat button |
| Green total with absent pulse | 2/0/2/2/2 (8/10) | Leave blank | 80.6/100 — High | Urgent evaluation | No repeat button |
| Colour concern | 0/2/2/2/2 (8/10) | Leave blank | 19.4/100 — Low | Urgent evaluation | No repeat button |
| Limp tone | 1/2/2/0/2 (7/10) | Leave blank | 28.6/100 — Low | Urgent evaluation | No repeat button |
| No reflex response | 1/2/0/2/2 (7/10) | Leave blank | 28.6/100 — Low | Urgent evaluation | No repeat button |

## Steps to verify

1. Enter the 5-minute components. Confirm the total, its colour, and component concerns inside the 5-minute card. A total of 7–10 is green, 4–6 amber, and 0–3 red. Component alerts remain separate from that total colour.
2. For a total below 7, click **+ 5 minutes**. Only the 10-minute form should open. The next button stays hidden until all five components are recorded, and appears only if the preceding repeat total stays below 7. The form stops adding observations after 20 minutes.
3. Enter any 10-minute values specified above, complete the birth/family fields and submit. The final immediate result must use the latest complete observation, without averaging. The recorded facts should list the recorded times, and concerns/actions should appear under their own titles.
4. For the recovery case, the final index and action should reflect the 10-minute findings. Earlier component concerns must remain mentioned; a higher total does not establish their clinical resolution.
5. For the still-below-7 case, continue adding 15 and 20 minutes with 1/1/1/1/2 at each time. After 20 minutes there should be no further + button and the inference reference should be 20 minutes.

## Input validation checks

- Missing required 5-minute component: progression/submission must be blocked.
- Optional 1-minute observation with only one component entered: submission must be blocked; complete all five or clear the observation.
- Open the 10-minute observation and enter only one component: submission must be blocked; do not compute a new inference result from an incomplete row.
- Leave 1-minute and all repeat components blank: a complete 5-minute observation alone is accepted.
- Enter gestational age 19 weeks, maternal age 11, or weight 0 g: submission must be blocked with a field error.

Run automated checks from the project directory:

```powershell
.venv\Scripts\python.exe -m unittest discover -s tests -q
node tests/repeat_observation_ui.cjs
```
