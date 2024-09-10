#!/bin/bash

# Base URLs
SUBMIT_URL="http://localhost:8000"
SEARCH_URL="http://localhost:8001"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}PASS${NC}: $2"
    else
        echo -e "${RED}FAIL${NC}: $2"
    fi
}

# Function to check if a service is running
check_service() {
    if curl -s "$1" > /dev/null; then
        echo -e "${GREEN}Service at $1 is up${NC}"
    else
        echo -e "${RED}Service at $1 is down${NC}"
        exit 1
    fi
}

# Function to display response
show_response() {
    echo -e "${BLUE}Response:${NC}\n$1\n"
}

# Check if services are running
echo "Checking if services are running..."
check_service "$SUBMIT_URL"
check_service "$SEARCH_URL"

# Test submit_blog endpoint
echo -e "\nTesting submit_blog endpoint..."
SUBMIT_RESPONSE=$(curl -s -X POST "${SUBMIT_URL}/submit_blog" \
     -H "Content-Type: application/json" \
     -d '{"blog_title":"Test Blog","blog_text":"This is a test blog post.","user_id":"test_user"}')
show_response "$SUBMIT_RESPONSE"
TASK_ID=$(echo "$SUBMIT_RESPONSE" | jq -r '.task_id')
if [ -z "$TASK_ID" ] || [ "$TASK_ID" == "null" ]; then
    print_result 1 "Submit blog (Failed to get task_id)"
else
    print_result 0 "Submit blog (task_id: $TASK_ID)"
fi

# Test task_status endpoint
echo -e "\nTesting task_status endpoint..."
TASK_STATUS=$(curl -s "${SUBMIT_URL}/task_status/${TASK_ID}")
show_response "$TASK_STATUS"
if [ -z "$TASK_STATUS" ]; then
    print_result 1 "Check task status (No response)"
else
    print_result 0 "Check task status"
fi

# Test search endpoint
echo -e "\nTesting search endpoint..."
SEARCH_RESPONSE=$(curl -s "${SEARCH_URL}/search?query=test")
show_response "$SEARCH_RESPONSE"
if [ -z "$SEARCH_RESPONSE" ]; then
    print_result 1 "Search blogs (No response)"
else
    print_result 0 "Search blogs"
fi

# Test Elasticsearch health endpoint
echo -e "\nTesting Elasticsearch health endpoint..."
ES_HEALTH=$(curl -s "${SEARCH_URL}/health/elasticsearch")
show_response "$ES_HEALTH"
if [ -z "$ES_HEALTH" ]; then
    print_result 1 "Elasticsearch health check (No response)"
else
    print_result 0 "Elasticsearch health check"
fi

# Test RabbitMQ health endpoint
echo -e "\nTesting RabbitMQ health endpoint..."
RABBITMQ_HEALTH=$(curl -s "${SUBMIT_URL}/health/rabbitmq")
show_response "$RABBITMQ_HEALTH"
if [ -z "$RABBITMQ_HEALTH" ]; then
    print_result 1 "RabbitMQ health check (No response)"
else
    print_result 0 "RabbitMQ health check"
fi

echo -e "\nAll tests completed."


# #!/bin/bash

# # Base URLs
# SUBMIT_URL="http://localhost:8000"
# SEARCH_URL="http://localhost:8001"

# # Colors for output
# GREEN='\033[0;32m'
# RED='\033[0;31m'
# NC='\033[0m' # No Color

# # Function to print colored output
# print_result() {
#     if [ $1 -eq 0 ]; then
#         echo -e "${GREEN}PASS${NC}: $2"
#     else
#         echo -e "${RED}FAIL${NC}: $2"
#     fi
# }

# # Test submit_blog endpoint
# echo "Testing submit_blog endpoint..."
# SUBMIT_RESPONSE=$(curl -s -X POST ${SUBMIT_URL}/submit_blog \
#      -H "Content-Type: application/json" \
#      -d '{"blog_title":"Test Blog","blog_text":"This is a test blog post.","user_id":"test_user"}')
# TASK_ID=$(echo $SUBMIT_RESPONSE | jq -r '.task_id')
# print_result $? "Submit blog"

# # Test task_status endpoint
# echo "Testing task_status endpoint..."
# curl -s ${SUBMIT_URL}/task_status/${TASK_ID} > /dev/null
# print_result $? "Check task status"

# # Test search endpoint
# echo "Testing search endpoint..."
# curl -s "${SEARCH_URL}/search?query=test" > /dev/null
# print_result $? "Search blogs"

# # Test Elasticsearch health endpoint
# echo "Testing Elasticsearch health endpoint..."
# curl -s ${SEARCH_URL}/health/elasticsearch > /dev/null
# print_result $? "Elasticsearch health check"

# # Test RabbitMQ health endpoint
# echo "Testing RabbitMQ health endpoint..."
# curl -s ${SUBMIT_URL}/health/rabbitmq > /dev/null
# print_result $? "RabbitMQ health check"

# echo "All tests completed."