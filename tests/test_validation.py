import unittest
from unittest.mock import patch

from werkzeug.datastructures import MultiDict
from werkzeug.security import generate_password_hash

import app as application
from extensions import db
from models import Assessment, User
from persistence import build_assessment_record
from test_database import sample_results, valid_values


def valid_form(**overrides):
    data = {
        'baby_name': 'Baby Emma',
        'appearance': '2',
        'pulse': '2',
        'grimace': '2',
        'activity': '2',
        'respiration': '2',
        'birth_week': '38.5',
        'birth_weight': '3.2',
        'weight_unit': 'kg',
        'maternal_age': '28',
        'child_gender': 'male',
        'delivery_type': 'vaginal',
        'delivery_comp': '0',
        'family_history_status': 'no',
    }
    data.update(overrides)
    return MultiDict(data)


class SubmissionValidationTests(unittest.TestCase):
    def test_valid_submission_is_normalized(self):
        values, errors, rows = application.validate_submission(valid_form())

        self.assertEqual(errors, {})
        self.assertEqual(rows, [])
        self.assertEqual(values['appearance'], 2)
        self.assertEqual(values['baby_name'], 'Baby Emma')
        self.assertEqual(values['birth_week'], 38.5)
        self.assertEqual(values['maternal_age'], 28)
        self.assertEqual(values['birth_weight_g'], 3200)
        self.assertEqual(values['delivery_type'], 'vaginal')
        self.assertEqual(values['delivery_comp'], 0)
        self.assertEqual(values['family_history'], {
            'status': 'no', 'disease': '', 'affected_relative': ''
        })

    def test_baby_name_is_required_and_limited(self):
        _, errors, _ = application.validate_submission(valid_form(baby_name=''))
        self.assertIn('baby_name', errors)

        _, errors, _ = application.validate_submission(valid_form(baby_name='   '))
        self.assertIn('baby_name', errors)

        _, errors, _ = application.validate_submission(valid_form(baby_name='x' * 81))
        self.assertIn('baby_name', errors)

        values, errors, _ = application.validate_submission(valid_form(baby_name='  Li-Wei '))
        self.assertEqual(errors, {})
        self.assertEqual(values['baby_name'], 'Li-Wei')

    def test_missing_and_invalid_apgar_values_are_rejected(self):
        for value in ('', '-1', '3', '1.5', 'not-a-number'):
            with self.subTest(value=value):
                _, errors, _ = application.validate_submission(valid_form(appearance=value))
                self.assertIn('appearance', errors)

    def test_invalid_birth_values_are_rejected(self):
        cases = (
            ('birth_week', '', 'birth_week'),
            ('birth_week', 'nan', 'birth_week'),
            ('birth_week', '1_000', 'birth_week'),
            ('birth_week', '19.5', 'birth_week'),
            ('birth_week', '45.5', 'birth_week'),
            ('birth_week', '38.2', 'birth_week'),
            ('maternal_age', '-1', 'maternal_age'),
            ('maternal_age', '28.5', 'maternal_age'),
            ('maternal_age', '61', 'maternal_age'),
            ('birth_weight', 'nan', 'birth_weight'),
            ('birth_weight', '3.2kg', 'birth_weight'),
            ('birth_weight', '-3.2', 'birth_weight'),
            ('birth_weight', '0.05', 'birth_weight'),
            ('birth_weight', '6', 'birth_weight'),
            ('weight_unit', 'ounces', 'birth_weight'),
            ('child_gender', 'unknown', 'child_gender'),
            ('delivery_type', 'emergency', 'delivery_type'),
            ('delivery_comp', '2', 'delivery_comp'),
        )
        for field, value, error_field in cases:
            with self.subTest(field=field, value=value):
                _, errors, _ = application.validate_submission(valid_form(**{field: value}))
                self.assertIn(error_field, errors)

    def test_known_family_disease_is_accepted(self):
        form = valid_form(
            family_history_status='yes',
            family_disease='muscular_dystrophy',
            affected_relative='mother',
        )

        values, errors, rows = application.validate_submission(form)

        self.assertEqual(errors, {})
        self.assertEqual(rows, [])
        self.assertEqual(values['family_history']['disease'], 'Muscular dystrophy')
        self.assertEqual(values['family_history']['affected_relative'], 'mother')

    def test_incomplete_or_altered_family_values_are_rejected(self):
        cases = (
            ({'family_history_status': ''}, 'family_history_status'),
            ({'family_history_status': 'invented'}, 'family_history_status'),
            ({'family_history_status': 'yes', 'family_disease': '', 'affected_relative': 'mother'}, 'family_disease'),
            ({'family_history_status': 'yes', 'family_disease': 'diabetes', 'affected_relative': ''}, 'affected_relative'),
            ({'family_history_status': 'yes', 'family_disease': 'diabetes', 'affected_relative': 'carrier'}, 'affected_relative'),
            ({'family_history_status': 'yes', 'family_disease': 'made-up-condition', 'affected_relative': 'mother'}, 'family_disease'),
        )
        for changes, error_field in cases:
            with self.subTest(changes=changes):
                _, errors, _ = application.validate_submission(valid_form(**changes))
                self.assertIn(error_field, errors)

    def test_unknown_family_history_is_valid_without_disease_details(self):
        values, errors, _rows = application.validate_submission(
            valid_form(family_history_status='unknown')
        )

        self.assertEqual(errors, {})
        self.assertEqual(values['family_history']['status'], 'unknown')
        self.assertEqual(values['family_history']['disease'], '')

    def test_technical_genetic_fields_are_not_used(self):
        values, errors, _rows = application.validate_submission(valid_form(
            mode_0='xlinked', xlinked_status_0='carrier', genotype='Aa'
        ))

        self.assertEqual(errors, {})
        self.assertNotIn('mode', values['family_history'])
        self.assertNotIn('genotype', values['family_history'])


class RouteValidationTests(unittest.TestCase):
    def setUp(self):
        application.app.config.update(TESTING=True)
        with application.app.app_context():
            db.create_all()
            db.session.query(Assessment).delete()
            db.session.query(User).delete()
            user = User(
                name='Route Test User',
                email='route-test@example.com',
                password_hash=generate_password_hash('test-password'),
            )
            db.session.add(user)
            db.session.commit()
        self.client = application.app.test_client()
        response = self.client.post('/login', data={
            'email': 'route-test@example.com',
            'password': 'test-password',
        })
        self.assertEqual(response.status_code, 302)

    def tearDown(self):
        with application.app.app_context():
            db.session.rollback()
            db.session.query(Assessment).delete()
            db.session.query(User).delete()
            db.session.commit()

    def test_form_has_five_apgar_components_and_no_manual_total(self):
        response = self.client.get('/')

        self.assertEqual(response.status_code, 200)
        for field in application.APGAR_FIELDS:
            self.assertIn(f'name="{field}"'.encode(), response.data)
        self.assertNotIn(b'name="apgar_total"', response.data)

    def test_form_collects_baby_name(self):
        response = self.client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'name="baby_name"', response.data)

    def test_profile_page_shows_user_and_baby_summary(self):
        with application.app.app_context():
            user = User.query.filter_by(email='route-test@example.com').one()
            values, raw_form = valid_values()
            record = build_assessment_record(values, sample_results(), raw_form, user.id)
            db.session.add(record)
            db.session.commit()

        response = self.client.get('/profile')

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Route Test User', response.data)
        self.assertIn(b'Emma', response.data)

    def test_history_can_be_filtered_by_baby_name(self):
        with application.app.app_context():
            user = User.query.filter_by(email='route-test@example.com').one()
            values, raw_form = valid_values()
            record = build_assessment_record(values, sample_results(), raw_form, user.id)
            db.session.add(record)
            db.session.commit()

        all_history = self.client.get('/assessments')
        self.assertEqual(all_history.status_code, 200)
        self.assertIn(b'Emma', all_history.data)

        filtered = self.client.get('/assessments?baby=Emma')
        self.assertEqual(filtered.status_code, 200)
        self.assertIn(b'47.8 / 100', filtered.data)

        other_baby = self.client.get('/assessments?baby=Nobody')
        self.assertEqual(other_baby.status_code, 200)
        self.assertNotIn(b'47.8 / 100', other_baby.data)

    def test_form_uses_only_simple_family_history_questions(self):
        response = self.client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'name="family_history_status"', response.data)
        self.assertIn(b'name="family_disease"', response.data)
        self.assertIn(b'name="affected_relative"', response.data)
        self.assertIn(b'<select id="family_disease"', response.data)
        self.assertNotIn(b'<input type="text" id="family_disease"', response.data)
        self.assertEqual(len(application.FAMILY_DISEASE_OPTIONS), 20)
        for value, label in application.FAMILY_DISEASE_OPTIONS:
            self.assertIn(f'value="{value}"'.encode(), response.data)
            self.assertIn(label.encode(), response.data)
        self.assertIn(b'Other disease / not listed', response.data)
        for technical_name in (b'name="mode_', b'name="xlinked_', b'name="genotype"', b'name="carrier_status"'):
            self.assertNotIn(technical_name, response.data)

    def test_assessment_form_has_no_repeated_user_identity_inputs(self):
        response = self.client.get('/')

        self.assertNotIn(b'name="user_name"', response.data)
        self.assertNotIn(b'name="user_email"', response.data)
        self.assertNotIn(b'Signed in as', response.data)

    def test_pages_share_the_top_navigation(self):
        for path in ('/', '/assessments', '/profile'):
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200, path)
            self.assertIn(b'site-nav', response.data)
            self.assertIn(b'profile-chip', response.data)
        self.assertNotIn(b'Signed in as', self.client.get('/assessments').data)

    def test_logged_out_user_is_redirected_from_protected_history(self):
        self.client.get('/logout')

        response = self.client.get('/assessments')

        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.headers['Location'])

    @patch('app.assess_risk')
    def test_invalid_submission_never_reaches_fuzzy_assessment(self, assess_risk):
        response = self.client.post('/', data=valid_form(appearance='9'))

        self.assertEqual(response.status_code, 400)
        assess_risk.assert_not_called()
        self.assertIn(b'Select an APGAR score of 0, 1, or 2.', response.data)

    @patch('app.build_report_payload', return_value={})
    @patch('app.render_template', return_value='results rendered')
    @patch('app.assess_risk', return_value={})
    def test_valid_submission_reaches_fuzzy_assessment(
        self, assess_risk, _render_template, _build_report_payload
    ):
        response = self.client.post('/', data=valid_form())

        self.assertEqual(response.status_code, 200)
        assess_risk.assert_called_once()

    @patch('fuzzy_logic.generate_visualizations', return_value=(45.0, {
        'apgar': 'static/apgar_fuzzy.png',
        'week': 'static/week_fuzzy.png',
        'weight': 'static/weight_fuzzy.png',
        'age': 'static/age_fuzzy.png',
        'genetic': None,
        'final': 'static/final_risk.png',
    }))
    def test_real_submission_renders_detailed_result_page(self, _plots):
        response = self.client.post('/', data=valid_form(family_history_status='unknown'))

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'APGAR Score Breakdown', response.data)
        self.assertIn(b'Birth Summary of Baby Emma', response.data)
        self.assertNotIn(b"Baby&#39;s Name", response.data)
        self.assertNotIn(b"Baby's Name", response.data)
        self.assertIn(b'Immediate Condition Risk', response.data)
        self.assertIn(b'Birth-Related Risk', response.data)
        self.assertIn(b'Family-History Risk', response.data)
        self.assertIn(b'Overall Assessment Result', response.data)
        self.assertIn(b'Important Triggered Fuzzy Rules', response.data)
        self.assertIn(b'Family disease history is unknown', response.data)


if __name__ == '__main__':
    unittest.main()
