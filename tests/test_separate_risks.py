import unittest
from unittest.mock import patch
from flask import render_template
from pypdf import PdfReader
import app as application
from fuzzy_logic import assess_risk, apply_hierarchical_risk_rules, defuzzify_risk
from pdf_report import build_pdf_report
from test_pdf_report import sample_report


class SeparateRiskTests(unittest.TestCase):
    @staticmethod
    def plots(inputs, levels, *args, **kwargs):
        return defuzzify_risk(levels or kwargs['module_risk_levels']['immediate']), {k: '' for k in ('apgar', 'week', 'weight', 'age', 'genetic', 'immediate', 'birth', 'family', 'final')}

    def test_family_index_never_changes_acute_rules(self):
        for immediate in (15, 50, 85):
            for birth in (15, 50, 85):
                baseline, rules = apply_hierarchical_risk_rules(immediate, birth, 0, True)
                self.assertNotIn('HR-07', [r['id'] for r in rules])
                self.assertNotIn('HR-04', [r['id'] for r in rules])
                for family in range(101):
                    self.assertEqual(baseline, apply_hierarchical_risk_rules(immediate, birth, family))

    @patch('fuzzy_logic.generate_visualizations', side_effect=plots)
    def test_family_history_changes_follow_up_only(self, _plots):
        results = [assess_risk(2, 2, 2, 2, 2, 39, 3200, 28, 'vaginal', 0, family, 'male')
                   for family in ({'status': 'no'}, {'status': 'unknown'},
                                  {'status': 'yes', 'disease': 'Muscular dystrophy', 'affected_relative': 'both_parents'})]
        for result in results:
            self.assertEqual(result['overall_triage'], 'Routine care and observation')
            self.assertEqual(result['overall_risk_index'], results[0]['overall_risk_index'])
            self.assertEqual(result['main_contributing_factors'], results[0]['main_contributing_factors'])
            self.assertEqual(result['user_guidance'], results[0]['user_guidance'])
        self.assertEqual(results[1]['family_history_follow_up_level'], 'Unknown')
        self.assertIn('genetic counselling', results[2]['family_history_follow_up'])
        self.assertNotEqual(results[0]['family_history_follow_up'], results[2]['family_history_follow_up'])

    @patch('fuzzy_logic.generate_visualizations', side_effect=plots)
    def test_urgent_override_and_birth_monitoring_remain_separate(self, _plots):
        urgent = assess_risk(2, 0, 2, 2, 2, 39, 3200, 28, 'vaginal', 0, {'status': 'no'}, 'male')
        monitoring = assess_risk(2, 2, 2, 2, 2, 30, 1300, 28, 'vaginal', 0, {'status': 'no'}, 'male')
        self.assertEqual(urgent['overall_triage'], 'Urgent evaluation')
        self.assertTrue(urgent['safety_override']['active'])
        self.assertEqual(monitoring['overall_triage'], 'Routine care and observation')
        self.assertEqual(monitoring['module_actions'][1]['priority'], 'Prompt neonatal monitoring review')

    @patch('fuzzy_logic.generate_visualizations', side_effect=plots)
    def test_html_and_pdf_show_separate_results_without_overall_index(self, _plots):
        result = assess_risk(2, 2, 2, 2, 2, 39, 3200, 28, 'vaginal', 0,
                             {'status': 'yes', 'disease': 'Muscular dystrophy', 'affected_relative': 'both_parents'}, 'male')
        with application.app.test_request_context('/'):
            html = render_template('results.html', results=result)
        report = sample_report()
        report.update({k: result[k] for k in ('assessment_semantics', 'overall_triage', 'family_history_follow_up', 'recommendation', 'module_actions')})
        text = '\n'.join(page.extract_text() for page in PdfReader(build_pdf_report(report)).pages)
        for output in (html, text):
            self.assertIn('Recommended actions by module', output)
            self.assertIn('Family-history follow-up', output)
            self.assertNotIn('Overall Risk Index Chart', output)
            self.assertNotIn('Hierarchical fuzzy result from immediate, birth-related, and family-history', output)

    @patch('fuzzy_logic.generate_visualizations', side_effect=plots)
    def test_saved_snapshot_and_pdf_payload_preserve_separate_semantics(self, _plots):
        from persistence import build_assessment_record
        from test_database import valid_values
        values, raw = valid_values()
        result = assess_risk(values['appearance'], values['pulse'], values['grimace'],
                             values['activity'], values['respiration'], values['birth_week'],
                             values['birth_weight_g'], values['maternal_age'], values['delivery_type'],
                             values['delivery_comp'], values['family_history'], values['child_gender'])
        result['weight_display'] = '2400 g'
        with application.app.app_context():
            record = build_assessment_record(values, result, raw, 1)
            record.id = 1
            payload = application.build_report_payload(values, result)
        self.assertEqual(record.algorithm_version, 'fuzzy-v6-birth-monitoring')
        self.assertEqual(record.result_snapshot['overall_triage'], result['overall_triage'])
        self.assertEqual(payload['family_history_follow_up'], result['family_history_follow_up'])
        with application.app.test_request_context('/'):
            detail = render_template('assessment_detail.html', assessment=record, plots={})
        self.assertIn('Recommended actions by module', detail)
        self.assertIn(result['overall_triage'], detail)
        self.assertNotIn('Overall Risk Index Chart', detail)
        self.assertNotIn('Legacy assessment:', detail)
