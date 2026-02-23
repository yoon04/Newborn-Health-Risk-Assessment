# app.py
import os
from flask import Flask, render_template, request
from fuzzy_logic import assess_risk

app = Flask(__name__)

# Ensure static folder exists
if not os.path.exists('static'):
    os.makedirs('static')

# Common diseases for dropdown
COMMON_DISEASES = [
    'Diabetes', 'Heart Disease', 'Hemoglobin E', 'Congenital Deaf',
    'Muscular Dystrophy', 'Cystic Fibrosis', 'Sickle Cell Anemia', 'Other'
]

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # APGAR components
        appearance   = int(request.form['appearance'])
        pulse        = int(request.form['pulse'])
        grimace      = int(request.form['grimace'])
        activity     = int(request.form['activity'])
        respiration  = int(request.form['respiration'])

<<<<<<< Updated upstream
        # Other inputs
        birth_week   = float(request.form['birth_week'])
        birth_weight = float(request.form['birth_weight'])
        maternal_age = int(request.form['maternal_age'])
=======
        weight_val  = float(request.form['birth_weight'])
        weight_unit = request.form.get('weight_unit', 'g')
        birth_weight_g = convert_weight_to_grams(weight_val, weight_unit)

        maternal_age  = int(request.form['maternal_age'])
        child_gender  = request.form.get('child_gender', 'unknown')
>>>>>>> Stashed changes
        delivery_comp = int(request.form['delivery_comp'])

        # Inherited diseases – dynamic fields
        inherited_diseases = []
        i = 0
        while f'disease_{i}' in request.form:
            disease = request.form[f'disease_{i}']
            if disease == 'Other':
                disease = request.form.get(f'other_disease_{i}', 'Unknown')
<<<<<<< Updated upstream
            mode = request.form.get(f'mode_{i}', 'complex')
            try:
                carriers = int(request.form.get(f'carriers_{i}', 0))
            except ValueError:
                carriers = 0
=======
            mode = request.form.get(f'mode_{i}', 'unknown')
            xlinked_parent = request.form.get(f'xlinked_parent_{i}', 'mother')
            xlinked_status = request.form.get(f'xlinked_status_{i}', 'carrier')
>>>>>>> Stashed changes
            if disease.strip():
                inherited_diseases.append({
                    'disease': disease,
                    'mode': mode,
<<<<<<< Updated upstream
                    'carriers': carriers
=======
                    'xlinked_parent': xlinked_parent,
                    'xlinked_status': xlinked_status,
>>>>>>> Stashed changes
                })
            i += 1

        results = assess_risk(
            appearance, pulse, grimace, activity, respiration,
<<<<<<< Updated upstream
            birth_week, birth_weight, maternal_age, delivery_comp,
            inherited_diseases
=======
            birth_week, birth_weight_g, maternal_age, delivery_comp,
            inherited_diseases, child_gender
>>>>>>> Stashed changes
        )

        return render_template('results.html', results=results)

    return render_template('form.html', common_diseases=COMMON_DISEASES)

if __name__ == '__main__':
    app.run(debug=True)