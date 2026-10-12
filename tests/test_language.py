import unittest
from pathlib import Path

from app import app


class LanguagePreferenceTests(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True)
        self.client = app.test_client()

    def test_english_is_the_default_language(self):
        response = self.client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<html lang="en">', response.data)
        self.assertIn(b'window.NHRA_LANGUAGE = "en"', response.data)

    def test_burmese_choice_persists_in_the_session(self):
        response = self.client.post(
            '/language/my', data={'next': '/'}, follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<html lang="my">', response.data)
        self.assertIn(b'window.NHRA_LANGUAGE = "my"', response.data)
        self.assertIn('မြန်မာ'.encode('utf-8'), response.data)

        next_response = self.client.get('/')
        self.assertIn(b'<html lang="my">', next_response.data)

    def test_language_redirect_rejects_external_targets(self):
        response = self.client.post(
            '/language/en', data={'next': 'https://example.com/not-safe'}
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers['Location'], '/')

    def test_unsupported_language_is_not_accepted(self):
        response = self.client.post('/language/fr')

        self.assertEqual(response.status_code, 404)

    def test_in_place_language_switch_updates_session_without_redirect(self):
        response = self.client.post(
            '/language/my', headers={'X-Requested-With': 'language-switch'}
        )

        self.assertEqual(response.status_code, 204)
        with self.client.session_transaction() as browser_session:
            self.assertEqual(browser_session['language'], 'my')

    def test_form_contains_stage_and_draft_restoration_support(self):
        response = self.client.get('/')

        self.assertIn(b'nhra-assessment-draft-v1', response.data)
        self.assertIn(b'restoreAssessmentDraft()', response.data)
        self.assertIn(b'NHRA_SET_LANGUAGE', response.data)

    def test_dynamic_result_explanations_have_burmese_translation_patterns(self):
        script = Path('static/i18n.js').read_text(encoding='utf-8')

        self.assertIn('Graph interpretation: curves show fuzzy rule activation', script)
        self.assertIn('No heartbeat\\/breathing safety override', script)
        self.assertIn('A delivery complication was reported; review it', script)
        self.assertIn('Have the neonatal clinician reassess this component', script)
        self.assertIn('Reported family-history details', script)
        self.assertIn('Singleton births; gestation encoded as 20–45 completed weeks', script)
        self.assertIn('Actions come from recorded findings and project rules', script)
        self.assertIn('All important inputs were complete and valid', script)
        self.assertIn('Stable APGAR with complication', script)


if __name__ == '__main__':
    unittest.main()
