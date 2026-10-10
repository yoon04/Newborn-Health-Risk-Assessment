from apgar_observations import validate_observation_records
from apgar_safety import check_apgar_safety
from birth_monitoring import explain_birth_monitoring
import numpy as np
from scipy.integrate import simpson
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

def triangular_mf(x, a, b, c):
    if a <= x < b:
        return (x - a) / (b - a)
    elif b <= x <= c:
        return (c - x) / (c - b)
    else:
        return 0.0

def trapezoidal_mf(x, a, b, c, d):
    if x <= a or x >= d:
        return 0.0
    elif a < x < b:
        return (x - a) / (b - a) if b > a else 1.0
    elif b <= x <= c:
        return 1.0
    elif c < x < d:
        return (d - x) / (d - c) if d > c else 1.0
    return 0.0

def convert_weight_to_grams(value, unit):
    if unit == 'kg':
        return value * 1000
    elif unit == 'lb':
        return value * 453.592
    return value

APGAR_DESCRIPTIONS = {
    'appearance': {
        0: ("Blue/Pale all over", "Direct clinical assessment needed — skin colour alone cannot establish oxygenation."),
        1: ("Pink body, blue hands/feet", "Mild concern — body color looks good, but fingertips and toes are still slightly blue."),
        2: ("Fully pink", "Excellent — healthy skin color throughout the entire body."),
    },
    'pulse': {
        0: ("Absent", "Critical — no heartbeat detected. Immediate medical intervention is needed."),
        1: ("Slow (below 100 bpm)", "Below normal — heart rate is too slow and needs close monitoring."),
        2: ("Strong (100+ bpm)", "Excellent — heart is beating at a healthy, strong rate."),
    },
    'grimace': {
        0: ("No response", "Concerning — baby shows no reaction to stimulation. Reflexes may be impaired."),
        1: ("Grimace only", "Moderate — some reflex activity, but response is weak."),
        2: ("Cry, cough, or sneeze", "Excellent — strong, healthy reflex response to stimulation."),
    },
    'activity': {
        0: ("Limp", "Concerning — very low or absent muscle tone. Baby is not moving."),
        1: ("Some flexion", "Moderate — baby shows some movement, but muscle tone is limited."),
        2: ("Active movement", "Excellent — baby is actively moving with good muscle strength."),
    },
    'respiration': {
        0: ("Absent", "Critical — baby is not breathing. Immediate help is required."),
        1: ("Weak or irregular", "Concerning — breathing is present but too weak or inconsistent."),
        2: ("Strong cry", "Excellent — baby is breathing well and crying vigorously."),
    },
}

def calculate_apgar(appearance, pulse, grimace, activity, respiration):
    safety = check_apgar_safety(appearance, pulse, grimace, activity, respiration)
    apgar = appearance + pulse + grimace + activity + respiration
    if apgar >= 7:
        category = "Normal (7–10)"
        summary = "The total is in the normal range; it does not establish overall health."
        severity = "good"
    elif apgar >= 4:
        category = "Moderate concern (4–6)"
        summary = "Baby may need some medical support."
        severity = "moderate"
    else:
        category = "Low (0–3)"
        summary = "Baby requires immediate medical attention."
        severity = "critical"

    component_detail = {
        k: {'score': v, 'label': APGAR_DESCRIPTIONS[k][v][0], 'note': APGAR_DESCRIPTIONS[k][v][1]}
        for k, v in [('appearance', appearance), ('pulse', pulse), ('grimace', grimace),
                     ('activity', activity), ('respiration', respiration)]
    }
    breakdown = (f"APGAR Score: {apgar}/10 ({category}) — {summary} "
                 f"(A:{appearance} P:{pulse} G:{grimace} A:{activity} R:{respiration})")
    return apgar, breakdown, category, severity, component_detail

def fuzzify_apgar(apgar):
    return {
        # The shoulders extend just beyond 0 and 10 so the extreme valid
        # scores retain full membership. Wider transitions preserve overlap
        # at the integer APGAR totals used by the assessment.
        'low':    trapezoidal_mf(apgar, -0.1, 0, 3, 5),
        'medium': trapezoidal_mf(apgar, 3, 4, 6, 8),
        'high':   trapezoidal_mf(apgar, 6, 7, 10, 10.1),
    }

def fuzzify_birth_week(week):
    return {
        'very_preterm': trapezoidal_mf(week, -0.1, 20, 28, 32),
        'preterm':      trapezoidal_mf(week, 28, 32, 35, 37.5),
        'term':         trapezoidal_mf(week, 35, 37, 40, 42.5),
        'postterm':     trapezoidal_mf(week, 40, 42, 45, 50.1),
    }

def fuzzify_birth_weight(w):
    ext_low  = trapezoidal_mf(w, -0.1, 100, 800, 1200)
    # Very-low weight is a nested concern: preserve its left shoulder so
    # improving an extremely low weight cannot increase the High activation.
    very_low = trapezoidal_mf(w, -0.1, 100, 1300, 1700)
    low      = trapezoidal_mf(w, 1200, 1600, 2200, 2800)
    normal   = trapezoidal_mf(w, 2200, 2500, 3800, 4300)
    high     = trapezoidal_mf(w, 3600, 4000, 4600, 5200)
    very_high= trapezoidal_mf(w, 4500, 5000, 6000, 6000.1)
    return {
        'extremely_low': ext_low, 'very_low': very_low, 'low': low,
        'normal': normal, 'high': high, 'very_high': very_high,
        'any_low': max(ext_low, very_low, low),
        'any_high': max(high, very_high),
    }

def fuzzify_maternal_age(age):
    """Heuristic age context: adolescent membership ends at 20; older-age
    membership rises after 35. Exact ramps are not clinically calibrated."""
    vy = trapezoidal_mf(age, -0.1, 0, 15, 18)
    y  = trapezoidal_mf(age, 15, 18, 18, 20)
    n  = trapezoidal_mf(age, 18, 20, 35, 40)
    a  = trapezoidal_mf(age, 35, 40, 45, 50)
    va = trapezoidal_mf(age, 40, 45, 60, 60.1)
    return {
        'very_young': vy, 'young': y, 'normal': n, 'advanced': a, 'very_advanced': va,
        'any_young': max(vy, y), 'any_advanced': max(a, va),
    }

def fuzzify_delivery_comp(dc):
    return {
        'normal':      triangular_mf(dc, -0.1, 0, 0.5),
        'complicated': triangular_mf(dc, 0.5, 1, 1.1),
    }

INHERITANCE_MODES = {
    'dominant_both_parents': {
        'label': 'Dominant: both parents have the condition',
        'base_prob': 0.75,
        'parent_signal': 0.95,
        'grandparent_signal': 0.0,
        'explanation': 'Both parents are affected by a dominant condition, so inheritance risk is high.',
    },
    'dominant_one_parent': {
        'label': 'Dominant: only one parent has the condition',
        'base_prob': 0.50,
        'parent_signal': 0.7,
        'grandparent_signal': 0.0,
        'explanation': 'One affected parent with dominant inheritance gives a baseline family-history index of 50 / 100.',
    },
    'dominant_none_parents_grandparent_yes': {
        'label': 'Dominant: parents unaffected, but grandparent had it',
        'base_prob': 0.20,
        'parent_signal': 0.2,
        'grandparent_signal': 0.95,
        'explanation': 'No affected parent lowers direct risk, but grandparent history keeps some inherited risk.',
    },
    'recessive_both_parents_carriers': {
        'label': 'Recessive: both parents are carriers',
        'base_prob': 0.25,
        'parent_signal': 0.6,
        'grandparent_signal': 0.0,
        'explanation': 'Classic recessive pattern: two carrier parents give a baseline family-history index of 25 / 100.',
    },
    'recessive_one_parent_carrier': {
        'label': 'Recessive: only one parent is a carrier',
        'base_prob': 0.03,
        'parent_signal': 0.3,
        'grandparent_signal': 0.0,
        'explanation': 'One carrier parent alone usually produces a low family-history index.',
    },
    'recessive_none_parents_grandparent_yes': {
        'label': 'Recessive: parents unaffected, but grandparent had it',
        'base_prob': 0.10,
        'parent_signal': 0.25,
        'grandparent_signal': 0.95,
        'explanation': 'Grandparent history suggests possible carrier status in the family line.',
    },
    'xlinked': {
        'label': 'X-linked: use parent status + child gender',
        'base_prob': 0.25,
        'parent_signal': 0.7,
        'grandparent_signal': 0.0,
        'explanation': 'X-linked risk is adjusted using which parent has the condition and whether they are carrier or affected.',
    },
    'xlinked_mother_carrier': {
        'label': 'X-linked (legacy): mother is a carrier',
        'base_prob': 0.50,
        'parent_signal': 0.7,
        'grandparent_signal': 0.0,
        'explanation': 'Legacy mode kept for compatibility. Prefer the new X-linked option with parent and status fields.',
    },
    'complex': {
        'label': 'Complex/multifactorial (e.g. diabetes, heart disease)',
        'base_prob': 0.10,
        'parent_signal': 0.3,
        'grandparent_signal': 0.3,
        'explanation': 'Complex diseases involve many genes and environment, so risk is estimated conservatively.',
    },
    'unknown': {
        'label': 'Not sure / unknown pattern',
        'base_prob': 0.10,
        'parent_signal': 0.2,
        'grandparent_signal': 0.2,
        'explanation': 'Unknown inheritance pattern uses a cautious default estimate.',
    },
}

DISEASE_GUIDES = {
    'diabetes': {
        'about': 'This family condition is about how the body handles sugar.',
        'watch_for': 'Watch for poor feeding, unusual sleepiness, or slow weight gain.',
        'next_step': 'Keep regular baby checkups and ask if sugar and growth checks are needed.',
    },
    'heartdisease': {
        'about': 'This family condition is about how well the heart pumps blood.',
        'watch_for': 'Watch for fast breathing, tiring during feeding, or blue color around lips.',
        'next_step': 'Ask your doctor if an early heart check is needed after birth.',
    },
    'hemoglobine': {
        'about': 'This is a family blood condition that can affect strength and energy.',
        'watch_for': 'Watch for pale skin, low energy, or slower weight gain.',
        'next_step': 'Ask when a simple blood check is needed and follow growth checks closely.',
    },
    'congenitaldeafness': {
        'about': 'This family condition can affect hearing from birth.',
        'watch_for': 'Watch for little response to loud sounds or familiar voices as the baby grows.',
        'next_step': 'Do hearing checks early and repeat them if your doctor advises.',
    },
    'musculardystrophy': {
        'about': 'This family condition can make muscles weaker over time.',
        'watch_for': 'Watch for weak movement, weak sucking, or slow motor milestones.',
        'next_step': 'Track movement milestones and ask for early support if delays appear.',
    },
    'colorblindness': {
        'about': 'This family condition affects how some colors are seen.',
        'watch_for': 'In newborns, this usually does not show clear signs right away.',
        'next_step': 'Later, ask about a color-vision check when your child is old enough.',
    },
}

MODE_SIMPLE_LABELS = {
    'dominant_both_parents': 'Family pattern: strong from both parents',
    'dominant_one_parent': 'Family pattern: strong from one parent',
    'dominant_none_parents_grandparent_yes': 'Family pattern: from grandparent side',
    'recessive_both_parents_carriers': 'Family pattern: both parents carry it',
    'recessive_one_parent_carrier': 'Family pattern: one parent carries it',
    'recessive_none_parents_grandparent_yes': 'Family pattern: possible from grandparent side',
    'xlinked': 'Family pattern: linked to parent side and child gender',
    'xlinked_mother_carrier': 'Family pattern: linked to parent side and child gender',
    'complex': 'Family pattern: mixed family and lifestyle factors',
    'unknown': 'Family pattern: not clearly known',
}

MODE_SIMPLE_REASON = {
    'dominant_both_parents': 'Both parents have this condition in the family, so the family-history signal is stronger.',
    'dominant_one_parent': 'One parent has this condition in the family, so there is a clear family-history signal.',
    'dominant_none_parents_grandparent_yes': 'Parents are not affected, but grandparent history still adds a family-history signal.',
    'recessive_both_parents_carriers': 'Both parents carry this condition in the family, so risk is meaningful.',
    'recessive_one_parent_carrier': 'Only one parent carries this condition, so the family-history signal is usually lower.',
    'recessive_none_parents_grandparent_yes': 'Grandparent history suggests this condition may still run in the family.',
    'complex': 'This condition can come from both family history and daily life factors, so the estimate is moderate.',
    'unknown': 'Because the family pattern is not clear, the estimate stays cautious.',
}


def disease_key(name):
    return ''.join(ch for ch in (name or '').strip().lower() if ch.isalpha())


def disease_guide(name):
    key = disease_key(name)
    if key in DISEASE_GUIDES:
        return DISEASE_GUIDES[key]
    return {
        'about': f'{name} was entered as a custom family condition.',
        'watch_for': 'Watch for unusual feeding, breathing, hearing, movement, sleep, or growth changes.',
        'next_step': 'Share this condition name with your doctor and ask which baby checks are best.',
    }


def inherited_level_label(prob):
    if prob < 0.15:
        return 'Low'
    if prob < 0.40:
        return 'Moderate'
    return 'High'


def xlinked_simple_reason(child_gender, parent, status):
    g = normalize_gender(child_gender)
    p = (parent or 'mother').strip().lower()
    s = (status or 'carrier').strip().lower()

    if p == 'mother':
        if s == 'affected':
            return 'This was marked on the mother side, and mother has the condition, so the family-history signal can be stronger.'
        return 'This was marked on the mother side, and mother carries it in the family, so there is still a clear family-history signal.'

    if g == 'male':
        return 'This was marked on the father side, and for a boy this path usually lowers the family-history signal.'
    return 'This was marked on the father side, and for a girl this path can raise the family-history signal.'


def fuzzify_genetic_base(base_prob):
    return {
        'low': trapezoidal_mf(base_prob, 0.0, 0.0, 0.10, 0.30),
        'moderate': trapezoidal_mf(base_prob, 0.15, 0.30, 0.50, 0.70),
        'high': trapezoidal_mf(base_prob, 0.55, 0.70, 1.0, 1.0),
    }
def fuzzify_genetic_signal(signal):
    return {
        'low': trapezoidal_mf(signal, 0.0, 0.0, 0.20, 0.45),
        'moderate': trapezoidal_mf(signal, 0.25, 0.45, 0.60, 0.80),
        'high': trapezoidal_mf(signal, 0.60, 0.80, 1.0, 1.0),
    }
def apply_genetic_rules(base_prob, parent_signal, grandparent_signal):
    base = fuzzify_genetic_base(base_prob)
    parent = fuzzify_genetic_signal(parent_signal)
    gp = fuzzify_genetic_signal(grandparent_signal)
    high = max(
        min(base['high'], parent['high']),
        min(base['moderate'], parent['high']),
        min(base['moderate'], parent['moderate'], gp['high']),
        min(base['high'], gp['moderate']),
    )
    moderate = max(
        min(base['moderate'], parent['moderate']),
        min(base['low'], parent['high']),
        min(base['moderate'], gp['moderate']),
        min(base['low'], parent['moderate'], gp['high']),
    )
    low = max(
        min(base['low'], parent['low']),
        min(base['low'], gp['low']),
        min(base['moderate'], parent['low'], gp['low']),
    )
    return {'low': low, 'moderate': moderate, 'high': high}
def defuzzify_genetic_risk(levels, base_prob):
    strength = levels['low'] + levels['moderate'] + levels['high']
    if strength <= 0:
        return base_prob

    fuzzy_estimate = (
        levels['low'] * 0.12 +
        levels['moderate'] * 0.35 +
        levels['high'] * 0.75
    ) / strength
    return (0.65 * base_prob) + (0.35 * fuzzy_estimate)

def normalize_gender(gender):
    g = (gender or '').strip().lower()
    if g in ('male', 'm'):
        return 'male'
    if g in ('female', 'f'):
        return 'female'
    raise ValueError("child_gender must be 'male' or 'female'")

def xlinked_inheritance_profile(child_gender, parent, status):
    g = normalize_gender(child_gender)
    p = (parent or 'mother').strip().lower()
    s = (status or 'carrier').strip().lower()

    # Probability here represents inheriting the X-linked mutation.
    if p == 'mother':
        if s == 'affected':
            base_prob = 1.0
            reason = 'Mother is affected, so she passes an affected X chromosome to all children.'
            parent_signal = 1.0
        else:
            base_prob = 0.5
            reason = 'Mother is a carrier, producing a baseline inheritance index of 50 / 100 for this model.'
            parent_signal = 0.7
    else:
        if s == 'carrier':
            base_prob = 1.0 if g == 'female' else 0.0
            reason = 'Father cannot be a typical carrier in X-linked recessive patterns; the model treats this status as affected.'
            parent_signal = 0.75
        else:
            base_prob = 1.0 if g == 'female' else 0.0
            reason = 'Affected father passes his X chromosome to daughters and Y chromosome to sons.'
            parent_signal = 0.75

    gender_note = {
        'male': 'Child gender is male, so paternal X transmission is not possible.',
        'female': 'Child gender is female, so paternal X transmission applies.',
    }[g]
    return base_prob, parent_signal, reason, gender_note

def estimate_inherited_prob(diseases, child_gender):
    probs_list = []
    explanations = []
    for d in diseases:
        mode_key = d.get('mode', 'unknown')
        info = INHERITANCE_MODES.get(mode_key, INHERITANCE_MODES['unknown'])
        base_prob = info['base_prob']
        parent_signal = info.get('parent_signal', 0.2)
        gp_signal = info.get('grandparent_signal', 0.2)
        mode_explanation = info['explanation']
        mode_simple_reason = MODE_SIMPLE_REASON.get(
            mode_key,
            'Family history details were limited, so this estimate stays cautious.',
        )
        mode_display_label = MODE_SIMPLE_LABELS.get(mode_key, MODE_SIMPLE_LABELS['unknown'])

        if mode_key in ('xlinked', 'xlinked_mother_carrier'):
            x_parent = d.get('xlinked_parent', 'mother')
            x_status = d.get('xlinked_status', 'carrier')
            base_prob, parent_signal, x_reason, gender_note = xlinked_inheritance_profile(
                child_gender,
                x_parent,
                x_status,
            )
            gp_signal = 0.0
            mode_explanation = (
                f"{x_reason} Parent selected: {x_parent}. Parent status: {x_status}. {gender_note}"
            )
            mode_simple_reason = xlinked_simple_reason(child_gender, x_parent, x_status)

        fuzzy_levels = apply_genetic_rules(
            base_prob,
            parent_signal,
            gp_signal,
        )
        fuzzy_prob = defuzzify_genetic_risk(fuzzy_levels, base_prob)
        risk_index = float(fuzzy_prob * 100)
        guide = disease_guide(d.get('disease', 'Unknown'))
        simple_risk_level = inherited_level_label(fuzzy_prob)
        probs_list.append({
            'disease': d['disease'],
            'base_prob': base_prob,
            'fuzzy_prob': fuzzy_prob,
            'base_risk_index': float(base_prob * 100),
            'risk_index': risk_index,
            'expl': (
                f"{d['disease']}: {mode_explanation} "
                f"Baseline index {base_prob*100:.0f} / 100 adjusted by fuzzy family-history rules "
                f"to {risk_index:.1f} / 100."
            ),
            'mode_label': info['label'],
            'mode_display_label': mode_display_label,
            'simple_risk_level': simple_risk_level,
            'simple_about': guide['about'],
            'simple_watch_for': guide['watch_for'],
            'simple_next_step': guide['next_step'],
            'simple_why_score': mode_simple_reason,
        })
        explanations.append(
            f"{d['disease']}: {mode_explanation} "
            f"(baseline index {base_prob*100:.0f} / 100, fuzzy-adjusted index {risk_index:.1f} / 100)."
        )
    explanation = "; ".join(explanations) if explanations else "No inherited diseases noted."
    return probs_list, explanation


def apply_family_history_rules(family_history, return_rules=False):
    """Create a fuzzy family-history indicator from non-technical user input."""
    status = family_history.get('status', 'unknown')
    relative = family_history.get('affected_relative', '')
    is_no = 1.0 if status == 'no' else 0.0
    is_unknown = 1.0 if status == 'unknown' else 0.0
    is_yes = 1.0 if status == 'yes' else 0.0

    rules = [
        _rule('FH-01', 'Family History', 'No known family disease',
              'No known family disease supports a low family-history contribution.',
              'low', is_no),
        _rule('FH-02', 'Family History', 'Family history unknown - low component',
              'Unknown family history keeps a smaller low contribution because no affected relative is confirmed.',
              'low', 0.45 * is_unknown),
        _rule('FH-03', 'Family History', 'Family history unknown - uncertain component',
              'Unknown family history activates a moderate contribution and lowers assessment confidence.',
              'moderate', 0.55 * is_unknown),
        _rule('FH-04', 'Family History', 'Father affected',
              'A known disease in the father elevates the family-history indicator.',
              'moderate', is_yes if relative == 'father' else 0.0),
        _rule('FH-05', 'Family History', 'Mother affected',
              'A known disease in the mother elevates the family-history indicator.',
              'moderate', is_yes if relative == 'mother' else 0.0),
        _rule('FH-06', 'Family History', 'Both parents affected',
              'A known disease affecting both parents creates a stronger family-history indicator.',
              'high', is_yes if relative == 'both_parents' else 0.0),
        _rule('FH-07', 'Family History', 'Other family member affected',
              'A known disease in another family member creates a smaller moderate contribution.',
              'moderate', 0.75 * is_yes if relative == 'other_family_member' else 0.0),
        _rule('FH-08', 'Family History', 'Affected relative unknown',
              'A known disease with an unknown affected relative creates an uncertain moderate contribution.',
              'moderate', 0.65 * is_yes if relative == 'unknown' else 0.0),
        _rule('FH-09', 'Family History', 'Distant-family low component',
              'An affected non-parent family member retains a smaller low contribution.',
              'low', 0.25 * is_yes if relative == 'other_family_member' else 0.0),
        _rule('FH-10', 'Family History', 'Unknown-relative low component',
              'Unknown affected-relative information retains a smaller low contribution.',
              'low', 0.35 * is_yes if relative == 'unknown' else 0.0),
    ]
    levels = _aggregate_rule_levels(rules)
    return (levels, rules) if return_rules else levels


def family_history_message(family_history, family_history_risk_index):
    status = family_history.get('status', 'unknown')
    relative = family_history.get('affected_relative', '')
    if status == 'no':
        return 'No known family disease was reported, so no additional family-history follow-up is suggested by this input alone.'
    if status == 'unknown':
        return 'Family disease history is unknown, so this part of the assessment is less certain.'
    if relative == 'both_parents':
        return 'A disease was reported in both parents, so family history may need additional attention.'
    if relative in ('father', 'mother'):
        return 'A disease was reported in one parent, so family history may need additional attention.'
    if relative == 'other_family_member':
        return 'A disease was reported in another family member, creating a smaller family-history concern.'
    return 'A family disease was reported, but who has it is unknown, so this part is less certain.'

 
def _rule(rule_id, module, name, description, outcome, activation):
    return {
        'id': rule_id,
        'module': module,
        'name': name,
        'description': description,
        'outcome': outcome,
        'activation': float(activation),
    }


def _aggregate_rule_levels(rules):
    return {
        outcome: max(
            (rule['activation'] for rule in rules if rule['outcome'] == outcome),
            default=0.0,
        )
        for outcome in ('low', 'moderate', 'high')
    }


def apply_immediate_condition_rules(fi, return_rules=False):
    """Immediate condition module: APGAR plus reported delivery complication."""
    apgar = fi['apgar']
    comp = fi['delivery_comp']
    rules = [
        _rule('IM-01', 'Immediate Condition', 'Stable APGAR without complication',
              'Stable APGAR and no reported delivery complication support a low immediate risk level.',
              'low', min(apgar['high'], comp['normal'])),
        _rule('IM-02', 'Immediate Condition', 'Concerning APGAR',
              'A concerning APGAR activates the moderate immediate risk level.',
              'moderate', apgar['medium']),
        _rule('IM-03', 'Immediate Condition', 'Stable APGAR with complication',
              'A reported delivery complication can elevate immediate risk even when APGAR is stable.',
              'moderate', min(apgar['high'], comp['complicated'])),
        _rule('IM-04', 'Immediate Condition', 'Critical APGAR',
              'A critical APGAR activates the high immediate risk level.',
              'high', apgar['low']),
        _rule('IM-05', 'Immediate Condition', 'Concerning APGAR with complication',
              'Concerning APGAR together with a reported delivery complication activates high immediate risk.',
              'high', min(apgar['medium'], comp['complicated'])),
    ]
    levels = _aggregate_rule_levels(rules)
    return (levels, rules) if return_rules else levels


def apply_birth_related_rules(fi, return_rules=False):
    """Heuristic birth monitoring. Maternal-age rule strengths are scaled by
    0.25 as a project policy, not a clinically calibrated coefficient."""
    week = fi['birth_week']
    weight = fi['birth_weight']
    age = fi['maternal_age']
    comp = fi['delivery_comp']

    rules = [
        _rule('BR-01', 'Birth-Related', 'Very preterm gestation', 'Very preterm gestational age activates high birth-related risk.', 'high', week['very_preterm']),
        _rule('BR-02', 'Birth-Related', 'Extremely low birth weight', 'Extremely low birth weight activates high birth-related risk.', 'high', weight['extremely_low']),
        _rule('BR-03', 'Birth-Related', 'Very low birth weight', 'Very low birth weight activates high birth-related risk.', 'high', weight['very_low']),
        _rule('BR-04', 'Birth-Related', 'Very high birth weight', 'Very high birth weight activates high birth-related risk.', 'high', weight['very_high']),
        _rule('BR-05', 'Birth-Related', 'Very advanced maternal-age context', 'Maternal age adds limited context, not a standalone high newborn-risk signal (policy scale 0.25).', 'moderate', 0.25 * age['very_advanced']),
        _rule('BR-06', 'Birth-Related', 'Preterm with low birth weight', 'Preterm gestation together with low birth weight elevates birth-related risk.', 'high', min(week['preterm'], weight['any_low'])),
        _rule('BR-07', 'Birth-Related', 'Post-term with high birth weight', 'Post-term gestation together with high birth weight elevates birth-related risk.', 'high', min(week['postterm'], weight['any_high'])),
        _rule('BR-08', 'Birth-Related', 'Complication with a birth concern', 'A reported delivery complication combines with gestational-age or weight concerns; maternal age alone does not activate this high rule.', 'high', min(comp['complicated'], max(week['preterm'], weight['any_low'], weight['any_high']))),
        _rule('BR-09', 'Birth-Related', 'Preterm gestation', 'Preterm gestational age activates moderate birth-related risk.', 'moderate', week['preterm']),
        _rule('BR-10', 'Birth-Related', 'Post-term gestation', 'Post-term gestational age activates moderate birth-related risk.', 'moderate', week['postterm']),
        _rule('BR-11', 'Birth-Related', 'Low birth weight', 'Low birth weight activates moderate birth-related risk.', 'moderate', weight['low']),
        _rule('BR-12', 'Birth-Related', 'High birth weight', 'High birth weight activates moderate birth-related risk.', 'moderate', weight['high']),
        _rule('BR-13', 'Birth-Related', 'Young maternal-age context', 'Maternal age adds limited contextual moderate activation (policy scale 0.25).', 'moderate', 0.25 * age['any_young']),
        _rule('BR-14', 'Birth-Related', 'Advanced maternal-age context', 'Maternal age adds limited contextual moderate activation (policy scale 0.25).', 'moderate', 0.25 * age['advanced']),
        _rule('BR-15', 'Birth-Related', 'Reported delivery complication', 'A reported delivery complication activates moderate birth-related risk.', 'moderate', comp['complicated']),
        _rule('BR-16', 'Birth-Related', 'Term, normal weight, no complication', 'Term gestation, normal birth weight, and no reported complication support low birth-related risk.', 'low', min(week['term'], weight['normal'], comp['normal'])),
    ]
    levels = _aggregate_rule_levels(rules)
    return (levels, rules) if return_rules else levels


def risk_output_curves(risk_levels):
    """Clip overlapping low/moderate/high output sets by rule strength."""
    x_risk = np.linspace(0, 100, 1001)
    low_shape = np.clip((50 - x_risk) / 25, 0, 1)
    moderate_shape = np.clip(np.minimum((x_risk - 25) / 25, (75 - x_risk) / 25), 0, 1)
    high_shape = np.clip((x_risk - 50) / 25, 0, 1)
    low_mf = np.minimum(low_shape, risk_levels['low'])
    moderate_mf = np.minimum(moderate_shape, risk_levels['moderate'])
    high_mf = np.minimum(high_shape, risk_levels['high'])
    combined = np.maximum(low_mf, np.maximum(moderate_mf, high_mf))
    return x_risk, low_mf, moderate_mf, high_mf, combined


def defuzzify_risk(risk_levels):
    x_risk, _low, _moderate, _high, combined = risk_output_curves(risk_levels)
    denominator = simpson(combined, x=x_risk)
    if denominator <= 0:
        return 0.0
    return float(simpson(x_risk * combined, x=x_risk) / denominator)


def fuzzify_risk_index(risk_index):
    """Fuzzify a module's 0-100 index for hierarchical inference."""
    return {
        'low': trapezoidal_mf(risk_index, -0.1, 0, 25, 50),
        'moderate': trapezoidal_mf(risk_index, 25, 40, 60, 75),
        'high': trapezoidal_mf(risk_index, 50, 75, 100, 100.1),
    }


def apply_hierarchical_risk_rules(immediate_index, birth_index, family_index=None, return_rules=False):
    """Acute hierarchy only. family_index is ignored for legacy callers."""
    immediate = fuzzify_risk_index(immediate_index)
    birth = fuzzify_risk_index(birth_index)

    rules = [
        _rule('HR-01', 'Acute Triage', 'Both acute modules low', 'Low immediate and birth-related indices support routine care.', 'low', min(immediate['low'], birth['low'])),
        _rule('HR-02', 'Acute Triage', 'Moderate immediate risk', 'Moderate immediate risk keeps the overall result at least moderate.', 'moderate', immediate['moderate']),
        _rule('HR-03', 'Acute Triage', 'Moderate birth-related risk', 'Moderate birth-related risk keeps the overall result at least moderate.', 'moderate', birth['moderate']),
        _rule('HR-05', 'Acute Triage', 'High immediate risk persists', 'High immediate risk cannot be cancelled by lower birth-related or family-history indices.', 'high', immediate['high']),
        _rule('HR-06', 'Acute Triage', 'High birth-related risk persists', 'High birth-related risk remains elevated even when family-history risk is low.', 'high', birth['high']),
        _rule('HR-08', 'Acute Triage', 'Moderate immediate and birth risks', 'Moderate immediate and birth-related risks together activate high overall risk.', 'high', min(immediate['moderate'], birth['moderate'])),
        _rule('HR-09', 'Acute Triage', 'High immediate with moderate birth risk', 'High immediate risk with moderate birth-related risk activates high overall risk.', 'high', min(immediate['high'], birth['moderate'])),
        _rule('HR-10', 'Acute Triage', 'Moderate immediate with high birth risk', 'Moderate immediate risk with high birth-related risk activates high overall risk.', 'high', min(immediate['moderate'], birth['high'])),
    ]
    levels = _aggregate_rule_levels(rules)
    return (levels, rules) if return_rules else levels


def risk_level_for_index(risk_index):
    if risk_index < 30:
        return 'Low'
    if risk_index < 70:
        return 'Moderate'
    return 'High'


def select_important_rules(rule_traces, limit=10):
    """Return the strongest activated rules without changing fuzzy inference."""
    active = [rule.copy() for rule in rule_traces if rule['activation'] > 0.01]
    outcome_priority = {'high': 2, 'moderate': 1, 'low': 0}
    active.sort(
        key=lambda rule: (rule['activation'], outcome_priority[rule['outcome']]),
        reverse=True,
    )
    return active[:limit]


def calculate_assessment_confidence(final_risk_levels, important_inputs_complete, family_history):
    """Grade result confidence from input completeness and fuzzy activation clarity."""
    activations = sorted((float(value) for value in final_risk_levels.values()), reverse=True)
    strongest = activations[0] if activations else 0.0
    runner_up = activations[1] if len(activations) > 1 else 0.0
    separation = strongest - runner_up
    unknown_family_history = (
        family_history.get('status') == 'unknown'
        or (
            family_history.get('status') == 'yes'
            and family_history.get('affected_relative') == 'unknown'
        )
    )

    if not important_inputs_complete:
        level = 'Low'
    elif strongest >= 0.75 and separation >= 0.25:
        level = 'High'
    elif strongest >= 0.40 and separation >= 0.10:
        level = 'Moderate'
    else:
        level = 'Low'

    if unknown_family_history and level == 'High':
        level = 'Moderate'

    reasons = []
    reasons.append(
        'All important inputs were complete and valid.'
        if important_inputs_complete
        else 'One or more important inputs were incomplete.'
    )
    reasons.append(
        'At least one family-history inheritance pattern was marked unknown.'
        if unknown_family_history
        else 'Family-history information was either specified or no condition was reported.'
    )
    if strongest >= 0.75 and separation >= 0.25:
        reasons.append('The strongest module fuzzy level was clearly separated from the alternatives.')
    elif strongest >= 0.40 and separation >= 0.10:
        reasons.append('The module fuzzy levels showed a usable but not strong separation.')
    else:
        reasons.append('The module fuzzy levels overlapped substantially, so the interpretation is less certain.')

    return {
        'level': level,
        'reasons': reasons,
        'strongest_activation': strongest,
        'activation_separation': separation,
    }


def _dominant_membership(memberships, keys):
    key = max(keys, key=lambda item: memberships[item])
    return key, float(memberships[key])


def identify_assessment_factors(fuzzy_inputs, family_history_risk_index, family_history, include_family=True):
    """Summarize input signals; strengths rank factors but are not contribution shares."""
    factors = []

    apgar_key, apgar_strength = _dominant_membership(fuzzy_inputs['apgar'], ('low', 'medium', 'high'))
    apgar_text = {
        'low': ('Critical APGAR pattern', 'The APGAR memberships lean toward the critical range.', 'impact'),
        'medium': ('Concerning APGAR pattern', 'The APGAR memberships lean toward the concerning range.', 'impact'),
        'high': ('Stable APGAR pattern', 'The APGAR memberships lean toward the stable range.', 'lowering'),
    }[apgar_key]
    factors.append({'name': apgar_text[0], 'description': apgar_text[1], 'role': apgar_text[2], 'strength': apgar_strength})

    week_key, week_strength = _dominant_membership(
        fuzzy_inputs['birth_week'], ('very_preterm', 'preterm', 'term', 'postterm')
    )
    week_text = {
        'very_preterm': ('Very preterm gestational age', 'Gestational-age membership is strongest in the very preterm set.', 'impact'),
        'preterm': ('Preterm gestational age', 'Gestational-age membership is strongest in the preterm set.', 'impact'),
        'term': ('Term gestational age', 'Gestational-age membership is strongest in the term set.', 'lowering'),
        'postterm': ('Post-term gestational age', 'Gestational-age membership is strongest in the post-term set.', 'impact'),
    }[week_key]
    factors.append({'name': week_text[0], 'description': week_text[1], 'role': week_text[2], 'strength': week_strength})

    weight_key, weight_strength = _dominant_membership(
        fuzzy_inputs['birth_weight'], ('extremely_low', 'very_low', 'low', 'normal', 'high', 'very_high')
    )
    weight_text = {
        'extremely_low': ('Extremely low birth weight', 'Birth-weight membership is strongest in the extremely low set.', 'impact'),
        'very_low': ('Very low birth weight', 'Birth-weight membership is strongest in the very low set.', 'impact'),
        'low': ('Low birth weight', 'Birth-weight membership is strongest in the low set.', 'impact'),
        'normal': ('Normal birth weight', 'Birth-weight membership is strongest in the normal set.', 'lowering'),
        'high': ('High birth weight', 'Birth-weight membership is strongest in the high set.', 'impact'),
        'very_high': ('Very high birth weight', 'Birth-weight membership is strongest in the very high set.', 'impact'),
    }[weight_key]
    factors.append({'name': weight_text[0], 'description': weight_text[1], 'role': weight_text[2], 'strength': weight_strength})

    age_key, age_strength = _dominant_membership(
        fuzzy_inputs['maternal_age'], ('very_young', 'young', 'normal', 'advanced', 'very_advanced')
    )
    age_text = {
        'very_young': ('Very young maternal age', 'Maternal age is contextual only (rule scale 0.25), with membership strongest in the very young set.', 'impact'),
        'young': ('Young maternal age', 'Maternal age is contextual only (rule scale 0.25), with membership strongest in the young set.', 'impact'),
        'normal': ('Typical maternal age range', 'Typical maternal age adds no adverse-age activation; reassuring newborn rules depend on gestation, weight and complication findings.', 'context'),
        'advanced': ('Advanced maternal age', 'Maternal age is contextual only (rule scale 0.25), with membership strongest in the advanced set.', 'impact'),
        'very_advanced': ('Very advanced maternal age', 'Maternal age is contextual only (rule scale 0.25), with membership strongest in the very advanced set.', 'impact'),
    }[age_key]
    factors.append({'name': age_text[0], 'description': age_text[1], 'role': age_text[2], 'strength': 0.25 * age_strength})

    complication_strength = float(fuzzy_inputs['delivery_comp']['complicated'])
    if complication_strength > 0:
        factors.append({'name': 'Reported delivery complication', 'description': 'A delivery complication was reported separately from delivery type.', 'role': 'impact', 'strength': complication_strength})
    else:
        factors.append({'name': 'No reported delivery complication', 'description': 'Delivery type alone does not add a complication signal.', 'role': 'lowering', 'strength': float(fuzzy_inputs['delivery_comp']['normal'])})

    family_level = risk_level_for_index(family_history_risk_index)
    if family_history.get('status') == 'yes':
        factors.append({
            'name': 'Known family disease',
            'description': family_history_message(family_history, family_history_risk_index),
            'role': 'lowering' if family_level == 'Low' else 'impact',
            'strength': max(fuzzify_risk_index(family_history_risk_index).values()),
        })
    elif family_history.get('status') == 'unknown':
        factors.append({
            'name': 'Family disease history is unknown',
            'description': 'Unknown family history adds uncertainty and may need clarification with a healthcare professional.',
            'role': 'impact',
            'strength': max(fuzzify_risk_index(family_history_risk_index).values()),
        })
    else:
        factors.append({'name': 'No known family disease', 'description': 'No known family disease was reported.', 'role': 'lowering', 'strength': 1.0})

    if not include_family:
        factors = [f for f in factors if f['name'] not in {'Known family disease', 'Family disease history is unknown', 'No known family disease'}]
    impact_factors = sorted(
        (factor for factor in factors if factor['role'] == 'impact'),
        key=lambda factor: factor['strength'], reverse=True,
    )
    lowering_factors = sorted(
        (factor for factor in factors if factor['role'] == 'lowering'),
        key=lambda factor: factor['strength'], reverse=True,
    )
    main = impact_factors[:3]
    if len(main) < 3:
        main.extend(lowering_factors[:3 - len(main)])
    main_names = {factor['name'] for factor in main}
    lower_impact = [factor for factor in factors if factor['name'] not in main_names]
    lower_impact.sort(key=lambda factor: factor['strength'], reverse=True)
    return main, lower_impact


def build_user_guidance(risk_level, main_factors, lower_impact_factors):
    summaries = {
        'Low': 'The information entered does not highlight a major concern, but normal newborn observation and checkups are still important.',
        'Moderate': 'A few factors in the information entered may need closer attention and follow-up.',
        'High': 'Several entered factors suggest that prompt professional medical evaluation is important.',
    }
    actions = {
        'Low': [
            'Continue normal newborn care and routine checkups.',
            'Keep observing feeding, breathing, temperature, and activity.',
            'Contact a healthcare professional if anything seems unusual.',
        ],
        'Moderate': [
            'Arrange or continue follow-up with a healthcare professional.',
            'Pay closer attention to the factors highlighted in this assessment.',
            'Do not rely on this result alone for medical decisions.',
        ],
        'High': [
            'Seek prompt professional medical evaluation.',
            'Do not wait for this application to confirm or rule out a diagnosis.',
            'Keep the baby under close observation while following professional advice.',
        ],
    }
    notice_text = {
        'Very preterm gestational age': 'Baby was born much earlier than expected.',
        'Preterm gestational age': 'Baby was born earlier than expected.',
        'Post-term gestational age': 'Baby was born later than the usual term range.',
        'Extremely low birth weight': 'Birth weight is much lower than the usual range.',
        'Very low birth weight': 'Birth weight is well below the usual range.',
        'Low birth weight': 'Birth weight is lower than the usual range.',
        'High birth weight': 'Birth weight is above the usual range.',
        'Very high birth weight': 'Birth weight is well above the usual range.',
        'Critical APGAR pattern': 'The APGAR result needs urgent professional attention.',
        'Concerning APGAR pattern': 'The APGAR result may need closer attention.',
        'Very young maternal age': "Mother's age may add a pregnancy-related concern.",
        'Young maternal age': "Mother's age may add a pregnancy-related concern.",
        'Advanced maternal age': "Mother's age may add a pregnancy-related concern.",
        'Very advanced maternal age': "Mother's age may add a pregnancy-related concern.",
        'Reported delivery complication': 'A delivery complication was reported.',
        'Known family disease': 'Family history may need additional attention.',
        'Family disease history is unknown': 'Family disease history is unknown and may need clarification.',
    }
    ordered_factors = main_factors + lower_impact_factors
    notices = []
    for factor in ordered_factors:
        if factor.get('role') != 'impact':
            continue
        notice = notice_text.get(factor.get('name'))
        if notice and notice not in notices:
            notices.append(notice)
    if not notices:
        notices.append('No major concern was highlighted by the information entered.')

    return {
        'short_summary': summaries[risk_level],
        'main_notices': notices[:4],
        'next_steps': actions[risk_level],
        'urgent_help_signs': [
            'The baby stops breathing, has serious difficulty breathing, or looks blue, very pale, or grey.',
            'The baby is difficult to wake, unusually inactive, floppy, or unresponsive.',
            'The baby is not feeding normally and you are worried.',
            'The baby has a fever, feels unusually hot or cold, or has a seizure or fit.',
        ],
    }

def generate_visualizations(
    fuzzy_inputs, final_risk_levels, actual_values, family_history_items,
    chart_prefix='', module_risk_levels=None,
):
    static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    os.makedirs(static_dir, exist_ok=True)
    plots = {}

    plt.rcParams.update({
        'font.family': 'DejaVu Sans', 'axes.spines.top': False, 'axes.spines.right': False,
        'figure.facecolor': '#ffffff', 'axes.facecolor': '#ffffff',
        'axes.labelcolor': '#111827', 'xtick.color': '#4b5563', 'ytick.color': '#4b5563',
        'axes.titlecolor': '#111827', 'axes.edgecolor': '#9ca3af', 'grid.color': '#d9d9d9',
        'text.color': '#111827', 'legend.facecolor': '#ffffff', 'legend.edgecolor': '#d1d5db',
    })

    def save_fig(x_range, curves_data, title, xlabel, filename, user_val):
        fig, ax = plt.subplots(figsize=(7, 3.5))
        for label, vals, color in curves_data:
            ax.plot(x_range, vals, label=label, color=color, linewidth=2)
            ax.fill_between(x_range, 0, vals, alpha=0.07, color=color)
        if user_val is not None:
            ax.axvline(user_val, color='#111827', linestyle='--', linewidth=2.5, label=f'Your value: {user_val}', zorder=5)
        ax.set_title(title, fontsize=12, fontweight='bold', pad=10)
        ax.set_xlabel(xlabel, fontsize=10)
        ax.set_ylabel('Membership (0–1)', fontsize=10)
        ax.legend(fontsize=8, loc='upper right')
        ax.grid(True, alpha=0.3)
        ax.set_ylim(0, 1.15)
        fig.savefig(os.path.join(static_dir, filename), dpi=140, bbox_inches='tight', facecolor='#ffffff')
        plt.close(fig)

    x = np.linspace(0, 10, 500)
    save_fig(x, [
        ('Low (0–3)',    [trapezoidal_mf(v,-0.1,0,3,5) for v in x],    '#ef4444'),
        ('Medium (4–6)', [trapezoidal_mf(v,3,4,6,8) for v in x],       '#f59e0b'),
        ('High (7–10)',  [trapezoidal_mf(v,6,7,10,10.1) for v in x],  '#22c55e'),
    ], "Baby's APGAR Score Interpretation", "APGAR Score (0–10)", f"{chart_prefix}apgar_fuzzy.png", actual_values['apgar'])
    plots['apgar'] = f'static/{chart_prefix}apgar_fuzzy.png'

    x = np.linspace(20, 46, 500)
    save_fig(x, [
        ('Very Preterm (<28w)', [trapezoidal_mf(v,-0.1,20,28,32) for v in x],    '#7f1d1d'),
        ('Preterm (28–37w)',    [trapezoidal_mf(v,28,32,35,37.5) for v in x],   '#ef4444'),
        ('Term (37–42w)',       [trapezoidal_mf(v,35,37,40,42.5) for v in x],   '#22c55e'),
        ('Post-term (>42w)',    [trapezoidal_mf(v,40,42,45,50.1) for v in x],  '#f59e0b'),
    ], "Gestational Age Interpretation", "Weeks of Pregnancy", f"{chart_prefix}week_fuzzy.png", actual_values['week'])
    plots['week'] = f'static/{chart_prefix}week_fuzzy.png'

    x = np.linspace(400, 5500, 500)
    save_fig(x, [
        ('Extremely Low (<1kg)', [trapezoidal_mf(v,-0.1,100,800,1200) for v in x],     '#7f1d1d'),
        ('Very Low (1–1.5kg)',   [trapezoidal_mf(v,800,1000,1300,1700) for v in x],    '#ef4444'),
        ('Low (1.5–2.5kg)',      [trapezoidal_mf(v,1200,1600,2200,2800) for v in x],   '#f97316'),
        ('Normal (2.5–4kg)',     [trapezoidal_mf(v,2200,2500,3800,4300) for v in x],   '#22c55e'),
        ('High (4–4.5kg)',       [trapezoidal_mf(v,3600,4000,4600,5200) for v in x],   '#f59e0b'),
        ('Very High (>4.5kg)',   [trapezoidal_mf(v,4500,5000,6000,6000.1) for v in x], '#ef4444'),
    ], "Birth Weight Interpretation", "Weight (grams)", f"{chart_prefix}weight_fuzzy.png", actual_values['weight'])
    plots['weight'] = f'static/{chart_prefix}weight_fuzzy.png'

    x = np.linspace(12, 55, 500)
    save_fig(x, [
        ('Very Young (<15)',    [fuzzify_maternal_age(v)['very_young'] for v in x],   '#7f1d1d'),
        ('Adolescent (fades by 20)', [fuzzify_maternal_age(v)['young'] for v in x], '#f59e0b'),
        ('Typical age context', [fuzzify_maternal_age(v)['normal'] for v in x], '#22c55e'),
        ('Older age (rises after 35)', [fuzzify_maternal_age(v)['advanced'] for v in x], '#f59e0b'),
        ('Very advanced age context', [fuzzify_maternal_age(v)['very_advanced'] for v in x], '#ef4444'),
    ], "Mother's Age Interpretation", "Age (years)", f"{chart_prefix}age_fuzzy.png", actual_values['age'])
    plots['age'] = f'static/{chart_prefix}age_fuzzy.png'

    if family_history_items:
        diseases = [item['disease'] for item in family_history_items]
        indices = [item['risk_index'] for item in family_history_items]
        fig, ax = plt.subplots(figsize=(max(7, len(diseases) * 1.6), 4.5))
        xi = np.arange(len(diseases))
        ax.bar(xi, indices, 0.5, label='Family-History Indicator', color='#6366f1', edgecolor='#4f46e5', alpha=0.9)
        ax.set_title("Family-History Indicator", fontsize=12, fontweight='bold')
        ax.set_ylabel('Risk Index (0-100)', fontsize=10)
        ax.set_xticks(xi); ax.set_xticklabels(diseases, rotation=30, ha='right', fontsize=10)
        ax.legend(fontsize=9)
        ax.grid(True, axis='y', alpha=0.3)
        fig.tight_layout()
        fig.savefig(os.path.join(static_dir, f'{chart_prefix}genetic_risks.png'), dpi=140, bbox_inches='tight', facecolor='#ffffff')
        plt.close(fig)
        plots['genetic'] = f'static/{chart_prefix}genetic_risks.png'
    else:
        plots['genetic'] = None

    def save_risk_output(levels, title, filename):
        x_risk, low_mf, mod_mf, high_mf, combined = risk_output_curves(levels)
        low_shape = np.clip((50 - x_risk) / 25, 0, 1)
        moderate_shape = np.clip(
            np.minimum((x_risk - 25) / 25, (75 - x_risk) / 25), 0, 1
        )
        high_shape = np.clip((x_risk - 50) / 25, 0, 1)
        denominator = simpson(combined, x=x_risk)
        centroid = (
            simpson(x_risk * combined, x=x_risk) / denominator
            if denominator > 0 else 0
        )

        fig, ax = plt.subplots(figsize=(11, 5))
        for label, shape, clipped, color in (
            ('Low', low_shape, low_mf, '#22c55e'),
            ('Moderate', moderate_shape, mod_mf, '#f59e0b'),
            ('High', high_shape, high_mf, '#ef4444'),
        ):
            level_key = label.lower()
            ax.plot(
                x_risk, shape, color=color, lw=1.4, linestyle=':', alpha=0.7,
                label=f'{label} membership',
            )
            ax.plot(
                x_risk, clipped, color=color, lw=2.2,
                label=f'{label} activation = {levels[level_key]:.2f}',
            )
            ax.fill_between(x_risk, 0, clipped, color=color, alpha=0.12)

        ax.plot(
            x_risk, combined, color='#38bdf8', lw=2.5, linestyle='--',
            label='Aggregated output',
        )
        ax.axvline(
            centroid, color='#111827', lw=2.5, linestyle='-.',
            label=f'Risk Index = {centroid:.1f} / 100',
        )
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel('Risk Index (0-100)', fontsize=11)
        ax.set_ylabel('Membership Degree (0-1)', fontsize=11)
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 1.08)
        ax.legend(
            loc='upper left', bbox_to_anchor=(1.02, 1), fontsize=8.5,
            framealpha=0.9,
        )
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        fig.savefig(
            os.path.join(static_dir, filename), dpi=150,
            bbox_inches='tight', facecolor='#ffffff',
        )
        plt.close(fig)
        return centroid

    if module_risk_levels:
        module_plots = (
            ('immediate', 'Immediate Condition Risk - Fuzzy Output', 'immediate'),
            ('birth', 'Birth-Related Monitoring - Fuzzy Output', 'birth'),
            ('family', 'Family-History Follow-up - Fuzzy Output', 'family'),
        )
        for plot_key, title, levels_key in module_plots:
            filename = f'{chart_prefix}{plot_key}_risk.png'
            save_risk_output(module_risk_levels[levels_key], title, filename)
            plots[plot_key] = f'static/{filename}'

    if final_risk_levels is not None:
        centroid = save_risk_output(final_risk_levels, 'Legacy combined output', f'{chart_prefix}final_risk.png')
        plots['final'] = f'static/{chart_prefix}final_risk.png'
    else:
        centroid = None
        plots['final'] = None
    return centroid, plots


def assess_risk(appearance, pulse, grimace, activity, respiration,
                birth_week, birth_weight_g, maternal_age, delivery_type, delivery_comp,
                family_history, child_gender, chart_prefix='', apgar_observations=None):
    if apgar_observations:
        validate_observation_records(apgar_observations)
        latest = max(apgar_observations, key=lambda o: o['minute'])
        appearance, pulse, grimace, activity, respiration = (latest['components'][k] for k in ('appearance', 'pulse', 'grimace', 'activity', 'respiration'))
    safety = check_apgar_safety(appearance, pulse, grimace, activity, respiration)
    normalized_gender = normalize_gender(child_gender)
    apgar_score, apgar_breakdown, apgar_category, apgar_severity, component_detail = \
        calculate_apgar(appearance, pulse, grimace, activity, respiration)

    fuzzy_inputs = {
        'apgar':        fuzzify_apgar(apgar_score),
        'birth_week':   fuzzify_birth_week(birth_week),
        'birth_weight': fuzzify_birth_weight(birth_weight_g),
        'maternal_age': fuzzify_maternal_age(maternal_age),
        'delivery_comp': fuzzify_delivery_comp(delivery_comp),
    }
    immediate_risk_levels, immediate_rules = apply_immediate_condition_rules(
        fuzzy_inputs, return_rules=True
    )
    birth_risk_levels, birth_rules = apply_birth_related_rules(
        fuzzy_inputs, return_rules=True
    )
    raw_immediate_risk_index = defuzzify_risk(immediate_risk_levels)
    if safety['active']:
        immediate_risk_levels = {'low': 0.0, 'moderate': 0.0, 'high': 1.0}
    immediate_condition_risk_index = defuzzify_risk(immediate_risk_levels)
    birth_related_risk_index = defuzzify_risk(birth_risk_levels)

    family_risk_levels, family_rules = apply_family_history_rules(
        family_history, return_rules=True
    )
    family_history_risk_index = defuzzify_risk(family_risk_levels)
    affected_relative_labels = {
        'father': 'Father',
        'mother': 'Mother',
        'both_parents': 'Both parents',
        'other_family_member': 'Other family member',
        'unknown': 'Unknown',
    }
    family_history_items = []
    if family_history.get('status') == 'yes':
        family_history_items.append({
            'disease': family_history.get('disease', ''),
            'affected_relative': affected_relative_labels.get(
                family_history.get('affected_relative'), 'Unknown'
            ),
            'risk_index': family_history_risk_index,
        })
    family_summary = family_history_message(family_history, family_history_risk_index)

    # Legacy database fields mirror immediate condition; no combined inference.
    final_risk_levels = dict(immediate_risk_levels)
    raw_final_risk_index = raw_immediate_risk_index
    overall_risk_index = immediate_condition_risk_index
    _, plot_paths = generate_visualizations(
        fuzzy_inputs, None,
        {'apgar': apgar_score, 'week': birth_week, 'weight': birth_weight_g, 'age': maternal_age},
        family_history_items, chart_prefix=chart_prefix,
        module_risk_levels={'immediate': immediate_risk_levels, 'birth': birth_risk_levels, 'family': family_risk_levels},
    )
    risk_level = risk_level_for_index(immediate_condition_risk_index)
    risk_color = risk_level.lower()
    recommendation = safety['action'] if safety['active'] else ''

    delivery_type_label = {
        'vaginal': 'Vaginal Delivery',
        'assisted': 'Assisted Delivery',
        'cesarean': 'Cesarean Section',
    }.get(delivery_type, str(delivery_type).title())
    delivery_complication = 'Yes' if delivery_comp == 1 else 'No'
    important_inputs_complete = all(value is not None for value in (
        appearance, pulse, grimace, activity, respiration, birth_week,
        birth_weight_g, maternal_age, delivery_type, delivery_comp, normalized_gender,
    )) and family_history.get('status') in ('yes', 'no', 'unknown')
    if family_history.get('status') == 'yes':
        important_inputs_complete = important_inputs_complete and bool(
            family_history.get('disease') and family_history.get('affected_relative')
        )
    confidence = calculate_assessment_confidence(
        immediate_risk_levels, important_inputs_complete, {'status': 'no'}
    )
    confidence['reasons'].append('This is heuristic immediate-rule clarity, not calibrated uncertainty, predictive accuracy or a probability. A safety override can make the rule separation High without establishing model validity.')
    main_factors, lower_impact_factors = identify_assessment_factors(
        fuzzy_inputs, family_history_risk_index, family_history, include_family=False
    )
    family_names = {'Known family disease', 'Family disease history is unknown', 'No known family disease'}
    main_factors = [f for f in main_factors if f['name'] not in family_names]
    lower_impact_factors = [f for f in lower_impact_factors if f['name'] not in family_names]
    triggered_rules = select_important_rules(
        immediate_rules + birth_rules + family_rules
    )
    user_guidance = build_user_guidance(
        risk_level, main_factors, lower_impact_factors
    )
    if safety['active']:
        main_factors = [{'name': alert['reason'], 'description': safety['action'],
                        'role': 'impact', 'strength': 1.0} for alert in safety['alerts']] + main_factors
        lower_impact_factors = [f for f in lower_impact_factors if f['name'] != 'Stable APGAR pattern']
        triggered_rules = [{'id': a['id'], 'module': 'Safety override', 'name': a['reason'],
                            'description': safety['action'], 'outcome': 'high',
                            'activation': 1.0} for a in safety['alerts']] + triggered_rules
        user_guidance['short_summary'] = 'Urgent component alert: immediate professional assessment required.'
        user_guidance['main_notices'] = [a['reason'] for a in safety['alerts']]
        user_guidance['next_steps'] = [safety['action']]
    immediate_level = risk_level_for_index(immediate_condition_risk_index)
    birth_level = risk_level_for_index(birth_related_risk_index)
    birth_monitoring = explain_birth_monitoring(birth_week, birth_weight_g, maternal_age, delivery_comp,
                                               fuzzy_inputs, birth_rules, birth_related_risk_index, birth_level)
    if safety['active'] or any(n['urgency'] == 'urgent' for n in safety['notices']) or immediate_level == 'High':
        triage = 'Urgent evaluation'
    elif safety['notices'] or immediate_level == 'Moderate':
        triage = 'Closer monitoring and professional review'
    else:
        triage = 'Routine care and observation'
    if not safety['active']:
        recommendation = {
            'Urgent evaluation': 'Seek urgent professional evaluation of the baby’s current condition.',
            'Closer monitoring and professional review': 'Arrange neonatal professional review and a monitoring plan for the immediate or birth-related concerns.',
            'Routine care and observation': 'Continue routine newborn care and observation; seek professional help for new symptoms.',
        }[triage]
    if safety['notices'] and not safety['active']:
        recommendation = ' '.join(n['action'] for n in sorted(safety['notices'], key=lambda n: n['urgency'] != 'urgent'))
    family_follow_up = {
        'yes': 'Share the reported condition and affected relatives with the baby’s clinician. Discuss whether genetic counselling or disease-specific screening is appropriate; family history alone does not diagnose the baby.',
        'unknown': 'Clarify family history with relatives and the baby’s clinician. Unknown history does not establish low inherited risk.',
        'no': 'No additional referral is suggested by the reported family history alone. Continue routine newborn screening and share any newly discovered history with the clinician.',
    }[family_history['status']]
    family_follow_up_level = ('Unknown' if family_history['status'] == 'unknown'
                              else risk_level_for_index(family_history_risk_index))
    for notice in safety['notices']:
        main_factors.insert(0, {'name': notice['reason'], 'description': notice['action'], 'role': 'impact', 'strength': 1.0})
        user_guidance['main_notices'].insert(0, notice['reason'])
    user_guidance['short_summary'] = triage
    user_guidance['next_steps'] = [recommendation]
    conclusion = (f"Immediate-condition action: {triage}. {apgar_breakdown}. "
                  f"Birth at {birth_week}w, weight {birth_weight_g:.0f}g, "
                  f"mother age {maternal_age}, child gender: {normalized_gender}, "
                  f"delivery: {delivery_type_label}, delivery complication: {delivery_complication}. "
                  f"Immediate Condition Risk Index: {immediate_condition_risk_index:.1f} / 100. "
                  f"Birth-Related Monitoring Index: {birth_related_risk_index:.1f} / 100. "
                  f"Family-History Follow-up Index: {family_history_risk_index:.1f} / 100. "
                  f"Family follow-up: {family_follow_up}. "
                  f"Rule clarity (heuristic): {confidence['level']}. {recommendation}")

    timeline = []
    for observation in sorted(apgar_observations or [], key=lambda o: o['minute']):
        components = observation['components']
        total, breakdown, category, severity, _ = calculate_apgar(**components)
        checks = check_apgar_safety(**components)
        levels = apply_immediate_condition_rules({'apgar': fuzzify_apgar(total), 'delivery_comp': fuzzify_delivery_comp(delivery_comp)})
        if checks['active']:
            levels = {'low': 0.0, 'moderate': 0.0, 'high': 1.0}
        index = defuzzify_risk(levels)
        urgent = checks['active'] or any(n['urgency'] == 'urgent' for n in checks['notices']) or risk_level_for_index(index) == 'High'
        needs_review = bool(checks['notices']) or risk_level_for_index(index) == 'Moderate'
        action_label = 'Urgent evaluation' if urgent else 'Professional review' if needs_review else 'Routine observation'
        action_text = (checks['action'] if checks['active'] else ' '.join(n['action'] for n in checks['notices']) if checks['notices'] else
                       'Seek urgent neonatal clinical evaluation.' if urgent else
                       'Review this observation and reported delivery complication with the neonatal clinician.' if needs_review else
                       'Continue routine observation appropriate to the clinical context.')
        timeline.append({**observation, 'immediate_level': risk_level_for_index(index), 'action_label': action_label, 'action': action_text, 'total': total, 'category': category, 'severity': severity,
                         'notices': checks['notices'], 'alerts': checks['alerts'],
                         'immediate_index': defuzzify_risk(levels)})
    five = next((o for o in timeline if o['minute'] == 5), None)
    repeat_suggested = bool(five and five['total'] < 7)
    repeat_message = ''
    repeat_status = 'not_indicated'
    if repeat_suggested:
        latest_time = timeline[-1]['minute']
        next_time = next((t for t in (10, 15, 20) if t > latest_time), None)
        if latest_time > 5 and timeline[-1]['total'] >= 7:
            repeat_status = 'recorded_improvement'
            repeat_message = 'Repeat scoring was indicated by the 5-minute total below 7. The latest recorded total is now at least 7; ongoing assessment remains the clinician’s decision.'
        elif next_time:
            repeat_status = 'suggested'
            repeat_message = f'The 5-minute APGAR total was below 7. Record a fresh observation at {next_time} minutes after birth, and further scoring up to 20 minutes as clinically indicated. Do not delay clinical care.'
        else:
            repeat_status = 'window_complete'
            repeat_message = 'The 5-minute APGAR total was below 7. The 20-minute observation is recorded; further evaluation is determined by the clinical team.'
    first = next((o for o in timeline if o['minute'] == 1), None)
    trend = ('Not available: 1-minute observation not recorded' if not first else
             'Total improved' if timeline[-1]['total'] > first['total'] else
             'Total decreased' if timeline[-1]['total'] < first['total'] else 'Total unchanged') if timeline else 'Untimed observation'
    if timeline:
        conclusion = (f"Recorded APGAR timeline: {' → '.join(str(o['minute']) + ' min ' + str(o['total']) + '/10' for o in timeline)}. "
                      f"{trend}. Latest recorded observation: {timeline[-1]['minute']} minutes after birth. "
                      'This historical observation does not establish the baby’s condition now. ' + conclusion)
    recorded_text = '; '.join(f"{o['minute']} minutes: APGAR {o['total']}/10" for o in timeline)
    immediate_observation_summary = (
        (f"Recorded observations: {recorded_text}. {trend}. The latest complete observation at {timeline[-1]['minute']} minutes supplies the immediate inference input. " if timeline else f"Untimed observation: APGAR {apgar_score}/10. ")
        + f"Final immediate-condition index: {immediate_condition_risk_index:.1f}/100 ({immediate_level}). Recommended action: {triage}. {recommendation}"
        + (' Earlier component concerns remain documented; score improvement does not establish their clinical resolution.' if any(o['alerts'] or o['notices'] for o in timeline[:-1]) else '')
        + ' This describes recorded findings, not continuous monitoring or a diagnosis.'
    )
    immediate_facts = [
        f"{o['minute']} minutes: APGAR {o['total']}/10; support/resuscitation: {o.get('support', 'unknown')}." for o in timeline
    ] or [f"Untimed observation: APGAR {apgar_score}/10."]
    if timeline:
        immediate_facts.append(f"{trend}. Inference uses the latest complete {timeline[-1]['minute']}-minute observation, without averaging scores.")
    immediate_facts.append(f"Final immediate-condition index: {immediate_condition_risk_index:.1f}/100 ({immediate_level}). Action priority: {triage}.")
    if safety['active']:
        alert_facts = '; '.join(f"{a['component'].title()} {a['score']}/2: {a['reason']}" for a in safety['alerts'])
        immediate_facts.append(f"Reason for High: component safety override — {alert_facts}. The APGAR total alone did not set High; this numeric override is a conservative project policy, not a guideline-defined probability.")
    else:
        immediate_facts.append(f"No heartbeat/breathing safety override. The immediate index comes from APGAR {apgar_score}/10 and {'a reported' if delivery_comp else 'no reported'} delivery complication; component notices can separately change the action priority.")
    immediate_concerns = [a['reason'] for a in safety['alerts']] + [n['reason'] for n in safety['notices']]
    if delivery_comp:
        immediate_concerns.append('A delivery complication was reported; review it with the recorded APGAR findings.')
    if any(o['alerts'] or o['notices'] for o in timeline[:-1]):
        immediate_concerns.append('Earlier component concerns remain documented; improvement in the total does not confirm their clinical resolution.')
    if not immediate_concerns:
        immediate_concerns.append('No component safety alert is triggered by the latest recorded scores; continue direct clinical observation.')
    immediate_actions = [recommendation]
    if repeat_message:
        immediate_actions.append(repeat_message)
    module_actions = [
        {'module': 'Immediate condition', 'level': immediate_level, 'priority': triage, 'action': recommendation},
        {'module': 'Birth-related monitoring', 'level': birth_level,
         'priority': birth_monitoring['priority'],
         'action': ' '.join(birth_monitoring['actions'])},
        {'module': 'Family-history follow-up', 'level': family_follow_up_level, 'priority': 'Family-history plan', 'action': family_follow_up},
    ]
    return {
        'immediate_observation_summary': immediate_observation_summary,
        'birth_monitoring': birth_monitoring,
        'immediate_facts': immediate_facts,
        'immediate_care_concerns': immediate_concerns,
        'immediate_recommended_actions': immediate_actions,
        'module_actions': module_actions,
        'apgar_timeline': timeline,
        'apgar_trend': trend,
        'apgar_reference_minute': timeline[-1]['minute'] if timeline else None,
        'repeat_observations_suggested': repeat_status == 'suggested',
        'repeat_scoring_indicated_at_five': repeat_suggested,
        'repeat_observation_status': repeat_status,
        'repeat_observation_message': repeat_message,
        'assessment_semantics': 'separate-v3',
        'assessment_policy_version': 'fuzzy-v6-birth-monitoring',
        'inference_input_summary': {
            'reference_minute': timeline[-1]['minute'] if timeline else None,
            'components': {'appearance': appearance, 'pulse': pulse, 'grimace': grimace, 'activity': activity, 'respiration': respiration},
            'apgar_total': apgar_score,
            'delivery_complication': delivery_comp,
            'birth_week': birth_week, 'birth_weight_g': birth_weight_g, 'maternal_age': maternal_age,
        },
        'assessment_notices': safety['notices'],
        'overall_triage': triage,
        'family_history_follow_up': family_follow_up,
        'family_history_follow_up_level': family_follow_up_level,
        'safety_override': safety,
        'unoverridden_immediate_risk_index': raw_immediate_risk_index,
        'unoverridden_final_risk_index': raw_final_risk_index,
        'immediate_condition_risk_index': immediate_condition_risk_index,
        'birth_related_risk_index': birth_related_risk_index,
        'family_history_risk_index': family_history_risk_index,
        'overall_risk_index': overall_risk_index,
        'immediate_condition_risk_level': risk_level_for_index(immediate_condition_risk_index),
        'birth_related_risk_level': risk_level_for_index(birth_related_risk_index),
        'family_history_risk_level': risk_level_for_index(family_history_risk_index),
        'immediate_risk_levels': immediate_risk_levels,
        'birth_risk_levels': birth_risk_levels,
        'family_risk_levels': family_risk_levels,
        'final_risk_levels': final_risk_levels,
        'confidence_level': confidence['level'],
        'confidence_reasons': confidence['reasons'],
        'confidence_details': confidence,
        'main_contributing_factors': main_factors,
        'lower_impact_factors': lower_impact_factors,
        'triggered_rules': triggered_rules,
        'user_guidance': user_guidance,
        'apgar_score': apgar_score,
        'apgar_category': apgar_category,
        'apgar_severity': apgar_severity,
        'apgar_breakdown': apgar_breakdown,
        'component_detail': component_detail,
        'family_history': family_history,
        'family_history_items': family_history_items,
        'family_history_summary': family_summary,
        'conclusion': conclusion,
        'risk_level': risk_level,
        'risk_color': risk_color,
        'recommendation': recommendation,
        'plot_paths': plot_paths,
        'birth_week': birth_week,
        'birth_weight_g': birth_weight_g,
        'maternal_age': maternal_age,
        'child_gender': normalized_gender,
        'delivery_type': delivery_type_label,
        'delivery_complication': delivery_complication,
    }
