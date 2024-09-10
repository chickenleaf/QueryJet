import unittest
import requests

class TestSearchBlog(unittest.TestCase):
    BASE_URL = "http://localhost:8001"

    def test_search_blogs(self):
        response = requests.get(f"{self.BASE_URL}/search?query=test")
        self.assertEqual(response.status_code, 200)
        self.assertIn("results", response.json())

    def test_elasticsearch_health(self):
        response = requests.get(f"{self.BASE_URL}/health/elasticsearch")
        self.assertEqual(response.status_code, 200)
        self.assertIn("status", response.json())

if __name__ == '__main__':
    unittest.main()