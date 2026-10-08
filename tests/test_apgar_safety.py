import itertools
import unittest
from unittest.mock import patch
from apgar_safety import check_apgar_safety
from fuzzy_logic import assess_risk, calculate_apgar, defuzzify_risk


class ApgarSafetyTests(unittest.TestCase):
    def test_all_component_combinations(self):
        for values in itertools.product(range(3), repeat=5):
            with self.subTest(values=values):
                safety = check_apgar_safety(*values)
                self.assertEqual(safety['active'], values[1] < 2 or values[4] < 2)
                score, _, _, severity, _ = calculate_apgar(*values)
                self.assertEqual(score, sum(values))
                self.assertEqual(severity, 'good' if score >= 7 else 'moderate' if score >= 4 else 'critical')

    def test_invalid_components_rejected_before_total(self):
        for invalid in (-1, 3, 1.5, True, None, '2'):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                calculate_apgar(2, invalid, 2, 2, 2)

    @patch('fuzzy_logic.generate_visualizations')
    def test_reassuring_totals_cannot_cancel_urgent_components(self, plots):
        plots.side_effect = lambda inputs, levels, *args, **kwargs: (defuzzify_risk(levels or kwargs['module_risk_levels']['immediate']), {})
        for pulse, respiration in ((0, 2), (1, 2), (2, 0), (2, 1), (0, 0)):
            with self.subTest(pulse=pulse, respiration=respiration):
                result = assess_risk(2, pulse, 2, 2, respiration, 39, 3200, 28,
                                     'vaginal', 0, {'status': 'no'}, 'male')
                self.assertTrue(result['safety_override']['active'])
                self.assertEqual(result['risk_level'], 'High')
                self.assertEqual(result['immediate_condition_risk_level'], 'High')
                self.assertGreaterEqual(result['overall_risk_index'], 70)
                self.assertIn('Do not wait', result['recommendation'])
                self.assertEqual(result['triggered_rules'][0]['module'], 'Safety override')
                self.assertNotIn('Stable APGAR pattern', [f['name'] for f in result['lower_impact_factors']])
                self.assertIsNone(plots.call_args.args[1])

    @patch('fuzzy_logic.generate_visualizations')
    def test_normal_components_preserve_fuzzy_result(self, plots):
        plots.side_effect = lambda inputs, levels, *args, **kwargs: (defuzzify_risk(levels or kwargs['module_risk_levels']['immediate']), {})
        result = assess_risk(2, 2, 2, 2, 2, 39, 3200, 28,
                             'vaginal', 0, {'status': 'no'}, 'male')
        self.assertFalse(result['safety_override']['active'])
        self.assertEqual(result['overall_risk_index'], result['unoverridden_final_risk_index'])

    @patch('fuzzy_logic.generate_visualizations')
    def test_alert_in_html_and_pdf(self, plots):
        from flask import render_template
        from pypdf import PdfReader
        import app as application
        from pdf_report import build_pdf_report
        from test_pdf_report import sample_report
        plots.side_effect = lambda inputs, levels, *args, **kwargs: (defuzzify_risk(levels or kwargs['module_risk_levels']['immediate']), {
            key: '' for key in ('apgar', 'week', 'weight', 'age', 'genetic', 'immediate', 'birth', 'family', 'final')})
        result = assess_risk(2, 0, 2, 2, 2, 39, 3200, 28,
                             'vaginal', 0, {'status': 'no'}, 'male')
        with application.app.test_request_context('/'):
            html = render_template('results.html', results=result)
        self.assertIn('Urgent APGAR component alert', html)
        self.assertIn('No heartbeat detected', html)
        report = sample_report()
        report['safety_override'] = result['safety_override']
        text = '\n'.join(page.extract_text() for page in PdfReader(build_pdf_report(report)).pages)
        self.assertIn('Urgent APGAR component alert', text)
        self.assertIn('No heartbeat detected', text)
        self.assertIn('Do not wait', text)
