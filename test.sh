#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

echo "Starting Docker Compose services..."
docker-compose up --build -d

echo "Waiting for RabbitMQ to be healthy..."
docker-compose exec rabbitmq rabbitmqctl await_startup --timeout 60 || { echo "RabbitMQ failed to start in time!"; exit 1; }
echo "RabbitMQ is healthy."

echo "Waiting for Elasticsearch to be healthy..."
until curl -s -u elastic:password http://localhost:9200/_cluster/health | grep -q '"status":"green"\|"status":"yellow"'; do
  echo "Elasticsearch is not yet healthy. Waiting..."
  sleep 5
done
echo "Elasticsearch is healthy."

echo "Giving celery and api time to start up..."
sleep 15 # Give time for Python apps and Celery worker to fully initialize and connect

echo "--- Submitting Blog Posts ---"
# Submit blog post 1
echo "Submitting 'My First FastAPI Blog'..."
SUBMIT_RESPONSE_1=$(curl -s -X POST "http://localhost:8000/submit_blog" \
     -H "Content-Type: application/json" \
     -d '{"blog_title": "My First FastAPI Blog", "blog_text": "This is a test blog post for demonstration purposes.", "user_id": "user123"}')
echo "Response: $SUBMIT_RESPONSE_1"
TASK_ID_1=$(echo "$SUBMIT_RESPONSE_1" | grep -o '"task_id": "[^"]*"' | cut -d '"' -f 4)
echo "Task ID 1: $TASK_ID_1"

# Submit blog post 2
echo "Submitting 'Understanding Celery & RabbitMQ'..."
SUBMIT_RESPONSE_2=$(curl -s -X POST "http://localhost:8000/submit_blog" \
     -H "Content-Type: application/json" \
     -d '{"blog_title": "Understanding Celery & RabbitMQ", "blog_text": "Celery is a powerful distributed task queue. RabbitMQ is a robust message broker.", "user_id": "user456"}')
echo "Response: $SUBMIT_RESPONSE_2"
TASK_ID_2=$(echo "$SUBMIT_RESPONSE_2" | grep -o '"task_id": "[^"]*"' | cut -d '"' -f 4)
echo "Task ID 2: $TASK_ID_2"

# Submit blog post 3
echo "Submitting 'Elasticsearch for Fast Search'..."
SUBMIT_RESPONSE_3=$(curl -s -X POST "http://localhost:8000/submit_blog" \
     -H "Content-Type: application/json" \
     -d '{"blog_title": "Elasticsearch for Fast Search", "blog_text": "Elasticsearch allows full-text search and analytical queries.", "user_id": "user123"}')
echo "Response: $SUBMIT_RESPONSE_3"
TASK_ID_3=$(echo "$SUBMIT_RESPONSE_3" | grep -o '"task_id": "[^"]*"' | cut -d '"' -f 4)
echo "Task ID 3: $TASK_ID_3"


echo "--- Checking Task Status ---"
echo "Waiting for tasks to complete..."
sleep 5 # Give Celery worker some time to pick up tasks

STATUS="pending"
while [ "$STATUS" != "completed" ]; do
  echo "Checking status of Task ID 1: $TASK_ID_1"
  TASK_STATUS_1=$(curl -s "http://localhost:8000/task_status/$TASK_ID_1")
  echo "Status: $TASK_STATUS_1"
  STATUS=$(echo "$TASK_STATUS_1" | grep -o '"status": "[^"]*"' | cut -d '"' -f 4)
  if [ "$STATUS" != "completed" ]; then
    echo "Task 1 still pending. Waiting..."
    sleep 2
  fi
done
echo "Task 1 completed."

# You can add similar loops for Task ID 2 and 3 if desired, or just assume they will complete shortly after Task 1.
echo "Assuming other tasks also completed."


echo "--- Searching Blog Posts ---"
echo "Searching for 'FastAPI'..."
curl -s "http://localhost:8000/search?query=FastAPI" | json_pp # Use json_pp or jq for pretty print
echo ""

echo "Searching for 'Elasticsearch'..."
curl -s "http://localhost:8000/search?query=Elasticsearch" | json_pp
echo ""

echo "Searching for 'RabbitMQ'..."
curl -s "http://localhost:8000/search?query=RabbitMQ" | json_pp
echo ""

echo "Searching for 'test blog'..."
curl -s "http://localhost:8000/search?query=test%20blog" | json_pp # URL encode space
echo ""

echo "--- Health Checks ---"
echo "Checking Elasticsearch health..."
curl -s "http://localhost:8000/health/elasticsearch" | json_pp
echo ""

echo "Checking RabbitMQ health..."
curl -s "http://localhost:8000/health/rabbitmq" | json_pp
echo ""

echo "--- Demo Complete ---"

echo "Cleaning up Docker Compose services..."
docker-compose down

echo "Done."