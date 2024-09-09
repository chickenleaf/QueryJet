from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from elasticsearch import Elasticsearch, exceptions as es_exceptions
from celery import Celery
import os
from tasks import create_index_if_not_exists

app = FastAPI()

# Initialize Elasticsearch client
es_host = os.getenv("ELASTICSEARCH_HOST", "localhost")
es_port = os.getenv("ELASTICSEARCH_PORT", "9200")

es_username = os.getenv("ELASTICSEARCH_USERNAME", "elastic")
es_password = os.getenv("ELASTICSEARCH_PASSWORD", "password")

# Construct Elasticsearch URL
es_url = f"http://{es_host}:{es_port}"

# Initialize Elasticsearch client
if es_username and es_password:
    es = Elasticsearch([es_url], http_auth=(es_username, es_password))
else:
    es = Elasticsearch([es_url])


# Initialize Celery with result backend
celery_app = Celery('tasks',
                    broker=os.getenv("RABBITMQ_URL", "amqp://localhost"),
                    backend='rpc://', broker_connection_retry_on_startup=True)

class BlogPost(BaseModel):
    blog_title: str
    blog_text: str
    user_id: str


@app.post("/submit_blog")
async def submit_blog(blog_post: BlogPost):
    """
    Submit a blog post for indexing. The blog post is sent to a Celery task queue.

    Args:
        blog_post (BlogPost): The blog post data to be indexed.

    Returns:
        dict: Confirmation message and task ID.
    """
    create_index_if_not_exists()
    task = celery_app.send_task('tasks.index_blog_post', args=[blog_post.model_dump()])
    return {"message": "Blog post submitted successfully", "task_id": task.id}

@app.get("/task_status/{task_id}")
async def get_task_status(task_id: str):
    """
    Check the status of a Celery task.

    Args:
        task_id (str): The ID of the task to check.

    Returns:
        dict: Task status and result if completed.
    """
    task_result = celery_app.AsyncResult(task_id)
    if task_result.ready():
        return {"status": "completed", "result": task_result.result}
    else:
        return {"status": "pending"}

@app.get("/search")
async def search_blogs(query: str):
    """
    Search for blogs in Elasticsearch using a query string.

    Args:
        query (str): The search query.

    Returns:
        dict: Search results containing blog information.
    """
    create_index_if_not_exists()
    body = {
        "query": {
            "multi_match": {
                "query": query,
                "fields": ["blog_title", "blog_text"]
            }
        }
    }
    result = es.search(index="blog_posts", body=body)
    hits = result['hits']['hits']
    blogs = [{"id": hit["_id"], "title": hit["_source"]["blog_title"], 
              "text": hit["_source"]["blog_text"], "user_id": hit["_source"]["user_id"]} for hit in hits]
    return {"results": blogs}

@app.get("/health/elasticsearch")
async def elasticsearch_health():
    """
    Check the health of the Elasticsearch connection.

    Returns:
        dict: Status message indicating the connection status.
    """
    try:
        if es.ping():
            return {"status": "Elasticsearch is connected"}
        else:
            raise HTTPException(status_code=503, detail="Elasticsearch is not reachable")
    except es_exceptions.ConnectionError as e:
        raise HTTPException(status_code=503, detail="Elasticsearch is not reachable: " + str(e))

@app.get("/health/rabbitmq")
async def rabbitmq_health():
    """
    Check the health of the RabbitMQ connection.

    Returns:
        dict: Status message indicating the connection status.
    """
    try:
        celery_app.control.inspect().ping()
        return {"status": "RabbitMQ is connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail="RabbitMQ is not reachable")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

