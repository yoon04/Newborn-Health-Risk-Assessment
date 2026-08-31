import unittest
from unittest.mock import patch

from flask import render_template

import app as application
from fuzzy_logic import (
    apply_birth_related_rules,
    apply_family_history_rules,
    apply_immediate_condition_rules,
    assess_risk,
    build_user_guidance,
    calculate_assessment_confidence,
    defuzzify_risk,
    fuzzify_apgar,
    fuzzify_birth_week,
    fuzzify_birth_weight,
    fuzzify_delivery_comp,
    fuzzify_maternal_age,
)


class RuleTraceTests(unittest.TestCase):
    @staticmethod
    def inputs(apgar=5, week=34, weight=2000, complication=1):
        return {
            'apgar': fuzzify_apgar(apgar),
            'birth_week': fuzzify_birth_week(week),
            'birth_weight': fuzzify_birth_weight(weight),
            'maternal_age': fuzzify_maternal_age(28),
            'delivery_comp': fuzzify_delivery_comp(complication),
        }

    def test_rule_trace_does_not_change_immediate_levels(self):
        inputs = self.inputs()
        regular_levels = apply_immediate_condition_rules(inputs)
        traced_levels, rules = apply_immediate_condition_rules(inputs, return_rules=True)

        self.assertEqual(regular_levels, traced_levels)
        self.assertEqual({rule['id'] for rule in rules}, {'IM-01', 'IM-02', 'IM-03', 'IM-04', 'IM-05'})
        interaction = next(rule for rule in rules if rule['id'] == 'IM-05')
        self.assertGreater(interaction['activation'], 0)

    def test_preterm_low_weight_rule_reports_exact_activation(self):
        inputs = self.inputs(week=34, weight=2000)
        levels, rules = apply_birth_related_rules(inputs, return_rules=True)
        interaction = next(rule for rule in rules if rule['id'] == 'BR-06')
        expected = min(inputs['birth_week']['preterm'], inputs['birth_weight']['any_low'])

        self.assertEqual(interaction['activation'], expected)
        self.assertEqual(levels['high'], max(
            rule['activation'] for rule in rules if rule['outcome'] == 'high'
        ))


class ConfidenceTests(unittest.TestCase):
    def test_clear_activation_with_complete_inputs_is_high_confidence(self):
        confidence = calculate_assessment_confidence(
            {'low': 1.0, 'moderate': 0.2, 'high': 0.0},
            True,
            {'status': 'no', 'disease': '', 'affected_relative': ''},
        )
        self.assertEqual(confidence['level'], 'High')

    def test_unknown_family_history_caps_high_confidence(self):
        confidence = calculate_assessment_confidence(
            {'low': 1.0, 'moderate': 0.2, 'high': 0.0},
            True,
            {'status': 'unknown', 'disease': '', 'affected_relative': ''},
        )
        self.assertEqual(confidence['level'], 'Moderate')

    def test_overlapping_final_levels_produce_low_confidence(self):
        confidence = calculate_assessment_confidence(
            {'low': 0.50, 'moderate': 0.45, 'high': 0.40},
            True,
            {'status': 'no', 'disease': '', 'affected_relative': ''},
        )
        self.assertEqual(confidence['level'], 'Low')


class FamilyHistoryIndicatorTests(unittest.TestCase):
    @staticmethod
    def index(status, relative='', disease='Condition A'):
        levels = apply_family_history_rules({
            'status': status,
            'disease': disease if status == 'yes' else '',
            'affected_relative': relative if status == 'yes' else '',
        })
        return defuzzify_risk(levels)

    def test_simple_family_answers_have_ordered_indicator_strength(self):
        no_history = self.index('no')
        unknown_history = self.index('unknown')
        other_relative = self.index('yes', 'other_family_member')
        one_parent = self.index('yes', 'mother')
        both_parents = self.index('yes', 'both_parents')

        self.assertLess(no_history, unknown_history)
        self.assertLess(unknown_history, other_relative)
        self.assertLess(other_relative, one_parent)
        self.assertLess(one_parent, both_parents)

    def test_disease_name_does_not_invent_a_disease_specific_index(self):
        first = self.index('yes', 'father', disease='Condition A')
        second = self.index('yes', 'father', disease='Condition B')

        self.assertEqual(first, second)

    def test_family_rule_trace_contains_plain_relationship_rule(self):
        _levels, rules = apply_family_history_rules({
            'status': 'yes', 'disease': 'Condition', 'affected_relative': 'both_parents'
        }, return_rules=True)
        rule = next(item for item in rules if item['id'] == 'FH-06')

        self.assertEqual(rule['activation'], 1.0)


class UserGuidanceTests(unittest.TestCase):
    def test_recommendations_depend_on_risk_level(self):
        factors = [{'name': 'Preterm gestational age', 'role': 'impact'}]
        low = build_user_guidance('Low', factors, [])
        moderate = build_user_guidance('Moderate', factors, [])
        high = build_user_guidance('High', factors, [])

        self.assertIn('routine checkups', ' '.join(low['next_steps']))
        self.assertIn('follow-up', ' '.join(moderate['next_steps']))
        self.assertIn('prompt professional medical evaluation', ' '.join(high['next_steps']))
        self.assertNotEqual(low['short_summary'], high['short_summary'])


class AssessmentExplanationTests(unittest.TestCase):
    @patch('fuzzy_logic.generate_visualizations', return_value=(65.0, {}))
    def test_assessment_exposes_index_confidence_factors_and_rules(self, _plots):
        result = assess_risk(
            1, 1, 1, 1, 1,
            34, 2000, 28, 'vaginal', 1,
            {'status': 'no', 'disease': '', 'affected_relative': ''}, 'female',
        )

        self.assertEqual(result['overall_risk_index'], 65.0)
        self.assertIn(result['risk_level'], {'Low', 'Moderate', 'High'})
        self.assertIn(result['confidence_level'], {'Low', 'Moderate', 'High'})
        self.assertTrue(result['main_contributing_factors'])
        self.assertTrue(result['lower_impact_factors'])
        self.assertTrue(result['triggered_rules'])
        self.assertTrue(all('activation' in rule for rule in result['triggered_rules']))

    @patch('fuzzy_logic.generate_visualizations', return_value=(65.0, {'final': 'static/final_risk.png'}))
    def test_result_page_uses_risk_index_and_confidence_wording(self, _plots):
        result = assess_risk(
            1, 1, 1, 1, 1,
            34, 2000, 28, 'vaginal', 1,
            {'status': 'no', 'disease': '', 'affected_relative': ''}, 'female',
        )
        result['weight_display'] = '2.0 kg (2000g)'
        result['plot_paths'].update({
            'apgar': 'static/apgar_fuzzy.png',
            'week': 'static/week_fuzzy.png',
            'weight': 'static/weight_fuzzy.png',
            'age': 'static/age_fuzzy.png',
            'immediate': 'static/immediate_risk.png',
            'birth': 'static/birth_risk.png',
            'family': 'static/family_risk.png',
        })
        result['pdf_report_token'] = 'test-token'

        with application.app.test_request_context('/'):
            html = render_template('results.html', results=result)

        self.assertIn('APGAR Score Breakdown', html)
        self.assertIn('Birth Summary', html)
        self.assertIn('Immediate Condition Risk', html)
        self.assertIn('Birth-Related Risk', html)
        self.assertIn('Family-History Risk', html)
        self.assertIn('Immediate condition fuzzy output and risk-index centroid', html)
        self.assertIn('Overall Assessment Result', html)
        self.assertIn('Risk Index:', html)
        self.assertIn('Risk Level:', html)
        self.assertIn('Confidence:', html)
        self.assertIn('Important Triggered Fuzzy Rules', html)
        self.assertNotIn('65.0% risk', html)


if __name__ == '__main__':
    unittest.main()
