"""Frozen NICU research inference. Does not participate in triage or fuzzy rules."""
from functools import lru_cache
import hashlib
import importlib.metadata
import json
import logging
import math
from pathlib import Path

ARTIFACT_DIR = Path(__file__).resolve().parent / 'research_models' / 'nicu_v2'
FEATURES = ['gestational_age_weeks', 'birth_weight_g', 'maternal_age']
MODEL_VERSION = 'NICU-V2 / CDC 2024'
SCOPE = 'Singleton births; gestation encoded as 20–45 completed weeks, weight 227–5999 g, maternal age 13–49 years.'
LIMITATIONS = [
    'Retrospective prediction of admission recorded on U.S. birth certificates; prediction timing is unverified.',
    '2023 historical evaluation is not local hospital or future-year validation.',
    'At research threshold 0.10, sensitivity was 53.8% overall and 10.2% for term births. A low estimate cannot establish safety.',
    'No clinical action threshold is approved. This estimate does not determine admission, treatment, discharge, or module actions.'
]

@lru_cache(maxsize=1)
def _load_artifacts():
    # Only the bundled, user-exported model is accepted; no web upload/loading route.
    manifest = json.loads((ARTIFACT_DIR / 'manifest.json').read_text())
    for name in ['model.joblib', 'model_card.json', 'evaluation_report.json']:
        if hashlib.sha256((ARTIFACT_DIR / name).read_bytes()).hexdigest() != manifest[name]:
            raise ValueError('Model artifact checksum mismatch')
    card = json.loads((ARTIFACT_DIR / 'model_card.json').read_text())
    evaluation = json.loads((ARTIFACT_DIR / 'evaluation_report.json').read_text())
    if card['features'] != FEATURES or card['status'] != 'research_only':
        raise ValueError('Unexpected model schema or intended use')
    for name, version in card['versions'].items():
        if importlib.metadata.version(name) != version:
            raise ValueError('Inference dependency version differs from frozen export')
    import joblib
    model = joblib.load(ARTIFACT_DIR / 'model.joblib')
    if list(model.feature_names_in_) != FEATURES or list(model.classes_) != [0, 1]:
        raise ValueError('Unexpected model feature order or classes')
    return model, evaluation

def estimate_nicu_research(values):
    result = {'status': 'unavailable', 'reason': '', 'model_version': MODEL_VERSION,
              'scope': SCOPE, 'limitations': list(LIMITATIONS),
              'plurality': values.get('birth_plurality', 'unknown'),
              'target': 'Recorded NICU admission', 'probability': None}
    if result['plurality'] != 'singleton':
        result['reason'] = ('The model covers singleton births only.' if result['plurality'] in {'multiple', 'twin'}
                            else 'Confirm singleton birth before an ML estimate can be shown.')
        return result
    try:
        inputs = [float(values[k]) for k in ['birth_week', 'birth_weight_g', 'maternal_age']]
    except (KeyError, TypeError, ValueError):
        result['reason'] = 'Required model inputs are missing or invalid.'
        return result
    if not all(math.isfinite(v) for v in inputs):
        result['reason'] = 'Required model inputs must be finite numbers.'
        return result
    week, weight, age = inputs
    if not (20 <= week <= 45 and 227 <= weight <= 5999 and 13 <= age <= 49):
        result['reason'] = 'Recorded inputs fall outside the model population. The three module assessments remain separate.'
        return result
    if not age.is_integer():
        result['reason'] = 'Enter maternal age in completed whole years; fractional ages are not accepted by this model.'
        return result
    # CDC obstetric gestation is recorded in completed weeks. Preserve the
    # clinical observation and map only the ML feature (38.5 -> 38, never 39).
    completed_week = math.floor(week)
    result['input_encoding'] = {
        'recorded_gestational_weeks': week,
        'completed_gestational_weeks': completed_week,
        'method': 'floor_to_completed_week',
        'source_url': 'https://www.cdc.gov/nchs/nvss/facility-worksheets-guide/30.htm',
    }
    result['inference_policy_version'] = 'nicu-v2-completed-weeks'
    inputs[0] = completed_week
    result['inputs'] = dict(zip(FEATURES, inputs))
    try:
        model, evaluation = _load_artifacts()
        import pandas as pd
        from threadpoolctl import threadpool_limits
        with threadpool_limits(limits=1):
            probability = float(model.predict_proba(pd.DataFrame([inputs], columns=FEATURES))[0, 1])
        if not math.isfinite(probability) or not 0 <= probability <= 1:
            raise ValueError('Invalid model probability')
        result.update(status='available', probability=probability,
                      probability_percent=round(probability * 100, 1),
                      evaluation={k: evaluation['metrics'][k] for k in ['n', 'auroc', 'auprc', 'brier', 'sensitivity']},
                      reason='Research estimate only; observed findings and module rules guide the separate action summaries.')
    except Exception:
        logging.getLogger(__name__).exception('NICU research inference unavailable')
        result['reason'] = 'The research model is unavailable. Check the bundled artifacts and matching inference dependencies.'
    return result
