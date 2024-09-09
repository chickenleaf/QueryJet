#!/bin/bash

# Base URL for testing
BASE_URL="http://localhost:8000"

# Health check for Elasticsearch
echo "Testing Elasticsearch Health Check..."
curl -X GET "$BASE_URL/health/elasticsearch"
echo -e "\n"

# Health check for RabbitMQ
echo "Testing RabbitMQ Health Check..."
curl -X GET "$BASE_URL/health/rabbitmq"
echo -e "\n"

# Submit a blog post
echo "Submitting a Blog Post..."
curl -X POST "$BASE_URL/submit_blog" \
     -H "Content-Type: application/json" \
     -d '{"blog_title": "My First Blog", "blog_text": "This is the content of my first blog post.", "user_id": "user12345"}'
echo -e "\n"

# Check task status (replace with a valid task_id from the previous step)
TASK_ID="replace_with_task_id_from_previous_step"
echo "Checking Task Status for Task ID $TASK_ID..."
curl -X GET "$BASE_URL/task_status/$TASK_ID"
echo -e "\n"

# Search for blog posts
echo "Searching for Blog Posts containing 'First'..."
curl -X GET "$BASE_URL/search?query=First"
echo -e "\n"
