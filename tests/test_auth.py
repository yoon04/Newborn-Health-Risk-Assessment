import unittest
from unittest.mock import patch
import app as application
from extensions import db
from models import Assessment, User
from persistence import build_assessment_record
from test_database import sample_results, valid_values


class SharedDashboardTests(unittest.TestCase):
    def setUp(self):
        application.app.config.update(TESTING=True)
        with application.app.app_context():
            db.create_all(); db.session.query(Assessment).delete(); db.session.query(User).delete(); db.session.commit()
        self.client=application.app.test_client()

    def tearDown(self):
        with application.app.app_context():
            db.session.rollback(); db.session.query(Assessment).delete(); db.session.query(User).delete(); db.session.commit()

    def test_form_and_history_open_without_authentication(self):
        for path in ('/','/assessments'):
            response=self.client.get(path)
            self.assertEqual(response.status_code,200)
            self.assertIn(b'Shared History',response.data)
            self.assertNotIn(b'Log out',response.data)
            self.assertNotIn(b'profile-chip',response.data)

    def test_retired_account_pages_redirect_without_creating_users(self):
        for path in ('/login','/register','/logout'):
            self.assertEqual(self.client.get(path).status_code,302)
        self.client.post('/register',data={'name':'Staff','email':'staff@example.com','password':'password'})
        with application.app.app_context():
            self.assertEqual(User.query.count(),0)

    @patch('fuzzy_logic.generate_visualizations',return_value=(None,{}))
    def test_saved_records_and_pdf_are_shared(self,_plots):
        with application.app.app_context():
            values,raw=valid_values(); record=build_assessment_record(values,sample_results(),raw,None)
            db.session.add(record); db.session.commit(); record_id=record.id
        other_client=application.app.test_client()
        self.assertEqual(other_client.get(f'/assessments/{record_id}').status_code,200)
        pdf=other_client.get(f'/assessments/{record_id}/report.pdf')
        self.assertEqual(pdf.status_code,200)
        self.assertTrue(pdf.data.startswith(b'%PDF'))
        self.assertEqual(other_client.get('/assessments/999999').status_code,404)

    @patch('fuzzy_logic.generate_visualizations',return_value=(None,{'apgar':'','week':'','weight':'','age':'','genetic':'','immediate':'','birth':'','family':'','final':None}))
    def test_anonymous_submission_saves_without_owner(self,_plots):
        from test_validation import valid_form
        response=self.client.post('/',data=valid_form())
        self.assertEqual(response.status_code,200)
        with application.app.app_context():
            self.assertIsNone(Assessment.query.one().user_id)
