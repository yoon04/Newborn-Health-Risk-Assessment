"""Validate fresh timed observations; never infer missing component values."""
from apgar_safety import APGAR_FIELDS


def parse_observations(form, five_components):
    if form.get('apgar_mode') != 'timed':
        return ([], {'apgar_mode': 'Select the supported timed APGAR form.'}) if form.get('apgar_mode') else ([], {})
    errors, observations = {}, []
    for minute in (1, 5, 10, 15, 20):
        raw = {k: (form.get(f'apgar_{minute}_{k}') or '').strip() for k in APGAR_FIELDS}
        if minute == 5:
            components = five_components
        elif not any(raw.values()):
            continue
        else:
            components = {}
            for field, value in raw.items():
                if value not in ('0', '1', '2'):
                    errors[f'apgar_{minute}_{field}'] = f'Complete all five components for the {minute}-minute observation, or clear that observation.'
                else:
                    components[field] = int(value)
        support = (form.get(f'apgar_{minute}_support') or 'unknown').strip()
        if support not in ('none', 'provided', 'unknown'):
            errors[f'apgar_{minute}_support'] = 'Select no support, support provided, or unknown.'
        if len(components) == 5:
            observations.append({'minute': minute, 'components': dict(components), 'support': support})
    return observations, errors


def validate_observation_records(observations):
    from apgar_safety import check_apgar_safety
    minutes = []
    for observation in observations:
        minute = observation.get('minute')
        if type(minute) is not int or minute not in (1, 5, 10, 15, 20) or minute in minutes:
            raise ValueError('APGAR observations must have unique times of 1, 5, 10, 15, or 20 minutes.')
        minutes.append(minute)
        components = observation.get('components', {})
        if set(components) != set(APGAR_FIELDS):
            raise ValueError('Every recorded observation requires all five components.')
        check_apgar_safety(**components)
        if observation.get('support') not in ('none', 'provided', 'unknown'):
            raise ValueError('Observation support must be recorded as none, provided, or unknown.')
    if 5 not in minutes:
        raise ValueError('A timed birth assessment requires a 5-minute observation.')
