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
        0: ("Blue/Pale all over", "Concerning — the baby's skin is pale or blue, indicating oxygen may not be circulating well."),
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
    apgar = min(max(appearance + pulse + grimace + activity + respiration, 0), 10)
    if apgar >= 7:
        category = "Normal (7–10)"
        summary = "Baby is in good health."
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
        'low':    trapezoidal_mf(apgar, 0, 0, 3, 4),
        'medium': trapezoidal_mf(apgar, 3, 4, 6, 7),
        'high':   trapezoidal_mf(apgar, 6, 7, 10, 10),
    }

def fuzzify_birth_week(week):
    return {
        'very_preterm': trapezoidal_mf(week, 0, 0, 28, 32),
        'preterm':      trapezoidal_mf(week, 28, 32, 34, 37),
        'term':         trapezoidal_mf(week, 35, 37, 40, 42),
        'postterm':     trapezoidal_mf(week, 40, 42, 44, 50),
    }

def fuzzify_birth_weight(w):
    ext_low  = trapezoidal_mf(w, 0, 0, 800, 1000)
    very_low = trapezoidal_mf(w, 800, 1000, 1200, 1500)
    low      = trapezoidal_mf(w, 1200, 1500, 2000, 2500)
    normal   = trapezoidal_mf(w, 2000, 2500, 3500, 4000)
    high     = trapezoidal_mf(w, 3500, 4000, 4500, 5000)
    very_high= trapezoidal_mf(w, 4500, 5000, 6000, 6000)
    return {
        'extremely_low': ext_low, 'very_low': very_low, 'low': low,
        'normal': normal, 'high': high, 'very_high': very_high,
        'any_low': max(ext_low, very_low, low),
        'any_high': max(high, very_high),
    }

def fuzzify_maternal_age(age):
    vy = trapezoidal_mf(age, 0, 0, 15, 18)
    y  = trapezoidal_mf(age, 15, 18, 22, 25)
    n  = trapezoidal_mf(age, 22, 25, 30, 35)
    a  = trapezoidal_mf(age, 30, 35, 40, 45)
    va = trapezoidal_mf(age, 40, 45, 60, 60)
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
        'explanation': 'One affected parent with dominant inheritance usually gives around a 50% risk.',
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
        'explanation': 'Classic recessive pattern: if both parents are carriers, risk is about 25%.',
    },
    'recessive_one_parent_carrier': {
        'label': 'Recessive: only one parent is a carrier',
        'base_prob': 0.03,
        'parent_signal': 0.3,
        'grandparent_signal': 0.0,
        'explanation': 'One carrier parent alone usually means very low chance of an affected baby.',
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
    return 'unknown'

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
            reason = 'Mother is a carrier, so each child has about a 50% chance to inherit the mutation.'
            parent_signal = 0.7
    else:
        if s == 'carrier':
            base_prob = 0.5 if g == 'unknown' else (1.0 if g == 'female' else 0.0)
            reason = 'Father cannot be a typical carrier in X-linked recessive patterns; treated as affected for inheritance probability.'
            parent_signal = 0.75
        else:
            base_prob = 0.5 if g == 'unknown' else (1.0 if g == 'female' else 0.0)
            reason = 'Affected father passes his X chromosome to daughters and Y chromosome to sons.'
            parent_signal = 0.75

    gender_note = {
        'male': 'Child gender is male, so paternal X transmission is not possible.',
        'female': 'Child gender is female, so paternal X transmission applies.',
        'unknown': 'Child gender is unknown, so male/female outcomes are averaged.',
    }[g]
    return base_prob, parent_signal, reason, gender_note

def estimate_inherited_prob(diseases, child_gender='unknown'):
    probs_list = []
    explanations = []
    for d in diseases:
        mode_key = d.get('mode', 'unknown')
        info = INHERITANCE_MODES.get(mode_key, INHERITANCE_MODES['unknown'])
        base_prob = info['base_prob']
        parent_signal = info.get('parent_signal', 0.2)
        gp_signal = info.get('grandparent_signal', 0.2)
        mode_explanation = info['explanation']

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

        fuzzy_levels = apply_genetic_rules(
            base_prob,
            parent_signal,
            gp_signal,
        )
        fuzzy_prob = defuzzify_genetic_risk(fuzzy_levels, base_prob)
        probs_list.append({
            'disease': d['disease'],
            'base_prob': base_prob,
            'fuzzy_prob': fuzzy_prob,
            'expl': (
                f"{d['disease']}: {mode_explanation} "
                f"Base estimate {base_prob*100:.0f}% adjusted by fuzzy family-history rules "
                f"to {fuzzy_prob*100:.1f}%."
            ),
            'mode_label': info['label'],
        })
        explanations.append(
            f"{d['disease']}: {mode_explanation} "
            f"(base {base_prob*100:.0f}%, fuzzy-adjusted {fuzzy_prob*100:.1f}%)."
        )
    explanation = "; ".join(explanations) if explanations else "No inherited diseases noted."
    return probs_list, explanation

 
def apply_rules(fi):
    apgar  = fi['apgar']
    week   = fi['birth_week']
    weight = fi['birth_weight']
    age    = fi['maternal_age']
    comp   = fi['delivery_comp']

    high_rules = [
        apgar['low'],
        min(apgar['low'], week['preterm']),
        min(apgar['low'], week['very_preterm']),
        min(apgar['low'], weight['any_low']),
        min(apgar['low'], comp['complicated']),
        min(apgar['low'], age['any_young']),
        min(apgar['low'], age['any_advanced']),
        min(apgar['medium'], week['preterm'], comp['complicated']),
        min(apgar['medium'], weight['extremely_low']),
        min(apgar['medium'], week['very_preterm']),
        week['very_preterm'],
        min(week['very_preterm'], weight['any_low']),
        min(week['preterm'], weight['any_low']),
        min(week['preterm'], comp['complicated']),
        min(week['very_preterm'], comp['complicated']),
        min(week['postterm'], comp['complicated']),
        min(week['postterm'], weight['any_high']),
        weight['extremely_low'],
        weight['very_low'],
        weight['very_high'],
        min(weight['any_high'], week['preterm']),
        min(weight['any_low'], comp['complicated']),
        age['very_advanced'],
        min(age['advanced'], comp['complicated']),
        min(age['very_young'], comp['complicated']),
        min(age['any_advanced'], apgar['low']),
        min(age['advanced'], weight['any_high']),
        min(age['any_young'], week['preterm']),
        min(apgar['low'], week['very_preterm'], weight['any_low']),
        min(apgar['medium'], week['preterm'], weight['low'], comp['complicated']),
    ]
    high_risk = max(high_rules)

    low_rules = [
        min(apgar['high'], week['term'], weight['normal'], comp['normal']),
        min(apgar['high'], week['term']),
        min(apgar['high'], comp['normal']),
        min(apgar['high'], age['normal']),
        min(apgar['high'], weight['normal']),
        min(apgar['medium'], week['term'], weight['normal'], comp['normal']),
        min(age['normal'], comp['normal'], week['term'], weight['normal']),
        min(week['term'], comp['normal'], age['normal']),
        min(weight['normal'], age['normal'], comp['normal']),
        min(week['term'], weight['normal']),
    ]
    low_risk = max(low_rules)
    mod_risk = max(0, 1 - (high_risk + low_risk) / 2)
    return {'low': low_risk, 'moderate': mod_risk, 'high': high_risk}

def generate_visualizations(fuzzy_inputs, risk_levels, actual_values, inherited_probs_list):
    static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    os.makedirs(static_dir, exist_ok=True)
    plots = {}

    plt.rcParams.update({
        'font.family': 'DejaVu Sans', 'axes.spines.top': False, 'axes.spines.right': False,
        'figure.facecolor': '#0f172a', 'axes.facecolor': '#1e293b',
        'axes.labelcolor': '#94a3b8', 'xtick.color': '#64748b', 'ytick.color': '#64748b',
        'axes.titlecolor': '#e2e8f0', 'grid.color': '#334155',
        'text.color': '#e2e8f0', 'legend.facecolor': '#1e293b', 'legend.edgecolor': '#334155',
    })

    def save_fig(x_range, curves_data, title, xlabel, filename, user_val):
        fig, ax = plt.subplots(figsize=(7, 3.5))
        for label, vals, color in curves_data:
            ax.plot(x_range, vals, label=label, color=color, linewidth=2)
            ax.fill_between(x_range, 0, vals, alpha=0.07, color=color)
        if user_val is not None:
            ax.axvline(user_val, color='#f8fafc', linestyle='--', linewidth=2.5, label=f'Your value: {user_val}', zorder=5)
        ax.set_title(title, fontsize=12, fontweight='bold', pad=10)
        ax.set_xlabel(xlabel, fontsize=10)
        ax.set_ylabel('Membership (0–1)', fontsize=10)
        ax.legend(fontsize=8, loc='upper right')
        ax.grid(True, alpha=0.3)
        ax.set_ylim(0, 1.15)
        fig.savefig(os.path.join(static_dir, filename), dpi=140, bbox_inches='tight', facecolor='#0f172a')
        plt.close(fig)

    x = np.linspace(0, 10, 500)
    save_fig(x, [
        ('Low (0–3)',    [trapezoidal_mf(v,0,0,3,4) for v in x],     '#ef4444'),
        ('Medium (4–6)', [trapezoidal_mf(v,3,4,6,7) for v in x],    '#f59e0b'),
        ('High (7–10)', [trapezoidal_mf(v,6,7,10,10) for v in x],   '#22c55e'),
    ], "Baby's APGAR Score Interpretation", "APGAR Score (0–10)", "apgar_fuzzy.png", actual_values['apgar'])
    plots['apgar'] = 'static/apgar_fuzzy.png'

    x = np.linspace(20, 46, 500)
    save_fig(x, [
        ('Very Preterm (<28w)', [trapezoidal_mf(v,0,0,28,32) for v in x],    '#7f1d1d'),
        ('Preterm (28–37w)',    [trapezoidal_mf(v,28,32,34,37) for v in x],  '#ef4444'),
        ('Term (37–42w)',       [trapezoidal_mf(v,35,37,40,42) for v in x],  '#22c55e'),
        ('Post-term (>42w)',    [trapezoidal_mf(v,40,42,44,50) for v in x],  '#f59e0b'),
    ], "Gestational Age Interpretation", "Weeks of Pregnancy", "week_fuzzy.png", actual_values['week'])
    plots['week'] = 'static/week_fuzzy.png'

    x = np.linspace(400, 5500, 500)
    save_fig(x, [
        ('Extremely Low (<1kg)', [trapezoidal_mf(v,0,0,800,1000) for v in x],      '#7f1d1d'),
        ('Very Low (1–1.5kg)',   [trapezoidal_mf(v,800,1000,1200,1500) for v in x],'#ef4444'),
        ('Low (1.5–2.5kg)',      [trapezoidal_mf(v,1200,1500,2000,2500) for v in x],'#f97316'),
        ('Normal (2.5–4kg)',     [trapezoidal_mf(v,2000,2500,3500,4000) for v in x],'#22c55e'),
        ('High (4–4.5kg)',       [trapezoidal_mf(v,3500,4000,4500,5000) for v in x],'#f59e0b'),
        ('Very High (>4.5kg)',   [trapezoidal_mf(v,4500,5000,6000,6000) for v in x],'#ef4444'),
    ], "Birth Weight Interpretation", "Weight (grams)", "weight_fuzzy.png", actual_values['weight'])
    plots['weight'] = 'static/weight_fuzzy.png'

    x = np.linspace(12, 55, 500)
    save_fig(x, [
        ('Very Young (<15)',    [trapezoidal_mf(v,0,0,15,18) for v in x],   '#7f1d1d'),
        ('Young (15–22)',       [trapezoidal_mf(v,15,18,22,25) for v in x], '#f59e0b'),
        ('Optimal (22–35)',     [trapezoidal_mf(v,22,25,30,35) for v in x], '#22c55e'),
        ('Advanced (35–45)',    [trapezoidal_mf(v,30,35,40,45) for v in x], '#f59e0b'),
        ('Very Advanced (>45)', [trapezoidal_mf(v,40,45,60,60) for v in x], '#ef4444'),
    ], "Mother's Age Interpretation", "Age (years)", "age_fuzzy.png", actual_values['age'])
    plots['age'] = 'static/age_fuzzy.png'

    if inherited_probs_list:
        diseases = [p['disease'] for p in inherited_probs_list]
        base  = [p['base_prob']  * 100 for p in inherited_probs_list]
        fuzzy = [p['fuzzy_prob'] * 100 for p in inherited_probs_list]
        fig, ax = plt.subplots(figsize=(max(7, len(diseases) * 1.6), 4.5))
        xi = np.arange(len(diseases))
        w = 0.35
        ax.bar(xi-w/2, base,  w, label='Base Probability',  color='#38bdf8', edgecolor='#0ea5e9')
        ax.bar(xi+w/2, fuzzy, w, label='With Uncertainty',   color='#6366f1', edgecolor='#4f46e5', alpha=0.9)
        ax.set_title("Inherited / Genetic Risk per Condition", fontsize=12, fontweight='bold')
        ax.set_ylabel('Probability (%)', fontsize=10)
        ax.set_xticks(xi); ax.set_xticklabels(diseases, rotation=30, ha='right', fontsize=10)
        ax.legend(fontsize=9)
        ax.grid(True, axis='y', alpha=0.3)
        fig.tight_layout()
        fig.savefig(os.path.join(static_dir, 'genetic_risks.png'), dpi=140, bbox_inches='tight', facecolor='#0f172a')
        plt.close(fig)
        plots['genetic'] = 'static/genetic_risks.png'
    else:
        plots['genetic'] = None

    x_risk = np.linspace(0, 100, 1000)
    low_mf  = np.clip(np.minimum((30-x_risk)/30, risk_levels['low']), 0, None)
    mod_mf  = np.clip(np.minimum(np.minimum((x_risk-20)/30,(80-x_risk)/30), risk_levels['moderate']), 0, None)
    high_mf = np.clip(np.minimum((x_risk-60)/40, risk_levels['high']), 0, None)
    combined = np.maximum(low_mf, np.maximum(mod_mf, high_mf))
    denom = simpson(combined, x=x_risk)
    centroid = simpson(x_risk*combined, x=x_risk)/denom if denom>0 else 0
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(x_risk, low_mf,   color='#22c55e', lw=2, label='Low Risk zone')
    ax.plot(x_risk, mod_mf,   color='#f59e0b', lw=2, label='Moderate Risk zone')
    ax.plot(x_risk, high_mf,  color='#ef4444', lw=2, label='High Risk zone')
    ax.plot(x_risk, combined, color='#38bdf8', lw=2.5, linestyle='--', label='Combined Output')
    ax.axvline(centroid, color='#f8fafc', lw=3, linestyle='--', label=f'Your Risk Score = {centroid:.1f}%')
    ax.fill_between(x_risk, 0, combined, color='#38bdf8', alpha=0.07)
    ax.set_title("Final Risk Score — Fuzzy Logic Defuzzification", fontsize=14, fontweight='bold')
    ax.set_xlabel("Risk Level (%)   |   0% = very safe   ·   100% = very high risk", fontsize=11)
    ax.set_ylabel("Fuzzy Strength (0–1)", fontsize=11)
    ax.legend(loc='upper left', bbox_to_anchor=(1.02,1), fontsize=9.5, framealpha=0.9)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(static_dir, 'final_risk.png'), dpi=150, bbox_inches='tight', facecolor='#0f172a')
    plt.close(fig)
    plots['final'] = 'static/final_risk.png'

    return centroid, plots

def assess_risk(appearance, pulse, grimace, activity, respiration,
                birth_week, birth_weight_g, maternal_age, delivery_comp, inherited_diseases,
                child_gender='unknown'):
    apgar_score, apgar_breakdown, apgar_category, apgar_severity, component_detail = \
        calculate_apgar(appearance, pulse, grimace, activity, respiration)

    fuzzy_inputs = {
        'apgar':        fuzzify_apgar(apgar_score),
        'birth_week':   fuzzify_birth_week(birth_week),
        'birth_weight': fuzzify_birth_weight(birth_weight_g),
        'maternal_age': fuzzify_maternal_age(maternal_age),
        'delivery_comp': fuzzify_delivery_comp(delivery_comp),
    }
    risk_levels = apply_rules(fuzzy_inputs)
    inherited_probs_list, inherited_explanation = estimate_inherited_prob(inherited_diseases, child_gender)
    inherited_prob = np.mean([p['fuzzy_prob'] for p in inherited_probs_list]) if inherited_probs_list else 0.0

    overall_risk_prob, plot_paths = generate_visualizations(
        fuzzy_inputs, risk_levels,
        {'apgar': apgar_score, 'week': birth_week, 'weight': birth_weight_g, 'age': maternal_age},
        inherited_probs_list
    )

    total_risk = 0.7 * overall_risk_prob + 0.3 * inherited_prob * 100

    if total_risk < 30:
        risk_level, risk_color = "Low", "low"
        recommendation = "Based on the assessment, your baby appears to be in good health. Routine check-ups are recommended to monitor development."
    elif total_risk < 70:
        risk_level, risk_color = "Moderate", "moderate"
        recommendation = "Some factors require attention. Please consult your doctor for further evaluation and possibly additional tests."
    else:
        risk_level, risk_color = "High", "high"
        recommendation = "The assessment indicates significant risk factors. Immediate medical attention is strongly advised."

    delivery_type = "Normal Vaginal Delivery" if delivery_comp == 0 else "Cesarean Section"
    conclusion = (f"{risk_level} health risk. {apgar_breakdown}. "
                  f"Birth at {birth_week}w, weight {birth_weight_g:.0f}g, "
                  f"mother age {maternal_age}, child gender: {normalize_gender(child_gender)}, delivery: {delivery_type}. "
                  f"Birth-factor risk: {overall_risk_prob:.1f}%. "
                  f"Inherited risk: {inherited_prob*100:.1f}%. "
                  f"Total: {total_risk:.1f}%. {recommendation}")

    return {
        'overall_risk_probability': overall_risk_prob,
        'inherited_disease_probability': inherited_prob * 100,
        'total_risk_probability': total_risk,
        'apgar_score': apgar_score,
        'apgar_category': apgar_category,
        'apgar_severity': apgar_severity,
        'apgar_breakdown': apgar_breakdown,
        'component_detail': component_detail,
        'inherited_probs_list': inherited_probs_list,
        'inherited_explanation': inherited_explanation,
        'conclusion': conclusion,
        'risk_level': risk_level,
        'risk_color': risk_color,
        'recommendation': recommendation,
        'plot_paths': plot_paths,
        'birth_week': birth_week,
        'birth_weight_g': birth_weight_g,
        'maternal_age': maternal_age,
        'child_gender': normalize_gender(child_gender),
        'delivery_type': delivery_type,
    }

