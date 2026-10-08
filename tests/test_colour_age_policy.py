import unittest
from unittest.mock import patch
from flask import render_template
from pypdf import PdfReader
import app as application
from apgar_safety import check_apgar_safety
from fuzzy_logic import assess_risk, fuzzify_maternal_age, defuzzify_risk
from pdf_report import build_pdf_report
from test_database import valid_values
from persistence import build_assessment_record


class ColourAgePolicyTests(unittest.TestCase):
    @staticmethod
    def plots(inputs, levels, *args, **kwargs):
        return defuzzify_risk(levels or kwargs['module_risk_levels']['immediate']), {k: '' for k in ('apgar', 'week', 'weight', 'age', 'genetic', 'immediate', 'birth', 'family', 'final')}

    @staticmethod
    def result(appearance=0, age=23, pulse=2, respiration=2):
        return assess_risk(appearance, pulse, 1, 2, respiration, 38, 3200, age,
                           'vaginal', 0, {'status': 'unknown'}, 'male')

    def test_adult_ages_have_no_adolescent_or_older_contribution(self):
        for age in range(20, 35):
            with self.subTest(age=age):
                memberships = fuzzify_maternal_age(age)
                self.assertEqual(memberships['any_young'], 0)
                self.assertEqual(memberships['any_advanced'], 0)
                self.assertEqual(memberships['normal'], 1)

    def test_valid_age_range_has_coverage_and_preserves_context(self):
        for age in range(12, 61):
            self.assertGreater(max(fuzzify_maternal_age(age).values()), 0)
        self.assertGreater(fuzzify_maternal_age(19)['any_young'], 0)
        self.assertEqual(fuzzify_maternal_age(20)['any_young'], 0)
        self.assertGreater(fuzzify_maternal_age(36)['any_advanced'], 0)
        self.assertEqual(fuzzify_maternal_age(60)['very_advanced'], 1)
        for age in (18, 20, 35, 40, 45, 50):
            before, after = fuzzify_maternal_age(age - 0.001), fuzzify_maternal_age(age + 0.001)
            self.assertLess(max(abs(before[k] - after[k]) for k in before), 0.002)

    @patch('fuzzy_logic.generate_visualizations', side_effect=plots)
    def test_reported_case_has_colour_notice_and_no_age_23_penalty(self, _plots):
        result = self.result()
        self.assertEqual(result['apgar_score'], 7)
        self.assertAlmostEqual(result['immediate_condition_risk_index'], 28.6458666667)
        self.assertFalse(result['safety_override']['active'])
        self.assertEqual(result['overall_triage'], 'Urgent evaluation')
        self.assertEqual(result['birth_related_risk_level'], 'Low')
        self.assertAlmostEqual(result['birth_related_risk_index'], 19.4444444444)
        self.assertEqual(result['apgar_severity'], 'good')
        self.assertEqual(result['assessment_notices'][0]['component'], 'appearance')
        self.assertNotIn('BR-13', [r['id'] for r in result['triggered_rules']])
        self.assertIn('Skin colour alone', result['recommendation'])

    @patch('fuzzy_logic.generate_visualizations', side_effect=plots)
    def test_notice_is_removed_when_colour_selection_changes(self, _plots):
        for appearance in (1, 2):
            result = self.result(appearance=appearance)
            self.assertNotIn('appearance', [n['component'] for n in result['assessment_notices']])
            self.assertEqual(result['overall_triage'], 'Closer monitoring and professional review')

    @patch('fuzzy_logic.generate_visualizations', side_effect=plots)
    def test_heartbeat_override_remains_dominant(self, _plots):
        result = self.result(pulse=0)
        self.assertTrue(result['safety_override']['active'])
        self.assertEqual(result['risk_level'], 'High')
        self.assertIn('Do not wait', result['recommendation'])
        self.assertTrue(result['assessment_notices'])

    @patch('fuzzy_logic.generate_visualizations', side_effect=plots)
    def test_notice_in_results_snapshot_and_pdf(self, _plots):
        result = self.result()
        result['weight_display'] = '3200 g'
        values, raw = valid_values()
        values.update(appearance=0, pulse=2, grimace=1, activity=2, respiration=2,
                      birth_week=38, birth_weight_g=3200, maternal_age=23,
                      family_history={'status': 'unknown', 'disease': '', 'affected_relative': ''})
        with application.app.app_context():
            record = build_assessment_record(values, result, raw, 1)
            record.id = 1
            payload = application.build_report_payload(values, result)
        with application.app.test_request_context('/'):
            html = render_template('results.html', results=result)
            detail = render_template('assessment_detail.html', assessment=record, plots={})
        text = '\n'.join(p.extract_text() for p in PdfReader(build_pdf_report(payload)).pages)
        for output in (html, detail, text):
            self.assertIn('Blue or pale all over', output)
            self.assertIn('Skin colour alone', output)
            self.assertIn('Urgent evaluation', output)
        self.assertEqual(record.result_snapshot['assessment_notices'], result['assessment_notices'])

    def test_form_alert_precedes_total_completion(self):
        from pathlib import Path
        form = Path('templates/form.html').read_text(encoding='utf-8')
        self.assertIn('apgarVals.appearance===0', form)
        self.assertIn('fiveComponentAlerts', form)
