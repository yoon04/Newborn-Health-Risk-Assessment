"""Persistence helpers that keep database writes separate from fuzzy logic."""

import re

from extensions import db
from models import Assessment, User


ALGORITHM_VERSION = 'fuzzy-v2'
RAW_INPUT_FIELDS = (
    'appearance', 'pulse', 'grimace', 'activity', 'respiration',
    'birth_week', 'birth_weight', 'weight_unit', 'maternal_age',
    'child_gender', 'delivery_type', 'delivery_comp',
    'family_history_status', 'family_disease', 'affected_relative',
    'user_name', 'user_email',
)
EMAIL_PATTERN = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')


def _json_safe(value):
    """Convert NumPy scalars and nested values into JSON-serializable data."""
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    if hasattr(value, 'item'):
        try:
            return _json_safe(value.item())
        except (ValueError, TypeError):
            pass
    return value


def _raw_input_snapshot(raw_form):
    return {
        field: str(raw_form.get(field, '') or '')
        for field in RAW_INPUT_FIELDS
    }


def _get_or_create_user(name, email):
    name = (name or '').strip() or None
    email = (email or '').strip().lower() or None
    if not name and not email:
        return None

    user = User.query.filter_by(email=email).first() if email else None
    if user is None:
        user = User(name=name, email=email)
        db.session.add(user)
    elif name and not user.name:
        user.name = name
    return user


def _result_snapshot(results):
    excluded = {'plot_paths', 'pdf_report_token'}
    return _json_safe({key: value for key, value in results.items() if key not in excluded})


def build_assessment_record(values, results, raw_form):
    """Build a database record without committing it."""
    family_history = values['family_history']
    user = _get_or_create_user(values.get('user_name'), values.get('user_email'))

    record = Assessment(
        user=user,
        appearance=values['appearance'],
        pulse=values['pulse'],
        grimace=values['grimace'],
        activity=values['activity'],
        respiration=values['respiration'],
        apgar_total=results['apgar_score'],
        birth_week=values['birth_week'],
        birth_weight_input=values['weight_value'],
        birth_weight_unit=values['weight_unit'],
        birth_weight_g=values['birth_weight_g'],
        maternal_age=values['maternal_age'],
        child_gender=values['child_gender'],
        delivery_type=values['delivery_type'],
        delivery_complication=bool(values['delivery_comp']),
        family_history_status=family_history['status'],
        family_disease_name=family_history.get('disease') or None,
        family_affected_relative=family_history.get('affected_relative') or None,
        raw_inputs=_raw_input_snapshot(raw_form),
        immediate_risk_index=results['immediate_condition_risk_index'],
        immediate_risk_level=results['immediate_condition_risk_level'],
        birth_related_risk_index=results['birth_related_risk_index'],
        birth_related_risk_level=results['birth_related_risk_level'],
        family_history_risk_index=results['family_history_risk_index'],
        family_history_risk_level=results['family_history_risk_level'],
        overall_risk_index=results['overall_risk_index'],
        risk_level=results['risk_level'],
        confidence_level=results['confidence_level'],
        confidence_reasons=_json_safe(results['confidence_reasons']),
        main_contributing_factors=_json_safe(results['main_contributing_factors']),
        lower_impact_factors=_json_safe(results['lower_impact_factors']),
        triggered_rules=_json_safe(results['triggered_rules']),
        user_guidance=_json_safe(results['user_guidance']),
        apgar_breakdown=results['apgar_breakdown'],
        apgar_category=results['apgar_category'],
        apgar_severity=results['apgar_severity'],
        apgar_component_detail=_json_safe(results['component_detail']),
        family_history_summary=results['family_history_summary'],
        recommendation=results['recommendation'],
        result_snapshot=_result_snapshot(results),
        algorithm_version=ALGORITHM_VERSION,
    )
    return record


def save_assessment(values, results, raw_form):
    """Add and commit one assessment; callers roll back on database errors."""
    record = build_assessment_record(values, results, raw_form)
    db.session.add(record)
    db.session.commit()
    return record
