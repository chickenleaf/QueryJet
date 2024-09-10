import unittest
import requests

class TestSubmitBlog(unittest.TestCase):
    BASE_URL = "http://localhost:8000"

    def test_submit_blog(self):
        response = requests.post(f"{self.BASE_URL}/submit_blog", json={
            "blog_title": "Test Blog",
            "blog_text": "This is a test blog post.",
            "user_id": "test_user"
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("message", data)
        self.assertIn("task_id", data)

    def test_task_status(self):
        # First, submit a blog post to get a task_id
        submit_response = requests.post(f"{self.BASE_URL}/submit_blog", json={
            "blog_title": "Test Blog",
            "blog_text": "This is a test blog post.",
            "user_id": "test_user"
        })
        task_id = submit_response.json()["task_id"]

        # Now, check the task status
        response = requests.get(f"{self.BASE_URL}/task_status/{task_id}")
        self.assertEqual(response.status_code, 200)
        self.assertIn("status", response.json())

    def test_rabbitmq_health(self):
        response = requests.get(f"{self.BASE_URL}/health/rabbitmq")
        self.assertEqual(response.status_code, 200)
        self.assertIn("status", response.json())

if __name__ == '__main__':
    unittest.main()