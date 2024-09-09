import unittest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app

# Initialize TestClient
client = TestClient(app)

class BlogAPITestCase(unittest.TestCase):

    @patch('app.main.Elasticsearch')  # Mock Elasticsearch class
    @patch('app.main.create_index_if_not_exists')  # Mock create_index_if_not_exists function
    @patch('app.main.celery_app.send_task')  # Mock Celery task
    def test_submit_blog(self, mock_send_task, mock_create_index, mock_elasticsearch):
        # Arrange: Setup mock Elasticsearch client
        mock_es_instance = MagicMock()
        mock_elasticsearch.return_value = mock_es_instance

        # Arrange: Setup mock Celery task
        mock_send_task.return_value.id = "test_task_id"

        # Blog post data to be submitted
        blog_post_data = {
            "blog_title": "Test Blog",
            "blog_text": "This is a test blog post.",
            "user_id": "user_123"
        }

        # Act: Submit blog post
        response = client.post("/submit_blog", json=blog_post_data)

        # Assert: Check the response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "message": "Blog post submitted successfully",
            "task_id": "test_task_id"
        })

        # Ensure the Celery task was called with the correct arguments
        mock_send_task.assert_called_once_with('index_blog_post', args=[blog_post_data])

    @patch('app.main.Elasticsearch')  # Mock Elasticsearch class
    @patch('app.main.create_index_if_not_exists')  # Mock create_index_if_not_exists function
    @patch('app.main.es.search')  # Mock Elasticsearch search method
    def test_search_blogs(self, mock_search, mock_create_index, mock_elasticsearch):
        # Arrange: Setup mock Elasticsearch client
        mock_es_instance = MagicMock()
        mock_elasticsearch.return_value = mock_es_instance

        # Arrange: Setup mock search response
        mock_search.return_value = {
            "hits": {
                "hits": [
                    {
                        "_id": "1",
                        "_source": {
                            "blog_title": "Test Blog",
                            "blog_text": "This is a test blog post.",
                            "user_id": "user_123"
                        }
                    }
                ]
            }
        }

        # Arrange: Ensure the index creation function is also mocked
        mock_create_index.return_value = None

        # Act: Perform search
        response = client.get("/search", params={"query": "Test"})

        # Assert: Check the response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "results": [
                {
                    "id": "1",
                    "title": "Test Blog",
                    "text": "This is a test blog post.",
                    "user_id": "user_123"
                }
            ]
        })

        # Ensure the Elasticsearch search was called with the correct parameters
        mock_search.assert_called_once_with(
            index="blog_posts",
            body={
                "query": {
                    "multi_match": {
                        "query": "Test",
                        "fields": ["blog_title", "blog_text"]
                    }
                }
            }
        )

if __name__ == '__main__':
    unittest.main()

