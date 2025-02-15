import unittest
from api import app
import json

class TestAPI(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_get_all_books_pagination(self):
        # Test default pagination (page 1, limit 100)
        response = self.app.get('/all')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertLessEqual(len(data['books']), 100)
        self.assertEqual(data['page'], 1)
        self.assertEqual(data['limit'], 100)
        
        # Test custom pagination
        response = self.app.get('/all?page=2&limit=50')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertLessEqual(len(data['books']), 50)
        self.assertEqual(data['page'], 2)
        self.assertEqual(data['limit'], 50)

    def test_search_single_parameter(self):
        # Test search by name
        response = self.app.get('/search?name=harry')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        for book in data['books']:
            self.assertIn('harry', book['name'].lower())

    def test_search_multiple_parameters(self):
        # Test search with multiple parameters
        response = self.app.get('/search?author=j&language=english')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        for book in data['books']:
            self.assertIn('j', book['author'].lower())
            self.assertIn('english', book['language'].lower())

    def test_search_invalid_field(self):
        # Test search with invalid field
        response = self.app.get('/search?invalid_field=value')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', data)
        self.assertIn('Invalid field', data['error'])

    def test_search_no_parameters(self):
        # Test search with no parameters
        response = self.app.get('/search')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', data)
        self.assertIn('No search parameters', data['error'])

if __name__ == '__main__':
    unittest.main()