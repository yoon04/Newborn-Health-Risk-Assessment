import numpy as np
from scipy.integrate import simpson  # For defuzzification
import ast  # For parsing inherited string to list (not used now, but kept for potential future)

# Define membership functions
def triangular_mf(x, a, b, c):
    """Triangular membership function."""
    if x <= a or x >= c:
        return 0.0
    elif a < x <= b:
        return (x - a) / (b - a)
    else:
        return (c - x) / (c - b)

def trapezoidal_mf(x, a, b, c, d):
    """Trapezoidal membership function."""
    if x < a or x > d:
        return 0.0
    elif a <= x < b:
        return (x - a) / (b - a) if b > a else 1.0
    elif b <= x <= c:
        return 1.0
    elif c < x <= d:
        return (d - x) / (d - c) if d > c else 1.0
    return 0.0  # Fallback

# Calculate APGAR score from individual components and categorize
def calculate_apgar(appearance, pulse, grimace, activity, respiration):
    """Calculate total APGAR score (0-10) from components (each 0-2)."""
    apgar = appearance + pulse + grimace + activity + respiration
    apgar = min(max(apgar, 0), 10)  # Clamp to 0-10
    
    if apgar >= 7:
        category = "Normal (7-10) - Baby is in good health."
    elif apgar >= 4:
        category = "Moderately abnormal (4-6) - May need some intervention like oxygen."
    else:
        category = "Low (0-3) - Requires immediate medical attention."
    
    breakdown = f"APGAR Score: {apgar}/10 ({category}) (Appearance: {appearance}/2 - skin color; Pulse: {pulse}/2 - heart rate; Grimace: {grimace}/2 - reflex; Activity: {activity}/2 - muscle tone; Respiration: {respiration}/2 - breathing)"
    return apgar, breakdown

# Fuzzify inputs
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

def fuzzify_birth_weight(weight):  # in grams
    low = trapezoidal_mf(weight, 0, 500, 1500, 2500)
    normal = trapezoidal_mf(weight, 2000, 2500, 3500, 4000)
    high = trapezoidal_mf(weight, 3500, 4000, 5000, 6000)
    return {'low': low, 'normal': normal, 'high': high}

def fuzzify_maternal_age(age):
    young = trapezoidal_mf(age, 0, 10, 18, 25)
    normal = trapezoidal_mf(age, 20, 25, 30, 35)
    advanced = trapezoidal_mf(age, 30, 35, 45, 60)
    return {'young': young, 'normal': normal, 'advanced': advanced}

def fuzzify_delivery_comp(delivery_comp):  # 0=Normal Vaginal, 1=Cesarean Section
    normal = triangular_mf(delivery_comp, 0, 0, 0.5)  # High membership at 0
    complicated = triangular_mf(delivery_comp, 0.5, 1, 1)  # High membership at 1
    return {'normal': normal, 'complicated': complicated}

# For inherited diseases (updated with common ones)
def estimate_inherited_prob(diseases):
    probs = []
    explanations = []
    for d in diseases:
        disease_name = d['disease'].lower()
        mode = d['mode']
        if disease_name == 'heart disease' or disease_name == 'diabetes':
            base_prob = 0.1  # Complex, multifactorial
            expl = f"{d['disease']}: ~10% chance (complex inheritance, lifestyle/environment factors)."
        elif disease_name == 'hemoglobin e':
            base_prob = 0.25 if d.get('carriers', 0) == 2 else 0.0
            expl = f"{d['disease']}: {base_prob*100}% chance (recessive, depends on carriers)."
        elif disease_name == 'congenital deaf':
            base_prob = 0.5  # Assuming dominant form
            expl = f"{d['disease']}: 50% chance (dominant inheritance)."
        elif disease_name == 'muscular dystrophy':
            base_prob = 0.25 if d.get('carriers', 0) == 2 else 0.0
            expl = f"{d['disease']}: {base_prob*100}% chance (recessive/X-linked)."
        else:
            base_prob = 0.1
            expl = f"{d['disease']}: ~10% chance (default complex)."
        # Fuzzify with uncertainty
        fuzzy_prob = triangular_mf(base_prob, 0, 0.5, 1)
        probs.append(fuzzy_prob)
        explanations.append(expl)
    avg_prob = np.mean(probs) if probs else 0.0
    explanation = "; ".join(explanations) if explanations else "No inherited diseases noted."
    return avg_prob, explanation

# Expanded Fuzzy rules for overall risk (more rules added for accuracy)
def apply_rules(fuzzy_inputs):
    apgar = fuzzy_inputs['apgar']
    week = fuzzy_inputs['birth_week']
    weight = fuzzy_inputs['birth_weight']
    age = fuzzy_inputs['maternal_age']
    comp = fuzzy_inputs['delivery_comp']
    
    # Expanded High risk rules (min for AND, max for OR)
    high_risk1 = min(apgar['low'], week['preterm'], weight['low'])  # Low APGAR, preterm, low weight
    high_risk2 = min(age['advanced'], comp['complicated'])  # Advanced age and C-section
    high_risk3 = min(week['postterm'], comp['complicated'])  # Postterm with C-section
    high_risk4 = min(apgar['low'], age['young'])  # Low APGAR with young mother
    high_risk5 = min(weight['high'], week['preterm'])  # High weight but preterm
    high_risk6 = min(apgar['medium'], comp['complicated'])  # Medium APGAR with C-section
    high_risk7 = min(week['preterm'], age['advanced'])  # Preterm with advanced age
    high_risk8 = min(weight['low'], apgar['medium'])  # Low weight with medium APGAR
    high_risk9 = min(week['postterm'], weight['high'])  # Postterm with high weight
    high_risk10 = min(comp['complicated'], age['young'], apgar['low'])  # C-section with young age and low APGAR
    high_risk11 = min(week['preterm'], comp['complicated'])  # Preterm with C-section
    high_risk12 = min(weight['low'], comp['complicated'])  # Low weight with C-section
    high_risk13 = min(apgar['low'], week['postterm'])  # Low APGAR with postterm
    high_risk14 = min(age['advanced'], weight['high'])  # Advanced age with high weight (macrosomia risk)
    high_risk15 = min(apgar['medium'], week['preterm'], comp['complicated'])  # Medium APGAR, preterm, C-section
    high_risk = max(high_risk1, high_risk2, high_risk3, high_risk4, high_risk5, high_risk6, high_risk7, high_risk8, high_risk9, high_risk10,
                    high_risk11, high_risk12, high_risk13, high_risk14, high_risk15)
    
    # Expanded Low risk rules
    low_risk1 = min(apgar['high'], week['term'], weight['normal'])  # High APGAR, term, normal weight
    low_risk2 = min(age['normal'], comp['normal'])  # Normal age, vaginal delivery
    low_risk3 = min(apgar['high'], comp['complicated'])  # High APGAR even with C-section
    low_risk4 = min(week['term'], age['normal'])  # Term birth with normal age
    low_risk5 = min(weight['normal'], apgar['medium'], comp['normal'])  # Normal weight, medium APGAR, vaginal
    low_risk6 = min(apgar['high'], week['term'], comp['normal'])  # High APGAR, term, vaginal
    low_risk7 = min(weight['normal'], age['normal'], comp['normal'])  # Normal weight, age, vaginal
    low_risk = max(low_risk1, low_risk2, low_risk3, low_risk4, low_risk5, low_risk6, low_risk7)
    
    # Moderate risk as residual (fuzzy complement)
    mod_risk = max(0, 1 - (high_risk + low_risk) / 2)
    
    return {'low': low_risk, 'moderate': mod_risk, 'high': high_risk}

# Defuzzification (centroid method)
def defuzzify(risk_levels):
    x = np.linspace(0, 100, 1000)  # Risk percentage scale
    low_mf = np.maximum(0, np.minimum((20 - x)/20, risk_levels['low']))
    mod_mf = np.maximum(0, np.minimum(np.minimum((x - 20)/30, (80 - x)/30), risk_levels['moderate']))
    high_mf = np.maximum(0, np.minimum((x - 70)/30, risk_levels['high']))
    combined_mf = np.maximum(low_mf, np.maximum(mod_mf, high_mf))
    
    if np.sum(combined_mf) == 0:
        return 0
    centroid = simpson(x * combined_mf, x) / simpson(combined_mf, x)
    return centroid

# Main assessment function
def assess_risk(appearance, pulse, grimace, activity, respiration, birth_week, birth_weight, maternal_age, delivery_comp, inherited_diseases):
    apgar_score, apgar_breakdown = calculate_apgar(appearance, pulse, grimace, activity, respiration)
    
    fuzzy_inputs = {
        'apgar': fuzzify_apgar(apgar_score),
        'birth_week': fuzzify_birth_week(birth_week),
        'birth_weight': fuzzify_birth_weight(birth_weight),
        'maternal_age': fuzzify_maternal_age(maternal_age),
        'delivery_comp': fuzzify_delivery_comp(delivery_comp)
    }
    risk_levels = apply_rules(fuzzy_inputs)
    overall_risk_prob = defuzzify(risk_levels)
    inherited_prob, inherited_explanation = estimate_inherited_prob(inherited_diseases)
    total_risk = (overall_risk_prob + inherited_prob * 100) / 2  # Combined estimate
    
    # Parent/Doctor-friendly conclusion
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
    conclusion = f"{risk_level} health risk. {apgar_breakdown}. Birth at {birth_week} weeks, weight {birth_weight}g, maternal age {maternal_age}, delivery: {delivery_type}. Overall fuzzy risk from birth factors: {overall_risk_prob:.2f}% (accounts for uncertainties). Inherited risks: {inherited_prob * 100:.2f}% ({inherited_explanation}). Total: {total_risk:.2f}%. {recommendation}"
    
    return {
        'overall_risk_probability': overall_risk_prob,
        'inherited_disease_probability': inherited_prob * 100,
        'total_risk_probability': total_risk,
        'apgar_breakdown': apgar_breakdown,
        'inherited_explanation': inherited_explanation,
        'conclusion': conclusion
    }

# Interactive user input app
if __name__ == "__main__":
    print("Welcome to the Newborn Health Risk Assessment App (Fuzzy Logic-Based)")
    print("Please enter the following details:")
    
    # APGAR components with user-friendly explanations
    appearance = int(input("Appearance (skin color): Enter 0 for blue/pale all over (bad), 1 for pink body but blue hands/feet (moderate), 2 for completely pink (good): "))
    pulse = int(input("Pulse (heart rate): Enter 0 for absent (critical), 1 for below 100 bpm (slow), 2 for above 100 bpm (normal): "))
    grimace = int(input("Grimace (reflex response): Enter 0 for no response (bad), 1 for grimace only (minimal), 2 for grimace and pull away/cough/sneeze (strong): "))
    activity = int(input("Activity (muscle tone): Enter 0 for limp (bad), 1 for some flex of arms/legs (moderate), 2 for active movement (good): "))
    respiration = int(input("Respiration (breathing): Enter 0 for absent (critical), 1 for weak cry/slow irregular (weak), 2 for good strong cry (good): "))
    
    birth_week = float(input("Birth week (e.g., 38 for full term): "))
    birth_weight = float(input("Birth weight in grams (e.g., 3200): "))
    maternal_age = int(input("Maternal age in years (e.g., 28): "))
    delivery_comp = int(input("Delivery complication: Enter 0 for Normal Vaginal Delivery, 1 for Cesarean Section: "))
    
    # Inherited diseases interactively
    inherited_diseases = []
    num_diseases = int(input("Number of inherited diseases (enter 0 if none): "))
    for i in range(num_diseases):
        print(f"\nInherited Disease {i+1}:")
        disease = input("Disease name (e.g., Diabetes): ")
        mode = input("Inheritance mode (e.g., complex, recessive, dominant): ")
        carriers = int(input("Number of carriers (0-2, e.g., 2 for both parents carriers in recessive diseases): "))
        inherited_diseases.append({'disease': disease, 'mode': mode, 'carriers': carriers})
    
    # Run assessment
    results = assess_risk(appearance, pulse, grimace, activity, respiration, birth_week, birth_weight, maternal_age, delivery_comp, inherited_diseases)
    
    print("\nHealth Risk Assessment Results:")
    print(f"Overall Risk Probability: {results['overall_risk_probability']:.2f}%")
    print(f"Inherited Disease Probability: {results['inherited_disease_probability']:.2f}%")
    print(f"Total Risk Probability: {results['total_risk_probability']:.2f}%")
    print("Conclusion:", results['conclusion'])