from app import app
import unittest

class FlaskappTests(unittest.TestCase):
    def setUp(self):
        # Creates a test client
        self.app = app.test_client()

        # Propagate the exceptions to the test client
        self.app.testing = True

    # Test listing the users
    def test_users_status_code(self):
        result = self.app.get('/api/v1/users')
        self.assertEqual(result.status_code, 200)
    
    # Test to add a new user
    def test_addusers_status_code(self):
        result = self.app.post('/api/v1/users', data='{"username": "cloud-test", "email":"none@none.com", "password": "cloud-native"}', content_type='application/json')
        print (result)
        self.assertEquals(result.status_code, 201)
    
    # Test to update an existing user
    def test_updusers_status_code(self):
        result = self.app.put('/api/v1/users/1', data='{"password": "cloud-native-test"}', content_type='application/json')
        self.assertEquals(result.status_code, 200)

    # Test to delete an existing user
    def test_delusers_status_code(self):
        result = self.app.delete('/api/v1/users', data='{"username": "cloud-test"}', content_type='application/json')
        self.assertEquals(result.status_code, 200)