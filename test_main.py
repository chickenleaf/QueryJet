import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from main import app

class TestBlogAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    @patch('main.celery_app.send_task')
    def test_submit_blog(self, mock_send_task):
        mock_send_task.return_value = MagicMock(id='test_task_id')
        response = self.client.post(
            "/submit_blog",
            json={"blog_title": "Test Blog", "blog_text": "This is a test blog post", "user_id": "user1"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Blog post submitted successfully", "task_id": "test_task_id"})
        mock_send_task.assert_called_once_with('tasks.index_blog_post', args=[{'blog_title': 'Test Blog', 'blog_text': 'This is a test blog post', 'user_id': 'user1'}])

    @patch('main.es.search')
    def test_search_blogs(self, mock_es_search):
        mock_es_search.return_value = {
            'hits': {
                'hits': [
                    {'_id': 'test_id_1', '_source': {'blog_title': 'Test Blog 1', 'blog_text': 'This is test blog 1', 'user_id': 'user1'}},
                    {'_id': 'test_id_2', '_source': {'blog_title': 'Test Blog 2', 'blog_text': 'This is test blog 2', 'user_id': 'user2'}}
                ]
            }
        }
        response = self.client.get("/search?query=test")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"results": [
            {"id": "test_id_1", "title": "Test Blog 1", "text": "This is test blog 1", "user_id": "user1"},
            {"id": "test_id_2", "title": "Test Blog 2", "text": "This is test blog 2", "user_id": "user2"}
        ]})

if __name__ == '__main__':
    unittest.main()