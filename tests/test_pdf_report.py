import unittest

from pypdf import PdfReader
from werkzeug.security import generate_password_hash

import app as application
from extensions import db
from models import Assessment, User
from pdf_report import build_pdf_report


def sample_report():
    return {
        'generated_at': '2026-08-21 18:30 +0630',
        'inputs': {
            'birth_week': 36.5,
            'birth_weight': '2.35 kg (2350g)',
            'maternal_age': 31,
            'child_gender': 'Female',
            'delivery_type': 'Cesarean Section',
            'delivery_complication': 'Yes',
            'family_history_status': 'Yes',
            'family_disease': 'Congenital Deafness',
            'affected_relative': 'Other family member',
        },
        'apgar': {
            'components': [
                {'name': 'Appearance', 'score': 1, 'label': 'Pink body, blue hands/feet', 'note': 'Some bluish color in hands or feet.'},
                {'name': 'Pulse', 'score': 2, 'label': 'Strong (100+ bpm)', 'note': 'Heart rate is in the stronger range.'},
                {'name': 'Grimace', 'score': 1, 'label': 'Grimace only', 'note': 'Limited response to stimulation.'},
                {'name': 'Activity', 'score': 2, 'label': 'Active movement', 'note': 'Good muscle tone and movement.'},
                {'name': 'Respiration', 'score': 1, 'label': 'Weak or irregular', 'note': 'Breathing effort needs attention.'},
            ],
            'total': 7,
            'category': 'Normal (7-10)',
            'breakdown': 'The calculated APGAR total is in the generally stable range.',
        },
        'risk_modules': [
            {'name': 'Immediate Condition Risk', 'label': 'Immediate', 'risk_index': 41.2, 'level': 'Moderate', 'description': 'APGAR is the main signal.'},
            {'name': 'Birth-Related Risk', 'label': 'Birth Risk', 'risk_index': 63.8, 'level': 'Moderate', 'description': 'Uses birth information with overlapping fuzzy memberships.'},
            {'name': 'Family-History Risk', 'label': 'Family Risk', 'risk_index': 45.0, 'level': 'Moderate', 'description': 'Family history may need additional attention.'},
        ],
        'family_conditions': [
            {
                'disease': 'Congenital Deafness',
                'affected_relative': 'Other family member',
                'risk_index': 45.0,
            },
        ],
        'overall_risk_index': 65.4,
        'risk_level': 'Moderate',
        'confidence_level': 'Moderate',
        'confidence_reasons': [
            'All important inputs were complete and valid.',
            'The final fuzzy levels showed a usable but not strong separation.',
        ],
        'user_guidance': {
            'short_summary': 'A few factors in the information entered may need closer attention and follow-up.',
            'main_notices': ['Baby was born earlier than expected.', 'Birth weight is lower than the usual range.'],
            'next_steps': ['Arrange or continue follow-up with a healthcare professional.', 'Do not rely on this result alone for medical decisions.'],
            'urgent_help_signs': ['The baby has serious difficulty breathing.', 'The baby is difficult to wake or is not feeding normally.'],
        },
        'main_contributing_factors': [
            {'name': 'Preterm gestational age', 'description': 'Gestational-age membership is strongest in the preterm set.'},
            {'name': 'Low birth weight', 'description': 'Birth-weight membership is strongest in the low set.'},
        ],
        'lower_impact_factors': [
            {'name': 'Typical maternal age range', 'description': 'Maternal-age membership is strongest in the typical range.'},
        ],
        'triggered_rules': [
            {
                'id': 'BR-06',
                'name': 'Preterm with low birth weight',
                'description': 'Preterm gestation together with low birth weight elevates birth-related risk.',
                'outcome': 'high',
                'activation': 0.75,
            },
        ],
        'recommendation': 'Arrange or continue follow-up with a healthcare professional and pay closer attention to the highlighted factors.',
        'plot_paths': {},
    }


class PdfReportTests(unittest.TestCase):
    def setUp(self):
        application.app.config.update(TESTING=True, SECRET_KEY='pdf-test-secret')
        with application.app.app_context():
            db.create_all()
            db.session.query(Assessment).delete()
            db.session.query(User).delete()
            db.session.add(User(
                name='PDF User',
                email='pdf@example.com',
                password_hash=generate_password_hash('test-password'),
            ))
            db.session.commit()
        self.client = application.app.test_client()
        response = self.client.post('/login', data={
            'email': 'pdf@example.com',
            'password': 'test-password',
        })
        self.assertEqual(response.status_code, 302)

    def tearDown(self):
        with application.app.app_context():
            db.session.rollback()
            db.session.query(Assessment).delete()
            db.session.query(User).delete()
            db.session.commit()

    def test_pdf_contains_input_and_result_sections(self):
        report = sample_report()
        report['plot_paths'] = {
            'apgar': 'static/apgar_fuzzy.png',
            'week': 'static/week_fuzzy.png',
            'weight': 'static/weight_fuzzy.png',
            'age': 'static/age_fuzzy.png',
            'genetic': 'static/genetic_risks.png',
            'final': 'static/final_risk.png',
        }
        stream = build_pdf_report(report)
        reader = PdfReader(stream)
        text = '\n'.join(page.extract_text() or '' for page in reader.pages)

        self.assertGreaterEqual(len(reader.pages), 1)
        self.assertEqual(reader.metadata.title, 'Newborn Health Risk Assessment Results')
        self.assertIn('APGAR Score Breakdown', text)
        self.assertIn('Birth Summary', text)
        self.assertIn('Immediate Condition Risk', text)
        self.assertIn('Birth-Related Risk', text)
        self.assertIn('Family-History Risk', text)
        self.assertIn('Birth Chart Summary', text)
        self.assertIn('Overall Assessment Result', text)
        self.assertIn('Confidence Basis', text)
        self.assertIn('Assessment Factors', text)
        self.assertIn('Important Triggered Fuzzy Rules', text)
        self.assertIn('Overall Risk Index Chart', text)
        self.assertIn('65.4 / 100', text)
        self.assertIn('Confidence:', text)
        self.assertIn('BR-06', text)

    def test_download_endpoint_returns_pdf_attachment(self):
        token = application._report_serializer().dumps(sample_report())

        response = self.client.post('/report.pdf', data={'report_token': token})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'application/pdf')
        self.assertIn('newborn_health_risk_summary.pdf', response.headers['Content-Disposition'])
        self.assertTrue(response.data.startswith(b'%PDF'))

    def test_download_endpoint_rejects_tampered_token(self):
        response = self.client.post('/report.pdf', data={'report_token': 'tampered'})

        self.assertEqual(response.status_code, 400)
        self.assertIn(b'invalid', response.data)


if __name__ == '__main__':
    unittest.main()
