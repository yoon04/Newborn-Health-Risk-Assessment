import unittest
from unittest.mock import patch

from fuzzy_logic import (
    apply_birth_related_rules,
    apply_hierarchical_risk_rules,
    apply_immediate_condition_rules,
    assess_risk,
    calculate_apgar,
    defuzzify_risk,
    fuzzify_apgar,
    fuzzify_birth_week,
    fuzzify_birth_weight,
    fuzzify_delivery_comp,
    fuzzify_maternal_age,
)


class ApgarTests(unittest.TestCase):
    def test_total_and_category_are_derived_from_five_components(self):
        score, _breakdown, category, severity, details = calculate_apgar(2, 2, 1, 1, 1)

        self.assertEqual(score, 7)
        self.assertEqual(category, 'Normal (7–10)')
        self.assertEqual(severity, 'good')
        self.assertEqual(len(details), 5)

    def test_valid_extreme_scores_keep_full_fuzzy_membership(self):
        self.assertEqual(fuzzify_apgar(0)['low'], 1.0)
        self.assertEqual(fuzzify_apgar(10)['high'], 1.0)

    def test_integer_category_boundaries_have_overlapping_memberships(self):
        score_four = fuzzify_apgar(4)
        score_seven = fuzzify_apgar(7)

        self.assertGreater(score_four['low'], 0)
        self.assertGreater(score_four['medium'], 0)
        self.assertGreater(score_seven['medium'], 0)
        self.assertGreater(score_seven['high'], 0)


class DeliveryComplicationTests(unittest.TestCase):
    @staticmethod
    def fuzzy_inputs(complication):
        return {
            'apgar': fuzzify_apgar(5),
            'birth_week': fuzzify_birth_week(39),
            'birth_weight': fuzzify_birth_weight(3200),
            'maternal_age': fuzzify_maternal_age(28),
            'delivery_comp': fuzzify_delivery_comp(complication),
        }

    def test_complication_interacts_with_medium_apgar(self):
        without_complication = apply_immediate_condition_rules(self.fuzzy_inputs(0))
        with_complication = apply_immediate_condition_rules(self.fuzzy_inputs(1))

        self.assertEqual(without_complication['high'], 0)
        self.assertGreater(with_complication['high'], without_complication['high'])

    def test_delivery_method_is_not_part_of_fuzzy_inputs(self):
        inputs = self.fuzzy_inputs(0)

        self.assertNotIn('delivery_type', inputs)
        self.assertEqual(inputs['delivery_comp']['normal'], 1.0)
        self.assertEqual(inputs['delivery_comp']['complicated'], 0.0)

    @patch('fuzzy_logic.generate_visualizations', return_value=(25.0, {}))
    def test_cesarean_alone_does_not_change_risk(self, generate_visualizations):
        common = (2, 2, 2, 2, 2, 39, 3200, 28)

        family_history = {'status': 'no', 'disease': '', 'affected_relative': ''}
        vaginal = assess_risk(*common, 'vaginal', 0, family_history, 'female')
        cesarean = assess_risk(*common, 'cesarean', 0, family_history, 'female')

        vaginal_rule_levels = generate_visualizations.call_args_list[0].args[1]
        cesarean_rule_levels = generate_visualizations.call_args_list[1].args[1]
        self.assertEqual(vaginal_rule_levels, cesarean_rule_levels)
        self.assertEqual(vaginal['birth_related_risk_index'], cesarean['birth_related_risk_index'])
        self.assertEqual(vaginal['overall_risk_index'], cesarean['overall_risk_index'])
        self.assertEqual(cesarean['delivery_type'], 'Cesarean Section')
        self.assertEqual(cesarean['delivery_complication'], 'No')


class GestationAndWeightMembershipTests(unittest.TestCase):
    def test_gestational_boundaries_overlap(self):
        at_30_weeks = fuzzify_birth_week(30)
        at_36_weeks = fuzzify_birth_week(36)
        at_41_weeks = fuzzify_birth_week(41)

        self.assertGreater(at_30_weeks['very_preterm'], 0)
        self.assertGreater(at_30_weeks['preterm'], 0)
        self.assertGreater(at_36_weeks['preterm'], 0)
        self.assertGreater(at_36_weeks['term'], 0)
        self.assertGreater(at_41_weeks['term'], 0)
        self.assertGreater(at_41_weeks['postterm'], 0)

    def test_birth_weight_boundaries_overlap(self):
        overlaps = (
            (900, 'extremely_low', 'very_low'),
            (1400, 'very_low', 'low'),
            (2400, 'low', 'normal'),
            (3900, 'normal', 'high'),
            (4800, 'high', 'very_high'),
        )
        for weight, first, second in overlaps:
            with self.subTest(weight=weight):
                memberships = fuzzify_birth_weight(weight)
                self.assertGreater(memberships[first], 0)
                self.assertGreater(memberships[second], 0)


class HierarchicalRiskTests(unittest.TestCase):
    @staticmethod
    def inputs(apgar, week, weight, age=28, complication=0):
        return {
            'apgar': fuzzify_apgar(apgar),
            'birth_week': fuzzify_birth_week(week),
            'birth_weight': fuzzify_birth_weight(weight),
            'maternal_age': fuzzify_maternal_age(age),
            'delivery_comp': fuzzify_delivery_comp(complication),
        }

    def test_preterm_and_low_weight_raise_birth_related_risk(self):
        stable = apply_birth_related_rules(self.inputs(9, 39, 3200))
        preterm_low_weight = apply_birth_related_rules(self.inputs(9, 34, 2000))

        self.assertGreater(preterm_low_weight['high'], stable['high'])
        self.assertGreater(defuzzify_risk(preterm_low_weight), defuzzify_risk(stable))

    def test_stable_term_normal_case_activates_low_overall_risk(self):
        inputs = self.inputs(9, 39, 3200)
        immediate = defuzzify_risk(apply_immediate_condition_rules(inputs))
        birth = defuzzify_risk(apply_birth_related_rules(inputs))
        final = apply_hierarchical_risk_rules(immediate, birth, 0)

        self.assertGreater(final['low'], 0)
        self.assertEqual(final['high'], 0)

    def test_high_immediate_risk_is_not_cancelled_by_low_family_risk(self):
        final = apply_hierarchical_risk_rules(85, 20, 0)

        self.assertGreater(final['high'], 0)

    def test_high_birth_risk_remains_elevated_with_low_family_risk(self):
        final = apply_hierarchical_risk_rules(20, 85, 0)

        self.assertGreater(final['high'], 0)

    def test_moderate_immediate_and_birth_risk_interact(self):
        final = apply_hierarchical_risk_rules(50, 50, 0)

        self.assertGreater(final['high'], 0)


if __name__ == '__main__':
    unittest.main()
