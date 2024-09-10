from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from celery_tasks.tasks import create_index_if_not_exists
from celery_tasks.celery_app import celery_app

router = APIRouter()

class BlogPost(BaseModel):
    blog_title: str
    blog_text: str
    user_id: str

@router.post("/submit_blog")
async def submit_blog(blog_post: BlogPost):
    create_index_if_not_exists()
    task = celery_app.send_task('index_blog_post', args=[blog_post.model_dump()])
    return {"message": "Blog post submitted successfully", "task_id": task.id}

@router.get("/task_status/{task_id}")
async def get_task_status(task_id: str):
    task_result = celery_app.AsyncResult(task_id)
    if task_result.ready():
        return {"status": "completed", "result": task_result.result}
    else:
        return {"status": "pending"}

@router.get("/health/rabbitmq")
async def rabbitmq_health():
    try:
        celery_app.control.inspect().ping()
        return {"status": "RabbitMQ is connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail="RabbitMQ is not reachable")