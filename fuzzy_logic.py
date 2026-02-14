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

def fuzzify_delivery_comp(delivery_comp):
    normal = triangular_mf(delivery_comp, 0, 0, 0.5)
    complicated = triangular_mf(delivery_comp, 0.5, 1, 1)
    return {'normal': normal, 'complicated': complicated}

def estimate_inherited_prob(diseases):
    probs_list = []
    explanations = []
    for d in diseases:
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
        probs_list.append({
            'disease': d['disease'],
            'base_prob': base_prob,
            'fuzzy_prob': fuzzy_prob,
            'expl': expl
        })
        explanations.append(expl)
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
                birth_week, birth_weight, maternal_age, delivery_comp, inherited_diseases):
    apgar_score, apgar_breakdown = calculate_apgar(appearance, pulse, grimace, activity, respiration)
    fuzzy_inputs = {
        'apgar': fuzzify_apgar(apgar_score),
        'birth_week': fuzzify_birth_week(birth_week),
        'birth_weight': fuzzify_birth_weight(birth_weight),
        'maternal_age': fuzzify_maternal_age(maternal_age),
        'delivery_comp': fuzzify_delivery_comp(delivery_comp)
    }
    risk_levels = apply_rules(fuzzy_inputs)
    inherited_probs_list, inherited_explanation = estimate_inherited_prob(inherited_diseases)
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
    total_risk = (overall_risk_prob + inherited_prob * 100) / 2
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
    conclusion = (
        f"{risk_level} health risk. {apgar_breakdown}. "
        f"Birth at {birth_week} weeks, weight {birth_weight}g, "
        f"maternal age {maternal_age}, delivery: {delivery_type}. "
        f"Overall fuzzy risk from birth factors: {overall_risk_prob:.2f}% "
        f"(accounts for uncertainties). "
        f"Inherited risks: {inherited_prob*100:.2f}% ({inherited_explanation}). "
        f"Total: {total_risk:.2f}%. {recommendation}"
    )
    return {
        'overall_risk_probability': overall_risk_prob,
        'inherited_disease_probability': inherited_prob * 100,
        'total_risk_probability': total_risk,
        'apgar_breakdown': apgar_breakdown,
        'inherited_explanation': inherited_explanation,
        'conclusion': conclusion,
        'plot_paths': plot_paths
    }