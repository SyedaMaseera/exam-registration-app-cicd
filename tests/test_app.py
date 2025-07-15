import unittest
from app import app

class FlaskAppTestCase(unittest.TestCase):

    def setUp(self):
        # Set up test client
        self.client = app.test_client()
        self.client.testing = True

    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Welcome", response.data)  # adjust based on your HTML content

    def test_login_page(self):
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Login", response.data)

    def test_register_page(self):
        response = self.client.get('/register')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Register", response.data)

if __name__ == '__main__':
    unittest.main()
