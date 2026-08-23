import unittest
from io import BytesIO

from pypdf import PdfReader
from werkzeug.security import check_password_hash, generate_password_hash

import app as application
from extensions import db
from models import Assessment, User
from persistence import build_assessment_record
from test_database import sample_results, valid_values


class AuthenticationRouteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        application.app.config.update(TESTING=True, SECRET_KEY='auth-test-secret')

    def setUp(self):
        with application.app.app_context():
            db.create_all()
            db.session.query(Assessment).delete()
            db.session.query(User).delete()
            db.session.commit()
        self.client = application.app.test_client()

    def tearDown(self):
        with application.app.app_context():
            db.session.rollback()
            db.session.query(Assessment).delete()
            db.session.query(User).delete()
            db.session.commit()

    @staticmethod
    def add_user(email, name='Test User', password='test-password'):
        with application.app.app_context():
            user = User(
                name=name,
                email=email,
                password_hash=generate_password_hash(password),
            )
            db.session.add(user)
            db.session.commit()
            return user.id

    def login(self, email='test@example.com', password='test-password'):
        return self.client.post('/login', data={
            'email': email,
            'password': password,
        })

    def test_registration_hashes_password_and_logs_user_in(self):
        response = self.client.post('/register', data={
            'name': 'New User',
            'email': 'new@example.com',
            'password': 'correct-horse',
            'confirm_password': 'correct-horse',
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers['Location'], '/')
        with application.app.app_context():
            user = User.query.filter_by(email='new@example.com').one()
            self.assertNotEqual(user.password_hash, 'correct-horse')
            self.assertTrue(check_password_hash(user.password_hash, 'correct-horse'))
        self.assertEqual(self.client.get('/').status_code, 200)

    def test_registration_rejects_mismatched_or_short_password(self):
        response = self.client.post('/register', data={
            'name': 'New User',
            'email': 'new@example.com',
            'password': 'short',
            'confirm_password': 'different',
        })

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Password must be at least', response.data)
        self.assertIn(b'Passwords do not match', response.data)

    def test_login_requires_valid_password_and_logout_clears_session(self):
        self.add_user('test@example.com')

        bad_login = self.login(password='wrong')
        self.assertEqual(bad_login.status_code, 200)
        self.assertIn(b'Invalid email or password', bad_login.data)

        response = self.login()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers['Location'], '/')
        self.assertEqual(self.client.get('/assessments').status_code, 200)

        self.assertEqual(self.client.get('/logout').status_code, 302)
        protected = self.client.get('/')
        self.assertEqual(protected.status_code, 302)
        self.assertIn('/login', protected.headers['Location'])

    def test_assessment_history_and_detail_are_owner_scoped(self):
        owner_id = self.add_user('owner@example.com', name='Owner')
        other_id = self.add_user('other@example.com', name='Other')
        with application.app.app_context():
            values, raw_form = valid_values()
            record = build_assessment_record(values, sample_results(), raw_form, owner_id)
            db.session.add(record)
            db.session.commit()
            record_id = record.id

        self.login('other@example.com')
        history = self.client.get('/assessments')
        self.assertEqual(history.status_code, 200)
        self.assertNotIn(b'47.8 / 100', history.data)
        self.assertEqual(self.client.get(f'/assessments/{record_id}').status_code, 404)

        self.client.get('/logout')
        self.login('owner@example.com')
        owner_history = self.client.get('/assessments')
        self.assertIn(b'47.8 / 100', owner_history.data)
        self.assertEqual(self.client.get(f'/assessments/{record_id}').status_code, 200)
        self.assertNotEqual(owner_id, other_id)

    def test_new_assessment_and_profile_stay_accessible_when_logged_in(self):
        self.add_user('test@example.com')
        self.login()

        new_assessment = self.client.get('/')
        self.assertEqual(new_assessment.status_code, 200)

        profile_page = self.client.get('/profile')
        self.assertEqual(profile_page.status_code, 200)
        self.assertIn(b'Test User', profile_page.data)

    def _create_saved_assessment(self, owner_email):
        owner_id = self.add_user(owner_email, name='Owner')
        with application.app.app_context():
            values, raw_form = valid_values()
            record = build_assessment_record(values, sample_results(), raw_form, owner_id)
            db.session.add(record)
            db.session.commit()
            return record.id

    def test_saved_assessment_detail_matches_main_design_and_offers_pdf(self):
        record_id = self._create_saved_assessment('detail-owner@example.com')

        self.login('detail-owner@example.com')
        detail = self.client.get(f'/assessments/{record_id}')

        self.assertEqual(detail.status_code, 200)
        self.assertIn(b'Birth Summary of Emma', detail.data)
        self.assertIn(b'Assessment Factors', detail.data)
        self.assertIn(b'Main Contributing Factors', detail.data)
        self.assertIn(b'Lower-Impact Factors', detail.data)
        self.assertIn(b'Birth Chart Summary', detail.data)
        self.assertIn(f'static/a{record_id}_'.encode(), detail.data)
        self.assertIn('Download PDF Summary'.encode(), detail.data)
        self.assertIn(f'/assessments/{record_id}/report.pdf'.encode(), detail.data)

    def test_saved_assessment_pdf_downloads_with_baby_named_file(self):
        record_id = self._create_saved_assessment('pdf-owner@example.com')

        self.login('pdf-owner@example.com')
        response = self.client.get(f'/assessments/{record_id}/report.pdf')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'application/pdf')
        self.assertTrue(response.data.startswith(b'%PDF'))
        reader = PdfReader(BytesIO(response.data))
        text = '\n'.join(page.extract_text() or '' for page in reader.pages)
        self.assertIn('Birth Summary of Emma', text)

    def test_saved_assessment_pdf_is_owner_scoped(self):
        record_id = self._create_saved_assessment('scope-owner@example.com')

        other_id = self.add_user('scope-other@example.com', name='Other')
        self.assertNotEqual(record_id, other_id)
        self.login('scope-other@example.com')

        page = self.client.get(f'/assessments/{record_id}')
        pdf = self.client.get(f'/assessments/{record_id}/report.pdf')

        self.assertEqual(page.status_code, 404)
        self.assertEqual(pdf.status_code, 404)


if __name__ == '__main__':
    unittest.main()
