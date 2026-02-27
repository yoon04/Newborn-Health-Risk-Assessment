import os
from flask import Flask, render_template, request
from fuzzy_logic import assess_risk, convert_weight_to_grams, INHERITANCE_MODES

app = Flask(__name__)

if not os.path.exists('static'):
    os.makedirs('static')

COMMON_DISEASES = [
    'Diabetes', 'Heart Disease', 'Hemoglobin E', 'Congenital Deafness',
    'Muscular Dystrophy', 'Color Blindness', 'Other'
]

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        appearance  = int(request.form['appearance'])
        pulse       = int(request.form['pulse'])
        grimace     = int(request.form['grimace'])
        activity    = int(request.form['activity'])
        respiration = int(request.form['respiration'])
        birth_week  = float(request.form['birth_week'])

        weight_val  = float(request.form['birth_weight'])
        weight_unit = request.form.get('weight_unit', 'g')
        birth_weight_g = convert_weight_to_grams(weight_val, weight_unit)

        maternal_age  = int(request.form['maternal_age'])
        child_gender  = request.form.get('child_gender', 'unknown')
        delivery_comp = int(request.form['delivery_comp'])

        inherited_diseases = []
        i = 0
        while f'disease_{i}' in request.form:
            disease = request.form[f'disease_{i}']
            if disease == 'Other':
                disease = request.form.get(f'other_disease_{i}', 'Unknown')
            mode = request.form.get(f'mode_{i}', 'unknown')
            xlinked_parent = request.form.get(f'xlinked_parent_{i}', 'mother')
            xlinked_status = request.form.get(f'xlinked_status_{i}', 'carrier')
            if disease.strip():
                inherited_diseases.append({
                    'disease': disease,
                    'mode': mode,
                    'xlinked_parent': xlinked_parent,
                    'xlinked_status': xlinked_status,
                })
            i += 1

        results = assess_risk(
            appearance, pulse, grimace, activity, respiration,
            birth_week, birth_weight_g, maternal_age, delivery_comp,
            inherited_diseases, child_gender
        )
        results['weight_display'] = f"{weight_val} {weight_unit} ({birth_weight_g:.0f}g)"
        return render_template('results.html', results=results)

    return render_template('form.html',
                           common_diseases=COMMON_DISEASES,
                           inheritance_modes=INHERITANCE_MODES)

if __name__ == '__main__':
    app.run(debug=True)
