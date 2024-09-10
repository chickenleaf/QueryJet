from fastapi import FastAPI
from submit_blog.submit import router as submit_router
from search_blog.search import router as search_router

app = FastAPI()

app.include_router(submit_router)
app.include_router(search_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)