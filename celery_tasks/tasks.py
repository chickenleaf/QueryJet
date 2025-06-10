from .celery_app import celery_app
from elasticsearch import Elasticsearch
import os

# Initialize Elasticsearch client with retries and timeout
es_host = os.environ.get("ELASTICSEARCH_HOST", "localhost")
es_port = os.environ.get("ELASTICSEARCH_PORT", "9200")
es_url = f"http://{es_host}:{es_port}"
es_username = os.getenv("ELASTICSEARCH_USERNAME", "elastic")
es_password = os.getenv("ELASTICSEARCH_PASSWORD", "password")

es = Elasticsearch(
    [es_url],
    basic_auth=(es_username, es_password),
    retry_on_timeout=True,
    max_retries=3,
)

def create_index_if_not_exists():
    """Create the 'blog_posts' index with proper mappings"""
    try:
        if not es.indices.exists(index="blog_posts"):
            es.indices.create(index="blog_posts", body={
                "settings": {
                    "number_of_shards": 1,
                    "number_of_replicas": 0
                },
                "mappings": {
                    "properties": {
                        "blog_title": {"type": "text"},
                        "blog_text": {"type": "text"},
                        "user_id": {"type": "keyword"}
                    }
                }
            })
    except Exception as e:
        print(f"Error creating index: {e}")

@celery_app.task(name='index_blog_post')
def index_blog_post(blog_post):
    """
    Index a blog post in Elasticsearch.

    Args:
        blog_post (dict): The blog post data to index.

    Returns:
        str: Confirmation message with the ID of the indexed blog post.
    """
    # Ensure index exists
    create_index_if_not_exists()
    # Index the blog post in Elasticsearch
    result = es.index(index="blog_posts", body=blog_post)
    return f"Blog post processed and indexed with ID: {result['_id']}"
