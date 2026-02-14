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

        # Other inputs
        birth_week   = float(request.form['birth_week'])
        birth_weight = float(request.form['birth_weight'])
        maternal_age = int(request.form['maternal_age'])
        delivery_comp = int(request.form['delivery_comp'])

        # Inherited diseases – dynamic fields
        inherited_diseases = []
        i = 0
        while f'disease_{i}' in request.form:
            disease = request.form[f'disease_{i}']
            if disease == 'Other':
                disease = request.form.get(f'other_disease_{i}', 'Unknown')
            mode = request.form.get(f'mode_{i}', 'complex')
            try:
                carriers = int(request.form.get(f'carriers_{i}', 0))
            except ValueError:
                carriers = 0
            if disease.strip():
                inherited_diseases.append({
                    'disease': disease,
                    'mode': mode,
                    'carriers': carriers
                })
            i += 1

        results = assess_risk(
            appearance, pulse, grimace, activity, respiration,
            birth_week, birth_weight, maternal_age, delivery_comp,
            inherited_diseases
        )

        return render_template('results.html', results=results)

    return render_template('form.html', common_diseases=COMMON_DISEASES)

if __name__ == '__main__':
    app.run(debug=True)