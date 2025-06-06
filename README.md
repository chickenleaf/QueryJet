# QueryJet

A FastAPI-based application that utilizes Celery for asynchronous task processing with rabbitMQ as broker and Elasticsearch for indexing and searching blog posts. The project includes Docker support for containerization and deployment.

## Features

- **FastAPI**: Enables fast and efficient API development with easy-to-use asynchronous features.
- **Celery**: Effectively manages background tasks and scales with system demands.
- **Elasticsearch**: Provides quick search and indexing capabilities for large data sets.
- **RabbitMQ**: Offers reliable message brokering and scalable task distribution.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Testing](#testing)
- [Docker](#docker)
- [API Endpoints](#api-endpoints)

## Installation

To set up and run the **QueryJet** project locally, follow these steps:

1. **Clone the Repository**

   ```bash
   git clone https://github.com/chickenleaf/QueryJet.git
   cd QueryJet
   ```

2. **Create and Activate a Virtual Environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Start the Application**

   Run the FastAPI application:

   ```bash
   uvicorn app.main:app --reload
   ```

2. **Start Celery Workers**

   Start Celery to process background tasks:

   ```bash
   celery -A celery_tasks.celery_app worker -P threads
   ```

3. **Access the Application**

   Open your web browser and navigate to `http://localhost:8000` to interact with the API.

## Testing

1. **Run Unit Tests**

   Execute the test cases using:

   ```bash
   python -m unittest tests.test_main
   ```

2. **Run Shell Script**

   Use the provided shell script for additional test tasks:

   ```bash
   bash tests/test.sh
   ```

## Docker

1. **Build the Docker Image**

   ```bash
   docker build -t queryjet .
   ```

2. **Run the Docker Container**

   ```bash
   docker-compose up
   ```

   This command will start the application and Celery workers in Docker containers.

## API Endpoints

- **Submit Blog Post**

  `POST /submit_blog`

  Submits a blog post for indexing. Requires a JSON body with `blog_title`, `blog_text`, and `user_id`.

  **Response:**

  ```json
  {
    "message": "Blog post submitted successfully",
    "task_id": "<task_id>"
  }
  ```

- **Check Task Status**

  `GET /task_status/{task_id}`

  Checks the status of a Celery task.

  **Response:**

  ```json
  {
    "status": "completed",
    "result": "<result>"
  }
  ```

- **Search Blogs**

  `GET /search?query=<query>`

  Searches for blogs in Elasticsearch based on the provided query string.

  **Response:**

  ```json
  {
    "results": [
      {
        "id": "<id>",
        "title": "<blog_title>",
        "text": "<blog_text>",
        "user_id": "<user_id>"
      }
    ]
  }
  ```

- **Check Elasticsearch Health**

  `GET /health/elasticsearch`

  Checks the health of the Elasticsearch connection.

  **Response:**

  ```json
  {
    "status": "Elasticsearch is connected"
  }
  ```

- **Check RabbitMQ Health**

  `GET /health/rabbitmq`

  Checks the health of the RabbitMQ connection used by Celery.

  **Response:**

  ```json
  {
    "status": "RabbitMQ is connected"
  }
  ```


