import numpy as np
from scipy.integrate import simpson  # For defuzzification (updated name)
import pandas as pd
import ast  # For parsing inherited string to list

# Define membership functions (triangular for simplicity)
def triangular_mf(x, a, b, c):
    """Triangular membership function."""
    if x <= a or x >= c:
        return 0.0
    elif a < x <= b:
        return (x - a) / (b - a)
    else:
        return (c - x) / (c - b)

# Fuzzify inputs
def fuzzify_apgar(apgar):
    low = triangular_mf(apgar, 0, 3, 6)
    medium = triangular_mf(apgar, 4, 6, 8)
    high = triangular_mf(apgar, 7, 10, 10)
    return {'low': low, 'medium': medium, 'high': high}

def fuzzify_birth_week(week):
    preterm = triangular_mf(week, 0, 32, 37)
    term = triangular_mf(week, 35, 39, 42)
    postterm = triangular_mf(week, 40, 42, 45)
    return {'preterm': preterm, 'term': term, 'postterm': postterm}

def fuzzify_birth_weight(weight):  # in grams
    low = triangular_mf(weight, 0, 1500, 2500)
    normal = triangular_mf(weight, 2000, 3000, 4000)
    high = triangular_mf(weight, 3500, 4500, 5000)
    return {'low': low, 'normal': normal, 'high': high}

def fuzzify_maternal_age(age):
    young = triangular_mf(age, 0, 18, 25)
    normal = triangular_mf(age, 20, 30, 35)
    advanced = triangular_mf(age, 30, 40, 50)
    return {'young': young, 'normal': normal, 'advanced': advanced}

def fuzzify_delivery_complications(comp):  # 0=none, 1=minor, 2=major
    none = triangular_mf(comp, 0, 0, 1)
    minor = triangular_mf(comp, 0.5, 1.5, 2.5)
    major = triangular_mf(comp, 2, 3, 3)
    return {'none': none, 'minor': minor, 'major': major}

# For inherited diseases: Assume input as list of diseases with inheritance mode
def estimate_inherited_prob(diseases):
    probs = []
    for d in diseases:
        if d['mode'] == 'recessive':
            if d.get('carriers', 0) == 2:
                base_prob = 0.25  # Mendelian
            else:
                base_prob = 0.0
        elif d['mode'] == 'dominant':
            base_prob = 0.5
        else:
            base_prob = 0.1  # Default for complex
        # Fuzzify with uncertainty
        fuzzy_prob = triangular_mf(base_prob, 0, 0.5, 1)  # Example: medium uncertainty
        probs.append(fuzzy_prob)
    return np.mean(probs) if probs else 0.0  # Average fuzzy prob

# Fuzzy rules for overall risk (expanded with more rules for accuracy)
def apply_rules(fuzzy_inputs):
    apgar = fuzzy_inputs['apgar']
    week = fuzzy_inputs['birth_week']
    weight = fuzzy_inputs['birth_weight']
    age = fuzzy_inputs['maternal_age']
    comp = fuzzy_inputs['delivery_complications']
    
    # High risk rules (min for AND)
    high_risk1 = min(apgar['low'], week['preterm'], weight['low'])  # Low vitality, preterm, low weight
    high_risk2 = min(age['advanced'], comp['major'])  # Advanced age and major complications
    high_risk3 = min(week['postterm'], comp['major'])  # Postterm with complications
    high_risk4 = min(apgar['low'], age['young'])  # Low APGAR with young mother
    high_risk = max(high_risk1, high_risk2, high_risk3, high_risk4)
    
    # Low risk rules
    low_risk1 = min(apgar['high'], week['term'], weight['normal'])  # High vitality, term, normal weight
    low_risk2 = min(age['normal'], comp['none'])  # Normal age, no complications
    low_risk = max(low_risk1, low_risk2)
    
    # Moderate risk as residual
    mod_risk = max(0, 1 - (high_risk + low_risk))  # Simplified fuzzy complement
    
    return {'low': low_risk, 'moderate': mod_risk, 'high': high_risk}

# Defuzzification (centroid method) – using simpson
def defuzzify(risk_levels):
    x = np.linspace(0, 100, 1000)  # Risk percentage scale
    low_mf = np.maximum(0, np.minimum((20 - x)/20, risk_levels['low']))  # Trapezoidal approx for low
    mod_mf = np.maximum(0, np.minimum(np.minimum((x - 20)/30, (80 - x)/30), risk_levels['moderate']))
    high_mf = np.maximum(0, np.minimum((x - 70)/30, risk_levels['high']))
    combined_mf = np.maximum(low_mf, np.maximum(mod_mf, high_mf))
    
    if np.sum(combined_mf) == 0:
        return 0
    centroid = simpson(x * combined_mf, x) / simpson(combined_mf, x)
    return centroid

# Main assessment function
def assess_risk(apgar, birth_week, birth_weight, maternal_age, delivery_comp, inherited_diseases):
    fuzzy_inputs = {
        'apgar': fuzzify_apgar(apgar),
        'birth_week': fuzzify_birth_week(birth_week),
        'birth_weight': fuzzify_birth_weight(birth_weight),
        'maternal_age': fuzzify_maternal_age(maternal_age),
        'delivery_complications': fuzzify_delivery_complications(delivery_comp)
    }
    risk_levels = apply_rules(fuzzy_inputs)
    overall_risk_prob = defuzzify(risk_levels)
    inherited_prob = estimate_inherited_prob(inherited_diseases)
    total_risk = (overall_risk_prob + inherited_prob * 100) / 2  # Combined estimate
    
    # Conclusion for parents/doctors
    if total_risk < 30:
        conclusion = "Low health risk. Baby appears healthy; routine monitoring recommended."
    elif total_risk < 70:
        conclusion = "Moderate health risk. Consult doctor for further tests."
    else:
        conclusion = "High health risk. Immediate medical attention advised."
    
    return {
        'overall_risk_probability': overall_risk_prob,
        'inherited_disease_probability': inherited_prob * 100,
        'total_risk_probability': total_risk,
        'conclusion': conclusion
    }

# Example single assessment + dataset processing
if __name__ == "__main__":
    # Sample single inputs
    apgar = 8
    birth_week = 38
    birth_weight = 3200
    maternal_age = 28
    delivery_comp = 0
    inherited_diseases = [{'disease': 'cystic fibrosis', 'mode': 'recessive', 'carriers': 1}]
    
    results = assess_risk(apgar, birth_week, birth_weight, maternal_age, delivery_comp, inherited_diseases)
    print("Single Sample Health Risk Assessment Results:")
    print(f"Overall Risk Probability: {results['overall_risk_probability']:.2f}%")
    print(f"Inherited Disease Probability: {results['inherited_disease_probability']:.2f}%")
    print(f"Total Risk Probability: {results['total_risk_probability']:.2f}%")
    print("Conclusion:", results['conclusion'])
    
    # Process dataset from CSV
    try:
        data = pd.read_csv('synthetic_newborn_data.csv')  # Or replace with your dataset path
        print("\nDataset Health Risk Assessment Results:")
        for idx, row in data.iterrows():
            # Parse inherited string safely
            try:
                inherited = ast.literal_eval(row['inherited'])
            except:
                inherited = []
            res = assess_risk(row['apgar'], row['birth_week'], row['birth_weight'], row['maternal_age'], row['delivery_comp'], inherited)
            print(f"Sample {idx+1}: Total Risk {res['total_risk_probability']:.2f}%, Conclusion: {res['conclusion']}")
    except FileNotFoundError:
        print("CSV file not found. Please provide 'synthetic_newborn_data.csv' or update the path.")