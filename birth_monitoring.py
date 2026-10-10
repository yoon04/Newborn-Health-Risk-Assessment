"""Explain recorded birth findings separately from heuristic fuzzy memberships.

Clinical categories are not crisp replacements for fuzzy inputs. This module
provides monitoring prompts, not diagnoses, orders, or a validated model.
"""


def explain_birth_monitoring(week, weight, age, complication, memberships, rules, index, level):
    gestation = ('Extremely preterm' if week < 28 else 'Very preterm' if week < 32
                 else 'Preterm' if week < 37 else 'Early term' if week < 39
                 else 'Full term' if week < 41 else 'Late term' if week < 42 else 'Post-term')
    weight_label = ('Extremely low birth weight' if weight < 1000 else
                    'Very low birth weight' if weight < 1500 else
                    'Low birth weight' if weight < 2500 else
                    'Higher birth weight (project review threshold)' if weight >= 4000 else
                    'Not low birth weight')
    age_label = 'Adolescent context' if age < 20 else 'Older maternal-age context' if age >= 35 else 'Maternal-age context'
    inputs = [
        {'name': 'Gestational age', 'value': f'{week:g} weeks', 'category': gestation,
         'memberships': {k: float(v) for k, v in memberships['birth_week'].items()},
         'explanation': 'Earlier gestation activates preterm rules; overlapping term and post-term sets make transitions gradual.'},
        {'name': 'Birth weight', 'value': f'{weight:g} g', 'category': weight_label,
         'memberships': {k: float(v) for k, v in memberships['birth_weight'].items() if not k.startswith('any_')},
         'explanation': 'Low and high weight memberships activate monitoring rules and interact with gestation. Weight alone cannot establish size for gestational age.'},
        {'name': 'Maternal age', 'value': f'{age:g} years', 'category': age_label,
         'memberships': {k: float(v) for k, v in memberships['maternal_age'].items() if not k.startswith('any_')},
         'explanation': 'Context only: age-related moderate rule activation is scaled by 0.25. This project coefficient is not clinically calibrated; age alone cannot activate a High rule.'},
        {'name': 'Delivery complication', 'value': 'Reported' if complication else 'Not reported',
         'category': 'Delivery context',
         'memberships': {k: float(v) for k, v in memberships['delivery_comp'].items()},
         'explanation': 'A reported complication activates review; with a gestation or weight concern it can activate a High rule. Delivery method alone does not imply a complication.'},
    ]
    concerns, actions = [], []
    if week < 37:
        concerns.append(f'Preterm birth ({week:g} weeks): assess feeding, temperature stability and respiratory status.')
    elif week < 39:
        concerns.append('Early-term birth: consider feeding and transition observations in the clinical context.')
    elif week >= 42:
        concerns.append('Post-term birth: review delivery history and neonatal transition findings.')
    if weight < 2500:
        concerns.append(f'Low birth weight ({weight:g} g): document feeding, temperature and growth monitoring needs.')
    elif weight >= 4000:
        concerns.append('Higher birth weight: review maternal diabetes history and whether glucose monitoring is indicated under local protocol.')
    if complication:
        concerns.append('Delivery complication reported; its type and severity are not captured by this Yes/No input.')
        actions.append('Clarify the delivery complication and document a neonatal review and monitoring plan appropriate to the actual findings.')
    if week < 32 or weight < 1500:
        priority = 'Prompt neonatal monitoring review'
        actions.insert(0, 'Arrange prompt neonatal-team review for very preterm or very low-weight findings, even if the fuzzy index is Moderate; document the monitoring setting and plan.')
    elif concerns or level != 'Low':
        priority = 'Monitoring plan'
    else:
        priority = 'Routine birth follow-up'
    if week < 37 or weight < 2500:
        actions.append('Use the local preterm/low-birth-weight pathway to document feeding support, thermal care, respiratory observations and growth follow-up; the clinical team decides interventions.')
    elif week < 39 or week >= 42 or weight >= 4000:
        actions.append('Ask the neonatal clinician to determine the observation plan and any indicated screening from the birth findings and actual examination.')
    if age < 20 or age >= 35:
        actions.append('Review maternal medical history and antenatal findings as context; maternal age alone does not establish illness in the newborn or a need for treatment.')
    if not concerns:
        concerns.append('No prematurity, low-weight, higher-weight or reported-complication flag is present; confirm the findings with the newborn examination.')
    if not actions:
        actions.append('Continue routine newborn observation, feeding assessment and follow-up according to the clinical examination and local protocol.')
    elif priority == 'Monitoring plan' and not (week < 37 or weight < 2500 or complication or week < 39 or week >= 42 or weight >= 4000):
        actions.append('Review the fuzzy monitoring signal in the clinical context before deciding whether additional observation is needed.')
    active = sorted((dict(r) for r in rules if r['activation'] > 0), key=lambda r: (-r['activation'], r['id']))
    summary = (f"Recorded birth: {week:g} weeks ({gestation.lower()}), {weight:g} g ({weight_label.lower()}), "
               f"maternal age {age:g}, and {'a reported delivery complication' if complication else 'no reported delivery complication'}. "
               f"Birth-monitoring index: {index:.1f}/100 ({level}); {priority.lower()}.")
    output_activations = {output: max((r['activation'] for r in active if r['outcome'] == output), default=0.0)
                          for output in ('low', 'moderate', 'high')}
    representatives = [next(r for r in active if r['outcome'] == output) for output in ('low', 'moderate', 'high')
                       if output_activations[output] > 0]
    drivers = '; '.join(f"{r['name']} ({r['outcome'].title()} rule strength {r['activation']:.2f})" for r in representatives)
    reason = (f"Main rule signals: {drivers}. The combined output has a centre-of-area index of {index:.1f}, "
              f"within the {level} band.")
    if output_activations['high'] > 0 and level != 'High':
        reason += ' A High rule is active, but overlapping outputs place the combined index below the High band; the monitoring concerns still apply.'
    finding_facts = [
        f"Gestational age: {week:g} weeks ({gestation.lower()}).",
        f"Birth weight: {weight:g} g ({weight_label.lower()}).",
        f"Maternal age: {age:g} years; contextual input only.",
        f"Delivery complication: {'Reported' if complication else 'Not reported'}.",
        f"Birth-monitoring index: {index:.1f}/100.",
        f"Final monitoring level: {level}.",
        f"Monitoring priority: {priority}.",
    ]
    reason_facts = [f"{r['name']}: {r['outcome'].title()} rule activation {r['activation']:.2f}." for r in representatives]
    reason_facts.append(f"Combined fuzzy output: centre-of-area index {index:.1f}; final label {level} (Low below 30, Moderate 30 to below 70, High 70 or above).")
    if output_activations['high'] > 0 and level != 'High':
        reason_facts.append('A High rule is active, but the combined index is below 70; recorded monitoring concerns still apply.')
    reason_facts.append('Rule activation is a membership strength, not a probability or a percentage contribution.')
    return {'inputs': inputs, 'concerns': concerns, 'actions': actions, 'priority': priority,
            'finding_facts': finding_facts, 'reason_facts': reason_facts,
            'summary': summary, 'result_reason': reason, 'output_activations': output_activations,
            'final_result': f'Birth-related monitoring index: {index:.1f}/100 ({level}). Monitoring priority: {priority}.',
            'active_rules': active,
            'explanation': 'Each rule uses the minimum membership for AND; the maximum activation per output level is aggregated. The index is the centroid of the clipped Low/Moderate/High curves. Activations are not probability or contribution percentages.',
            'limitations': 'This is a limited birth-monitoring screen, not a complete or validated estimate of newborn illness. Examination, vital signs, feeding and relevant maternal/infection history are not assessed here. Clinical category thresholds and overlapping fuzzy sets serve different purposes. No growth-percentile reference is included, so this module cannot classify small or large for gestational age. Rules and the 0.25 maternal-age scale require neonatal clinical review and outcome validation.'}
