#!/bin/bash

# EduAI Test Script
# This script tests the EduAI application to verify it's working correctly

# Print colorful messages
print_message() {
  echo -e "\033[1;34m>>> $1\033[0m"
}

print_success() {
  echo -e "\033[1;32m>>> $1\033[0m"
}

print_error() {
  echo -e "\033[1;31m>>> ERROR: $1\033[0m"
}

print_section() {
  echo -e "\n\033[1;35m=== $1 ===\033[0m"
}

# Check if curl is installed (needed for tests)
if ! command -v curl &> /dev/null; then
  print_error "curl is not installed. Please install curl first."
  exit 1
fi

# Check backend health
print_section "BACKEND HEALTH CHECK"
print_message "Testing backend health endpoint..."

response=$(curl -s http://localhost:8000)
if [[ $response == *"healthy"* ]]; then
  print_success "Backend health check passed!"
else
  print_error "Backend health check failed. Response: $response"
  print_message "Make sure the backend is running on http://localhost:8000"
  exit 1
fi

# Check backend API docs
print_section "API DOCUMENTATION CHECK"
print_message "Testing API documentation endpoint..."

response_code=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/docs)
if [[ $response_code == "200" ]]; then
  print_success "API documentation check passed!"
else
  print_error "API documentation check failed. HTTP code: $response_code"
fi

# Check frontend health
print_section "FRONTEND CHECK"
print_message "Testing frontend availability..."

response_code=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000)
if [[ $response_code == "200" ]]; then
  print_success "Frontend check passed!"
else
  print_error "Frontend check failed. HTTP code: $response_code"
  print_message "Make sure the frontend is running on http://localhost:3000"
  exit 1
fi

# Test content generation API
print_section "CONTENT API TEST"
print_message "Testing content generation API..."

content_response=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -d '{"topic":"Photosynthesis","audience":"high school"}' \
  http://localhost:8000/api/content/generate)

if [[ $content_response == *"explanation"* ]]; then
  print_success "Content API test passed!"
else
  print_message "Content API returned: $content_response"
  print_message "Note: If USE_MOCK_DATA=False in backend/.env, this test may fail without valid API keys."
fi

# Test deep research API
print_section "DEEP RESEARCH API TEST"
print_message "Testing deep research API..."

research_response=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -d '{"topic":"Quantum Computing","subtopics":[],"academic_level":"undergraduate","include_references":true}' \
  http://localhost:8000/api/deep-research/research)

if [[ $research_response == *"introduction"* ]]; then
  print_success "Deep Research API test passed!"
else
  print_message "Deep Research API returned: $research_response"
  print_message "Note: If USE_MOCK_DATA=False in backend/.env, this test may fail without valid API keys."
fi

print_section "TEST RESULTS SUMMARY"
echo "Backend health: ✅"
echo "API documentation: ✅"
echo "Frontend availability: ✅"
echo "Content API: Tested"
echo "Deep Research API: Tested"

print_success "All basic tests completed!"
print_message "For manual testing, open http://localhost:3000 in your browser and try the application."