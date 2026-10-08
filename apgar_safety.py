"""Conservative component-level safety policy; not a resuscitation algorithm."""
APGAR_FIELDS = ('appearance', 'pulse', 'grimace', 'activity', 'respiration')
URGENT_ACTION = ('Seek immediate assessment by the neonatal care team or emergency medical services. '
                 'Do not wait to finish this form or for an APGAR total. '
                 'Treatment requires direct clinical assessment.')


def check_apgar_safety(appearance, pulse, grimace, activity, respiration):
    values = dict(zip(APGAR_FIELDS, (appearance, pulse, grimace, activity, respiration)))
    for field, value in values.items():
        if isinstance(value, bool) or not isinstance(value, int) or value not in (0, 1, 2):
            raise ValueError(f'{field} must be an integer APGAR component score of 0, 1, or 2.')
    alerts = []
    for field, score, reason in (
        ('pulse', 0, 'No heartbeat detected'),
        ('pulse', 1, 'Heart rate below 100 bpm'),
        ('respiration', 0, 'No breathing detected'),
        ('respiration', 1, 'Weak or irregular breathing'),
    ):
        if values[field] == score:
            alerts.append({'id': f'SAFETY-{field.upper()}-{score}', 'component': field,
                           'score': score, 'reason': reason})
    notices = []
    if appearance == 0:
        notices.append({
            'id': 'NOTICE-APPEARANCE-0', 'component': 'appearance', 'score': 0,
            'reason': 'Blue or pale all over: direct clinical assessment needed',
            'action': 'Seek immediate in-person assessment by the neonatal care team or emergency medical services if this describes the baby now. Do not wait for an APGAR total. Skin colour alone cannot establish oxygenation or determine treatment.',
        })
    for field, score, reason, urgency in (
        ('grimace', 0, 'No reflex response to stimulation', 'urgent'),
        ('grimace', 1, 'Limited reflex response (grimace only)', 'review'),
        ('activity', 0, 'Limp or absent muscle tone', 'urgent'),
        ('activity', 1, 'Reduced muscle tone (some flexion)', 'review'),
    ):
        if values[field] == score:
            action = ('Seek immediate in-person clinical assessment if this describes the baby now. Do not wait for an APGAR total.'
                      if urgency == 'urgent' else 'Have the neonatal clinician reassess this component and document the finding.')
            notices.append({'id': f'NOTICE-{field.upper()}-{score}', 'component': field,
                            'score': score, 'reason': reason, 'urgency': urgency,
                            'action': action + ' Prematurity and maternal medication can affect tone and reflex responses; this notice does not diagnose a condition or prescribe treatment.'})
    for notice in notices:
        notice.setdefault('urgency', 'urgent')
    return {'active': bool(alerts), 'alerts': alerts, 'notices': notices,
            'action': URGENT_ACTION if alerts else '', 'policy_version': '1.2'}
