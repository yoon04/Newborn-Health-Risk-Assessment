import unittest

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


if __name__ == '__main__':
    unittest.main()
