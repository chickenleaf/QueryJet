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

# Submit a blog post and extract the task ID from the response
echo "Submitting a Blog Post..."
response=$(curl -s -X POST "$BASE_URL/submit_blog" \
     -H "Content-Type: application/json" \
     -d '{"blog_title": "My First Blog", "blog_text": "This is the content of my first blog post.", "user_id": "user12345"}')

echo "Response: $response"
task_id=$(echo $response | jq -r '.task_id')

if [ "$task_id" == "null" ] || [ -z "$task_id" ]; then
    echo "Failed to extract task ID."
    exit 1
fi
echo "Extracted Task ID: $task_id"
echo -e "\n"

# Check task status using the extracted task ID
echo "Checking Task Status for Task ID $task_id..."
curl -X GET "$BASE_URL/task_status/$task_id"
echo -e "\n"

# Search for blog posts
echo "Searching for Blog Posts containing 'First'..."
curl -X GET "$BASE_URL/search?query=First"
echo -e "\n"

