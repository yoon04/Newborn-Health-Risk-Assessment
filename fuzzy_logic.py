import numpy as np
from scipy.integrate import simpson
import matplotlib.pyplot as plt
import os

def triangular_mf(x, a, b, c):
    if x <= a or x >= c:
        return 0.0
    elif a < x <= b:
        return (x - a) / (b - a)
    else:
        return (c - x) / (c - b)

def trapezoidal_mf(x, a, b, c, d):
    if x < a or x > d:
        return 0.0
    elif a <= x < b:
        return (x - a) / (b - a) if b > a else 1.0
    elif b <= x <= c:
        return 1.0
    elif c < x <= d:
        return (d - x) / (d - c) if d > c else 1.0
    return 0.0

def calculate_apgar(appearance, pulse, grimace, activity, respiration):
    apgar = appearance + pulse + grimace + activity + respiration
    apgar = min(max(apgar, 0), 10)
    
    if apgar >= 7:
        category = "Normal (7-10) - Baby is in good health."
    elif apgar >= 4:
        category = "Moderately abnormal (4-6) - May need some intervention like oxygen."
    else:
        category = "Low (0-3) - Requires immediate medical attention."
    
    breakdown = (
        f"APGAR Score: {apgar}/10 ({category}) "
        f"(Appearance: {appearance}/2 - skin color; "
        f"Pulse: {pulse}/2 - heart rate; "
        f"Grimace: {grimace}/2 - reflex; "
        f"Activity: {activity}/2 - muscle tone; "
        f"Respiration: {respiration}/2 - breathing)"
    )
    return apgar, breakdown

def fuzzify_apgar(apgar):
    low = trapezoidal_mf(apgar, 0, 0, 3, 4)
    medium = trapezoidal_mf(apgar, 3, 4, 6, 7)
    high = trapezoidal_mf(apgar, 6, 7, 10, 10)
    return {'low': low, 'medium': medium, 'high': high}

def fuzzify_birth_week(week):
    preterm = trapezoidal_mf(week, 0, 28, 34, 37)
    term = trapezoidal_mf(week, 35, 37, 40, 42)
    postterm = trapezoidal_mf(week, 40, 42, 44, 50)
    return {'preterm': preterm, 'term': term, 'postterm': postterm}

def fuzzify_birth_weight(weight):
    low = trapezoidal_mf(weight, 0, 500, 1500, 2500)
    normal = trapezoidal_mf(weight, 2000, 2500, 3500, 4000)
    high = trapezoidal_mf(weight, 3500, 4000, 5000, 6000)
    return {'low': low, 'normal': normal, 'high': high}

def fuzzify_maternal_age(age):
    young = trapezoidal_mf(age, 0, 10, 18, 25)
    normal = trapezoidal_mf(age, 20, 25, 30, 35)
    advanced = trapezoidal_mf(age, 30, 35, 45, 60)
    return {'young': young, 'normal': normal, 'advanced': advanced}

<<<<<<< Updated upstream
def fuzzify_delivery_comp(delivery_comp):
    normal = triangular_mf(delivery_comp, 0, 0, 0.5)
    complicated = triangular_mf(delivery_comp, 0.5, 1, 1)
    return {'normal': normal, 'complicated': complicated}
=======
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
>>>>>>> Stashed changes

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
<<<<<<< Updated upstream
        name = d['disease'].lower()
        mode = d.get('mode', 'complex')
        carriers = d.get('carriers', 0)
        if name in ['heart disease', 'diabetes']:
            base_prob = 0.1
            expl = f"{d['disease']}: ~10% chance (complex inheritance, lifestyle factors)."
        elif name == 'hemoglobin e':
            base_prob = 0.25 if carriers == 2 else 0.0
            expl = f"{d['disease']}: {base_prob*100}% chance (recessive)."
        elif name == 'congenital deaf':
            base_prob = 0.5
            expl = f"{d['disease']}: 50% chance (dominant)."
        elif name == 'muscular dystrophy':
            base_prob = 0.25 if carriers == 2 else 0.0
            expl = f"{d['disease']}: {base_prob*100}% chance (recessive/X-linked)."
        else:
            base_prob = 0.1
            expl = f"{d['disease']}: ~10% chance (default complex)."
        fuzzy_prob = triangular_mf(base_prob, 0, 0.5, 1)
=======
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
>>>>>>> Stashed changes
        probs_list.append({
            'disease': d['disease'],
            'base_prob': base_prob,
            'fuzzy_prob': fuzzy_prob,
<<<<<<< Updated upstream
            'expl': expl
        })
        explanations.append(expl)
=======
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
>>>>>>> Stashed changes
    explanation = "; ".join(explanations) if explanations else "No inherited diseases noted."
    return probs_list, explanation

def apply_rules(fuzzy_inputs):
    apgar = fuzzy_inputs['apgar']
    week = fuzzy_inputs['birth_week']
    weight = fuzzy_inputs['birth_weight']
    age = fuzzy_inputs['maternal_age']
    comp = fuzzy_inputs['delivery_comp']
    # High risk rules (15)
    high_risk1 = min(apgar['low'], week['preterm'], weight['low'])
    high_risk2 = min(age['advanced'], comp['complicated'])
    high_risk3 = min(week['postterm'], comp['complicated'])
    high_risk4 = min(apgar['low'], age['young'])
    high_risk5 = min(weight['high'], week['preterm'])
    high_risk6 = min(apgar['medium'], comp['complicated'])
    high_risk7 = min(week['preterm'], age['advanced'])
    high_risk8 = min(weight['low'], apgar['medium'])
    high_risk9 = min(week['postterm'], weight['high'])
    high_risk10 = min(comp['complicated'], age['young'], apgar['low'])
    high_risk11 = min(week['preterm'], comp['complicated'])
    high_risk12 = min(weight['low'], comp['complicated'])
    high_risk13 = min(apgar['low'], week['postterm'])
    high_risk14 = min(age['advanced'], weight['high'])
    high_risk15 = min(apgar['medium'], week['preterm'], comp['complicated'])
    high_risk = max([high_risk1, high_risk2, high_risk3, high_risk4, high_risk5,
                     high_risk6, high_risk7, high_risk8, high_risk9, high_risk10,
                     high_risk11, high_risk12, high_risk13, high_risk14, high_risk15])
    # Low risk rules (7)
    low_risk1 = min(apgar['high'], week['term'], weight['normal'])
    low_risk2 = min(age['normal'], comp['normal'])
    low_risk3 = min(apgar['high'], comp['complicated'])
    low_risk4 = min(week['term'], age['normal'])
    low_risk5 = min(weight['normal'], apgar['medium'], comp['normal'])
    low_risk6 = min(apgar['high'], week['term'], comp['normal'])
    low_risk7 = min(weight['normal'], age['normal'], comp['normal'])
    low_risk = max([low_risk1, low_risk2, low_risk3, low_risk4, low_risk5, low_risk6, low_risk7])
    mod_risk = max(0, 1 - (high_risk + low_risk) / 2)
    return {'low': low_risk, 'moderate': mod_risk, 'high': high_risk}

def generate_visualizations(fuzzy_inputs, risk_levels, actual_values, inherited_probs_list):
    plots = {}
    # Helper function to create nice input fuzzification graphs
    def save_input_fuzzy(x_range, title, xlabel, filename, user_value=None, mf_params=None):
        plt.figure(figsize=(7, 4))
        color_map = {
            'low': 'red', 'medium': 'orange', 'high': 'green',
            'preterm': 'red', 'term': 'green', 'postterm': 'orange',
            'young': 'orange', 'normal': 'green', 'advanced': 'red'
        }
        curves = {}
        labels = []
        if mf_params:
            for label, params in mf_params.items():
                curves[label] = np.array([trapezoidal_mf(val, *params) for val in x_range])
                labels.append(label)
        else:
            return None  # Skip if no params
        
        for label in labels:
            color = color_map.get(label, 'blue')
            plt.plot(x_range, curves[label], label=label.capitalize(), color=color, linewidth=2.2)
        
        if user_value is not None:
            plt.axvline(user_value, color='black', linestyle='--', linewidth=2.5,
                        label=f'Your value: {user_value}')
        
        plt.title(title, fontsize=13, fontweight='bold')
        plt.xlabel(xlabel, fontsize=11)
        plt.ylabel('Membership Degree (0–1)', fontsize=11)
        plt.legend(fontsize=10)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        path = f'static/{filename}'
        plt.savefig(path, dpi=140, bbox_inches='tight')
        plt.close()
        return path
    
    # Define mf params for each variable
    apgar_params = {
        'low': (0, 0, 3, 4),
        'medium': (3, 4, 6, 7),
        'high': (6, 7, 10, 10)
    }
    week_params = {
        'preterm': (0, 28, 34, 37),
        'term': (35, 37, 40, 42),
        'postterm': (40, 42, 44, 50)
    }
    weight_params = {
        'low': (0, 500, 1500, 2500),
        'normal': (2000, 2500, 3500, 4000),
        'high': (3500, 4000, 5000, 6000)
    }
    age_params = {
        'young': (0, 10, 18, 25),
        'normal': (20, 25, 30, 35),
        'advanced': (30, 35, 45, 60)
    }
    
    # 1. APGAR
    x_apgar = np.linspace(0, 10, 500)
    plots['apgar'] = save_input_fuzzy(
        x_apgar, 
        "How your baby's APGAR score was interpreted",
        "APGAR Score (0–10)",
        "apgar_fuzzy.png",
        actual_values['apgar'],
        apgar_params
    )
    
    # 2. Birth Week / Gestational Age
    x_week = np.linspace(20, 45, 500)
    plots['week'] = save_input_fuzzy(
        x_week, 
        "How the pregnancy weeks were interpreted",
        "Weeks of Pregnancy",
        "week_fuzzy.png",
        actual_values['week'],
        week_params
    )
    
    # 3. Birth Weight
    x_weight = np.linspace(500, 5500, 500)
    plots['weight'] = save_input_fuzzy(
        x_weight, 
        "How the birth weight was interpreted",
        "Birth Weight (grams)",
        "weight_fuzzy.png",
        actual_values['weight'],
        weight_params
    )
    
    # 4. Maternal Age
    x_age = np.linspace(15, 55, 500)
    plots['age'] = save_input_fuzzy(
        x_age, 
        "How the mother's age was interpreted",
        "Mother's Age (years)",
        "age_fuzzy.png",
        actual_values['age'],
        age_params
    )
    
    # 5. Inherited / Genetic conditions — Bar chart
    if inherited_probs_list and len(inherited_probs_list) > 0:
        diseases = [p['disease'] for p in inherited_probs_list]
        base = [p['base_prob'] * 100 for p in inherited_probs_list]
        fuzzy = [p['fuzzy_prob'] * 100 for p in inherited_probs_list]
        plt.figure(figsize=(max(7, len(diseases) * 1.4), 5))
        x = np.arange(len(diseases))
        width = 0.35
        plt.bar(x - width/2, base, width, label='Basic Chance', color='lightblue', edgecolor='blue')
        plt.bar(x + width/2, fuzzy, width, label='Fuzzy Chance (with uncertainty)', color='navy', alpha=0.85)
        plt.title("Inherited / Genetic Risks — Per Condition", fontsize=13, fontweight='bold')
        plt.ylabel('Probability (%)', fontsize=11)
        plt.xticks(x, diseases, rotation=35, ha='right', fontsize=10)
        plt.legend(fontsize=10)
        plt.grid(True, axis='y', alpha=0.3)
        plt.tight_layout()
        plots['genetic'] = 'static/genetic_risks.png'
        plt.savefig(plots['genetic'], dpi=140, bbox_inches='tight')
        plt.close()
    else:
        plots['genetic'] = None
    
    # 6. Final combined output — very friendly
    x_risk = np.linspace(0, 100, 1000)
    low_mf = np.maximum(0, np.minimum((20 - x_risk)/20, risk_levels['low']))
    mod_mf = np.maximum(0, np.minimum(np.minimum((x_risk - 20)/30, (80 - x_risk)/30), risk_levels['moderate']))
    high_mf = np.maximum(0, np.minimum((x_risk - 70)/30, risk_levels['high']))
    combined = np.maximum(low_mf, np.maximum(mod_mf, high_mf))
    centroid = simpson(x_risk * combined, x_risk) / simpson(combined, x_risk) if np.sum(combined) > 0 else 0
    plt.figure(figsize=(11, 5.5))
    plt.plot(x_risk, low_mf, 'green', lw=2, label='Low Risk — Baby looks very healthy')
    plt.plot(x_risk, mod_mf, 'orange', lw=2, label='Moderate Risk — Needs some attention')
    plt.plot(x_risk, high_mf, 'red', lw=2, label='High Risk — Needs urgent attention')
    plt.plot(x_risk, combined, 'blue', linestyle='--', linewidth=3, label='Combined result after all rules')
    plt.axvline(centroid, color='black', linestyle='--', linewidth=3.5,
                label=f'YOUR FINAL RISK SCORE = {centroid:.1f}%')
    plt.fill_between(x_risk, 0, combined, color='blue', alpha=0.08)
    plt.title("Final Risk Calculation — Easy to Understand", fontsize=15, fontweight='bold')
    plt.xlabel("Risk Level (%) → 0% very safe • 100% very high risk", fontsize=12)
    plt.ylabel("Strength of belonging (0–1)", fontsize=12)
    plt.legend(loc='upper left', bbox_to_anchor=(1.02, 1), fontsize=10)
    plt.grid(True, alpha=0.3)
    plots['final'] = 'static/final_risk.png'
    plt.savefig(plots['final'], dpi=150, bbox_inches='tight')
    plt.close()
    return centroid, plots

def assess_risk(appearance, pulse, grimace, activity, respiration,
<<<<<<< Updated upstream
                birth_week, birth_weight, maternal_age, delivery_comp, inherited_diseases):
    apgar_score, apgar_breakdown = calculate_apgar(appearance, pulse, grimace, activity, respiration)
=======
                birth_week, birth_weight_g, maternal_age, delivery_comp, inherited_diseases,
                child_gender='unknown'):
    apgar_score, apgar_breakdown, apgar_category, apgar_severity, component_detail = \
        calculate_apgar(appearance, pulse, grimace, activity, respiration)

>>>>>>> Stashed changes
    fuzzy_inputs = {
        'apgar': fuzzify_apgar(apgar_score),
        'birth_week': fuzzify_birth_week(birth_week),
        'birth_weight': fuzzify_birth_weight(birth_weight),
        'maternal_age': fuzzify_maternal_age(maternal_age),
        'delivery_comp': fuzzify_delivery_comp(delivery_comp)
    }
    risk_levels = apply_rules(fuzzy_inputs)
    inherited_probs_list, inherited_explanation = estimate_inherited_prob(inherited_diseases, child_gender)
    inherited_prob = np.mean([p['fuzzy_prob'] for p in inherited_probs_list]) if inherited_probs_list else 0.0
    actual_values = {
        'apgar': apgar_score,
        'week': birth_week,
        'weight': birth_weight,
        'age': maternal_age
    }
    overall_risk_prob, plot_paths = generate_visualizations(
        fuzzy_inputs, risk_levels, actual_values, inherited_probs_list
    )
<<<<<<< Updated upstream
    total_risk = (overall_risk_prob + inherited_prob * 100) / 2
=======

    total_risk = 0.7 * overall_risk_prob + 0.3 * inherited_prob * 100

>>>>>>> Stashed changes
    if total_risk < 30:
        risk_level = "Low"
        recommendation = "The baby appears healthy based on fuzzy logic assessment, which handles uncertainties like 'borderline preterm' or 'slightly low weight'. Routine check-ups recommended."
    elif total_risk < 70:
        risk_level = "Moderate"
        recommendation = "Fuzzy logic indicates some concerns with overlapping factors (e.g., medium APGAR and C-section). Consult a doctor for further tests."
    else:
        risk_level = "High"
        recommendation = "Fuzzy logic highlights high risks due to combined imprecise indicators (e.g., low APGAR with preterm). Immediate medical attention advised."
    delivery_type = "Normal Vaginal Delivery" if delivery_comp == 0 else "Cesarean Section"
<<<<<<< Updated upstream
    conclusion = (
        f"{risk_level} health risk. {apgar_breakdown}. "
        f"Birth at {birth_week} weeks, weight {birth_weight}g, "
        f"maternal age {maternal_age}, delivery: {delivery_type}. "
        f"Overall fuzzy risk from birth factors: {overall_risk_prob:.2f}% "
        f"(accounts for uncertainties). "
        f"Inherited risks: {inherited_prob*100:.2f}% ({inherited_explanation}). "
        f"Total: {total_risk:.2f}%. {recommendation}"
    )
=======
    conclusion = (f"{risk_level} health risk. {apgar_breakdown}. "
                  f"Birth at {birth_week}w, weight {birth_weight_g:.0f}g, "
                  f"mother age {maternal_age}, child gender: {normalize_gender(child_gender)}, delivery: {delivery_type}. "
                  f"Birth-factor risk: {overall_risk_prob:.1f}%. "
                  f"Inherited risk: {inherited_prob*100:.1f}%. "
                  f"Total: {total_risk:.1f}%. {recommendation}")

>>>>>>> Stashed changes
    return {
        'overall_risk_probability': overall_risk_prob,
        'inherited_disease_probability': inherited_prob * 100,
        'total_risk_probability': total_risk,
        'apgar_breakdown': apgar_breakdown,
        'inherited_explanation': inherited_explanation,
        'conclusion': conclusion,
<<<<<<< Updated upstream
        'plot_paths': plot_paths
    }
=======
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

>>>>>>> Stashed changes
