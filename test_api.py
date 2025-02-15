import unittest
from app import app
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

    def test_health_check(self):
        # Test health endpoint
        response = self.app.get('/health')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], 'healthy')
        self.assertEqual(data['version'], '1.0.0')
        self.assertIsInstance(data['books_loaded'], int)

    def test_load_books_data(self):
        """Test the book loading function directly"""
        import app
        import os
        import tempfile
        import shutil
        from unittest.mock import patch, MagicMock
        
        # Save original state
        original_data_file = os.getenv('DATA_FILE', 'data/found_books_filtered.ndjson')
        original_books = app.books.copy()
        app.books.clear()  # Clear books for test
        
        test_dir = tempfile.mkdtemp()
        test_file = os.path.join(test_dir, 'test_books.ndjson')
        
        try:
            # Test missing file
            os.environ['DATA_FILE'] = test_file
            self.assertFalse(app.load_books_data())
            self.assertEqual(len(app.books), 0)
            
            # First verify our test data can be loaded
            test_book = ['metadata', {
                'name': 'Test Book',
                'author': 'Test Author',
                'language': 'English',
                'genre': 'Test',
                'publisher': 'Test Publisher',
                'release_date': '2024',
                'media_type': 'Book',
                'pages': '100',
                'isbn': '123456789'
            }]
            test_content = json.dumps(test_book) + '\n'
            
            # Write valid data and verify it loads
            with open(test_file, 'w') as f:
                f.write(test_content)
            
            # This should load successfully
            result = app.load_books_data()
            self.assertTrue(result)
            self.assertEqual(len(app.books), 1)
            self.assertEqual(app.books[0]['name'], 'Test Book')
            app.books.clear()
            
            # Now test LFS pointer and download
            with open(test_file, 'w') as f:
                f.write('version https://git-lfs.github.com/spec/v1\n')
                f.write('oid sha256:abc123\n')
            
            # Mock response will return same content
            mock_response = MagicMock()
            mock_response.raise_for_status = MagicMock()
            mock_response.iter_content = MagicMock(return_value=[test_content.encode('utf-8')])
            
            # Test LFS download
            with patch('requests.get', return_value=mock_response) as mock_get:
                result = app.load_books_data()
                mock_get.assert_called_once()
                
                # Verify the final result
                self.assertTrue(result)
                
                # Verify books were loaded
                self.assertTrue(result)
                self.assertEqual(len(app.books), 1)
                self.assertEqual(app.books[0]['name'], 'Test Book')
            
        finally:
            # Cleanup
            shutil.rmtree(test_dir)
            if original_data_file:
                os.environ['DATA_FILE'] = original_data_file
            else:
                del os.environ['DATA_FILE']
            # Restore original books
            app.books.clear()
            app.books.extend(original_books)

if __name__ == '__main__':
    unittest.main()