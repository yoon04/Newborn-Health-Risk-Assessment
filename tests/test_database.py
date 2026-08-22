import unittest
from unittest.mock import patch

from flask import Flask
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.datastructures import MultiDict
from werkzeug.security import generate_password_hash

import app as application
from extensions import db
from models import Assessment, User
from persistence import ALGORITHM_VERSION, build_assessment_record, save_assessment


def valid_values():
    form = MultiDict({
        'appearance': '2',
        'pulse': '2',
        'grimace': '1',
        'activity': '2',
        'respiration': '2',
        'birth_week': '36.5',
        'birth_weight': '2.4',
        'weight_unit': 'kg',
        'maternal_age': '31',
        'child_gender': 'female',
        'delivery_type': 'assisted',
        'delivery_comp': '1',
        'family_history_status': 'yes',
        'family_disease': 'cystic_fibrosis',
        'affected_relative': 'mother',
    })
    values, errors, _rows = application.validate_submission(form)
    assert errors == {}
    return values, form.to_dict(flat=True)


def sample_results():
    return {
        'apgar_score': 9,
        'apgar_category': 'Normal (7-10)',
        'apgar_severity': 'good',
        'apgar_breakdown': 'The APGAR result is in the stable range.',
        'component_detail': {
            'appearance': {'score': 2, 'label': 'Pink all over', 'note': 'Good color.'},
            'pulse': {'score': 2, 'label': 'Strong (100+ bpm)', 'note': 'Strong pulse.'},
            'grimace': {'score': 1, 'label': 'Grimace only', 'note': 'Some response.'},
            'activity': {'score': 2, 'label': 'Active movement', 'note': 'Good movement.'},
            'respiration': {'score': 2, 'label': 'Good breathing', 'note': 'Good breathing effort.'},
        },
        'immediate_condition_risk_index': 18.5,
        'immediate_condition_risk_level': 'Low',
        'birth_related_risk_index': 42.25,
        'birth_related_risk_level': 'Moderate',
        'family_history_risk_index': 52.0,
        'family_history_risk_level': 'Moderate',
        'overall_risk_index': 47.75,
        'risk_level': 'Moderate',
        'confidence_level': 'High',
        'confidence_reasons': ['All important inputs were complete and valid.'],
        'main_contributing_factors': [{'name': 'Preterm gestational age', 'description': 'Example factor.'}],
        'lower_impact_factors': [{'name': 'Stable APGAR pattern', 'description': 'Example lower-impact factor.'}],
        'triggered_rules': [{'id': 'BR-06', 'module': 'Birth-Related', 'name': 'Preterm with low birth weight', 'description': 'Example rule.', 'outcome': 'moderate', 'activation': 0.72}],
        'user_guidance': {'short_summary': 'Follow up with a healthcare professional.'},
        'family_history_summary': 'A disease was reported in one parent.',
        'recommendation': 'Arrange follow-up with a healthcare professional.',
        'plot_paths': {},
        'confidence_details': {'level': 'High'},
        'family_history_items': [{'disease': 'Cystic fibrosis', 'affected_relative': 'Mother', 'risk_index': 52.0}],
    }


class DatabasePersistenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_app = Flask('database-tests')
        cls.test_app.config.update(
            TESTING=True,
            SQLALCHEMY_DATABASE_URI='sqlite:///:memory:',
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
        )
        db.init_app(cls.test_app)
        cls.context = cls.test_app.app_context()
        cls.context.push()
        db.create_all()

    @classmethod
    def tearDownClass(cls):
        db.session.remove()
        db.drop_all()
        cls.context.pop()

    def tearDown(self):
        db.session.rollback()
        db.session.query(Assessment).delete()
        db.session.query(User).delete()
        db.session.commit()

    @staticmethod
    def create_user(email='test@example.com'):
        user = User(
            name='Test User',
            email=email,
            password_hash=generate_password_hash('test-password'),
        )
        db.session.add(user)
        db.session.commit()
        return user

    def test_record_preserves_raw_inputs_and_calculated_results(self):
        values, raw_form = valid_values()
        user = self.create_user()
        record = save_assessment(values, sample_results(), raw_form, user.id)

        stored = db.session.get(Assessment, record.id)
        self.assertIsNotNone(stored)
        self.assertEqual(stored.appearance, 2)
        self.assertEqual(stored.birth_weight_g, 2400)
        self.assertEqual(stored.raw_inputs['birth_weight'], '2.4')
        self.assertEqual(stored.raw_inputs['weight_unit'], 'kg')
        self.assertEqual(float(stored.overall_risk_index), 47.75)
        self.assertEqual(stored.risk_level, 'Moderate')
        self.assertEqual(stored.confidence_level, 'High')
        self.assertEqual(stored.algorithm_version, ALGORITHM_VERSION)
        self.assertEqual(stored.triggered_rules[0]['id'], 'BR-06')
        self.assertEqual(stored.user.name, 'Test User')
        self.assertEqual(stored.user.email, 'test@example.com')

    def test_assessments_are_saved_for_the_supplied_user(self):
        values, raw_form = valid_values()
        first_user = self.create_user('first@example.com')
        second_user = self.create_user('second@example.com')
        first = save_assessment(values, sample_results(), raw_form, first_user.id)
        second = save_assessment(values, sample_results(), raw_form, second_user.id)

        self.assertNotEqual(first.user_id, second.user_id)
        self.assertEqual(User.query.count(), 2)

    def test_commit_error_can_be_rolled_back_without_a_partial_record(self):
        values, raw_form = valid_values()
        user = self.create_user()
        with patch.object(db.session, 'commit', side_effect=SQLAlchemyError('database unavailable')):
            with self.assertRaises(SQLAlchemyError):
                save_assessment(values, sample_results(), raw_form, user.id)
            db.session.rollback()

        self.assertEqual(Assessment.query.count(), 0)
        self.assertEqual(User.query.count(), 1)

    def test_record_builder_does_not_change_fuzzy_result_values(self):
        values, raw_form = valid_values()
        results = sample_results()
        user = self.create_user()
        record = build_assessment_record(values, results, raw_form, user.id)

        self.assertEqual(float(record.overall_risk_index), results['overall_risk_index'])
        self.assertEqual(record.triggered_rules, results['triggered_rules'])
        self.assertEqual(record.main_contributing_factors, results['main_contributing_factors'])


if __name__ == '__main__':
    unittest.main()
