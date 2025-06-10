from fastapi import APIRouter, HTTPException
from elasticsearch import Elasticsearch, exceptions as es_exceptions
import os
from celery_tasks.tasks import create_index_if_not_exists

router = APIRouter()

# Initialize Elasticsearch client
es_host = os.getenv("ELASTICSEARCH_HOST", "localhost")
es_port = os.getenv("ELASTICSEARCH_PORT", "9200")
es_username = os.getenv("ELASTICSEARCH_USERNAME", "elastic")
es_password = os.getenv("ELASTICSEARCH_PASSWORD", "password")
es_url = f"http://{es_host}:{es_port}"

if es_username and es_password:
    es = Elasticsearch([es_url], http_auth=(es_username, es_password))
else:
    es = Elasticsearch([es_url])

@router.get("/search")
async def search_blogs(query: str):
    try:
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
        blogs = [{"id": hit["_id"],
                 "title": hit["_source"]["blog_title"],
                 "text": hit["_source"]["blog_text"],
                 "user_id": hit["_source"]["user_id"]}
                for hit in hits]
        return {"results": blogs}
    except Exception as e:
        raise HTTPException(status_code=500,
                          detail=f"Search error: {str(e)}")

@router.get("/health/elasticsearch")
async def elasticsearch_health():
    try:
        if es.ping():
            return {"status": "Elasticsearch is connected"}
        else:
            raise HTTPException(status_code=503, detail="Elasticsearch is not reachable")
    except es_exceptions.ConnectionError as e:
        raise HTTPException(status_code=503, detail="Elasticsearch is not reachable: " + str(e))