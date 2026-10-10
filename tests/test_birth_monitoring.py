import itertools
import unittest
from unittest.mock import patch

from flask import render_template
from pypdf import PdfReader

import app as application
from fuzzy_logic import (assess_risk, apply_birth_related_rules, defuzzify_risk,
                         fuzzify_birth_week, fuzzify_birth_weight,
                         fuzzify_maternal_age, fuzzify_delivery_comp)
from persistence import build_assessment_record
from pdf_report import build_pdf_report
from test_validation import valid_form


def inputs(week=39, weight=3200, age=28, complication=0):
    return {'birth_week': fuzzify_birth_week(week), 'birth_weight': fuzzify_birth_weight(weight),
            'maternal_age': fuzzify_maternal_age(age), 'delivery_comp': fuzzify_delivery_comp(complication)}


def index(**values):
    return defuzzify_risk(apply_birth_related_rules(inputs(**values)))


def plots(*args, **kwargs):
    return None, {k: '' for k in ('apgar', 'week', 'weight', 'age', 'genetic', 'immediate', 'birth', 'family', 'final')}


class BirthMonitoringRulesTests(unittest.TestCase):
    def test_age_alone_cannot_activate_high_even_with_complication(self):
        for age, comp in itertools.product(range(12, 61), (0, 1)):
            levels, rules = apply_birth_related_rules(inputs(age=age, complication=comp), return_rules=True)
            self.assertEqual(levels['high'], 0, (age, comp))
            for rule in rules:
                if rule['id'] in ('BR-05', 'BR-13', 'BR-14'):
                    self.assertLessEqual(rule['activation'], .25)
        self.assertLess(index(age=48), 30)

    def test_reported_complication_cannot_activate_reassuring_rule(self):
        levels = apply_birth_related_rules(inputs(complication=1))
        self.assertEqual(levels['low'], 0)
        self.assertEqual(levels['moderate'], 1)

    def test_rule_coverage_including_valid_extremes(self):
        for week, weight, age, comp in itertools.product((20, 32, 37, 39, 42, 45),
                (100, 1500, 2500, 4000, 5999), (12, 20, 35, 60), (0, 1)):
            levels = apply_birth_related_rules(inputs(week, weight, age, comp))
            self.assertGreater(max(levels.values()), 0, (week, weight, age, comp))

    def test_continuous_indices_at_membership_knots(self):
        knots = {'week': (28, 32, 35, 37, 37.5, 40, 42, 42.5),
                 'weight': (800, 1000, 1200, 1300, 1600, 1700, 2200, 2500, 2800, 3600, 3800, 4000, 4300, 4500, 4600, 5000, 5200),
                 'age': (15, 18, 20, 35, 40, 45, 50)}
        for key, boundaries in knots.items():
            for boundary in boundaries:
                self.assertLess(abs(index(**{key: boundary-.001}) - index(**{key: boundary+.001})), .05, (key, boundary))

    def test_improving_low_weight_does_not_raise_index(self):
        scores = [index(weight=w) for w in range(100, 3201, 25)]
        self.assertTrue(all(b <= a + 1e-6 for a, b in zip(scores, scores[1:])))

    def test_improving_preterm_gestation_does_not_raise_index(self):
        scores = [index(week=20+n/10) for n in range(191)]
        self.assertTrue(all(b <= a + 1e-6 for a, b in zip(scores, scores[1:])))

    def test_combined_preterm_low_weight_exceeds_each_alone(self):
        combined = index(week=34, weight=2000)
        self.assertGreater(combined, index(week=34))
        self.assertGreater(combined, index(weight=2000))


class BirthMonitoringExplanationTests(unittest.TestCase):
    def result(self, week=39, weight=3200, age=28, complication=0):
        with patch('fuzzy_logic.generate_visualizations', side_effect=plots):
            return assess_risk(2, 2, 2, 2, 2, week, weight, age, 'vaginal', complication, {'status': 'no'}, 'male')

    def test_exact_clinical_categories_are_distinct_from_fuzzy_overlap(self):
        for week, label in [(27.5, 'Extremely preterm'), (28, 'Very preterm'), (32, 'Preterm'),
                            (37, 'Early term'), (39, 'Full term'), (41, 'Late term'), (42, 'Post-term')]:
            self.assertEqual(self.result(week=week)['birth_monitoring']['inputs'][0]['category'], label)
        for weight, label in [(999, 'Extremely low birth weight'), (1000, 'Very low birth weight'),
                              (1499, 'Very low birth weight'), (1500, 'Low birth weight'),
                              (2499, 'Low birth weight'), (2500, 'Not low birth weight')]:
            self.assertEqual(self.result(weight=weight)['birth_monitoring']['inputs'][1]['category'], label)
        result = self.result(week=37, weight=2500)
        self.assertGreater(result['birth_monitoring']['inputs'][0]['memberships']['preterm'], 0)

    def test_preterm_or_low_weight_prompts_survive_low_fuzzy_result(self):
        result = self.result(week=36.5, weight=2499)
        self.assertIn('Preterm birth', ' '.join(result['birth_monitoring']['concerns']))
        self.assertIn('Low birth weight', ' '.join(result['birth_monitoring']['concerns']))
        self.assertIn('preterm/low-birth-weight pathway', ' '.join(result['birth_monitoring']['actions']))

    def test_severe_findings_prompt_review_without_overriding_other_modules(self):
        result = self.result(week=30, weight=1300)
        self.assertEqual(result['birth_monitoring']['priority'], 'Prompt neonatal monitoring review')
        self.assertEqual(result['module_actions'][1]['priority'], result['birth_monitoring']['priority'])
        self.assertEqual(result['immediate_condition_risk_level'], 'Low')
        self.assertEqual(result['family_history_follow_up_level'], 'Low')

    def test_very_low_weight_review_is_independent_of_moderate_index(self):
        result = self.result(weight=1499)
        self.assertEqual(result['birth_related_risk_level'], 'Moderate')
        self.assertEqual(result['birth_monitoring']['priority'], 'Prompt neonatal monitoring review')

    def test_age_context_has_no_physical_monitoring_flag(self):
        result = self.result(age=48)
        self.assertEqual(result['birth_monitoring']['priority'], 'Routine birth follow-up')
        self.assertIn('maternal age alone', ' '.join(result['birth_monitoring']['actions']))

    def test_result_reason_explains_mixed_outputs_without_forcing_high_label(self):
        result = self.result(week=34, weight=2000)
        birth = result['birth_monitoring']
        self.assertEqual(result['birth_related_risk_level'], 'Moderate')
        self.assertEqual(birth['output_activations'], {'low': 0.0, 'moderate': 1.0, 'high': 1.0})
        self.assertIn('Preterm with low birth weight', birth['result_reason'])
        self.assertIn('A High rule is active', birth['result_reason'])
        self.assertIn('69.0/100 (Moderate)', birth['summary'])

    def test_reassuring_summary_and_reason_use_only_recorded_findings(self):
        birth = self.result()['birth_monitoring']
        self.assertIn('39 weeks (full term)', birth['summary'])
        self.assertIn('3200 g', birth['summary'])
        self.assertIn('no reported delivery complication', birth['summary'])
        self.assertIn('Term, normal weight, no complication', birth['result_reason'])
        self.assertNotIn('A High rule is active', birth['result_reason'])
        self.assertIn('not a complete or validated estimate', birth['limitations'])

    def test_older_saved_explanation_has_summary_fallback(self):
        result = self.result()
        del result['birth_monitoring']['summary']
        del result['birth_monitoring']['result_reason']
        del result['birth_monitoring']['finding_facts']
        del result['birth_monitoring']['reason_facts']
        with application.app.test_request_context('/'):
            html = render_template('_birth_summary.html', results=result)
        self.assertIn('Gestational age: 39 weeks', html)
        self.assertIn('Birth-related monitoring index: 19.4/100', html)

    def test_user_example_is_factual_and_has_only_weak_high_overlap(self):
        result = self.result(week=39, weight=3628.74, age=29, complication=1)
        birth = result['birth_monitoring']
        self.assertAlmostEqual(result['birth_related_risk_index'],52.6,delta=.1)
        self.assertEqual(result['birth_related_risk_level'],'Moderate')
        self.assertIn('Birth weight: 3628.74 g', ' '.join(birth['finding_facts']))
        self.assertAlmostEqual(birth['output_activations']['high'], .07185)
        with application.app.test_request_context('/'):
            html = render_template('_birth_summary.html', results=result)
        self.assertIn('<li>Maternal age: 29 years', html)
        self.assertIn('<li>Reported delivery complication: Moderate rule activation 1.00.', html)
        self.assertNotIn('Main rule signals:',html)

    def test_results_saved_snapshot_and_pdf_include_explanations(self):
        raw = valid_form(birth_week='30', birth_weight='1300', weight_unit='g', maternal_age='28', delivery_comp='0')
        values, errors, _ = application.validate_submission(raw)
        self.assertFalse(errors)
        result = self.result(30, 1300)
        result['weight_display'] = '1300 g'
        with application.app.app_context():
            record = build_assessment_record(values, result, raw, None)
            record.id = 1
            payload = application.build_report_payload(values, result)
        with application.app.test_request_context('/'):
            html = render_template('results.html', results=result)
            detail = render_template('assessment_detail.html', assessment=record, plots={})
        pdf = '\n'.join(p.extract_text() for p in PdfReader(build_pdf_report(payload)).pages)
        self.assertEqual(record.result_snapshot['birth_monitoring'], result['birth_monitoring'])
        for output in (html, detail, pdf):
            self.assertIn('Recorded birth findings and final result', output)
            self.assertIn('Reason for this result', output)
            self.assertIn('rule activation', output)
            self.assertIn('Monitoring concerns', output)
            self.assertIn('Recommended monitoring actions', output)
            self.assertIn('0.25', output)
            self.assertIn('clinical review', output)


if __name__ == '__main__':
    unittest.main()
