from flask_testing import TestCase
from app import app

class MyTest(TestCase):

    def create_app(self):
        app.config['TESTING'] = True
        return app

    def test_example(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
   