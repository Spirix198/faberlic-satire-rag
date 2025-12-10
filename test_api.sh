#!/bin/bash

# ============================================================
# API Testing Script for Faberlic Satire RAG
# Tests all major endpoints with curl commands
# ============================================================

BASE_URL="http://localhost:8000"
API_KEY="test-api-key-12345"
JWT_TOKEN="your-jwt-token-here"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}========================================================${NC}"
echo -e "${YELLOW}Faberlic Satire RAG - API Test Suite${NC}"
echo -e "${YELLOW}========================================================${NC}\n"

# Test 1: Health Check
echo -e "${YELLOW}[TEST 1] Health Check${NC}"
echo "curl -s $BASE_URL/health | jq ."
echo -e "${GREEN}Response:${NC}"
curl -s "$BASE_URL/health" | jq . || echo "❌ Failed"
echo ""

# Test 2: List All Content (with pagination)
echo -e "${YELLOW}[TEST 2] List Content${NC}"
echo "curl -s \"$BASE_URL/api/content/list\" -H \"Authorization: Bearer $JWT_TOKEN\" | jq ."
echo -e "${GREEN}Response:${NC}"
curl -s "$BASE_URL/api/content/list" \
  -H "Authorization: Bearer $JWT_TOKEN" | jq . || echo "❌ Failed"
echo ""

# Test 3: Create Content
echo -e "${YELLOW}[TEST 3] Create Content${NC}"
echo "curl -X POST $BASE_URL/api/content \\""
echo "  -H 'Content-Type: application/json' \\"
echo "  -H 'Authorization: Bearer $JWT_TOKEN' \\"
echo "  -d '{...}'"
echo -e "${GREEN}Response:${NC}"
curl -s -X POST "$BASE_URL/api/content" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -d '{
    "title": "Test Article",
    "body": "This is a test article about RAG systems.",
    "metadata": {"category": "test", "author": "test-user"}
  }' | jq . || echo "❌ Failed"
echo ""

# Test 4: Generate Response (Perplexity)
echo -e "${YELLOW}[TEST 4] Generate Response (Requires Perplexity Key)${NC}"
echo "curl -X POST $BASE_URL/api/generate \\""
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{...}'"
echo -e "${GREEN}Response:${NC}"
curl -s -X POST "$BASE_URL/api/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Explain what RAG systems are",
    "max_tokens": 500
  }' | jq . || echo "❌ Failed"
echo ""

# Test 5: Analyze Content
echo -e "${YELLOW}[TEST 5] Analyze Content${NC}"
echo "curl -X POST $BASE_URL/api/analyze \\""
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{...}'"
echo -e "${GREEN}Response:${NC}"
curl -s -X POST "$BASE_URL/api/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "The system analyzes content using Perplexity AI",
    "analysis_type": "sentiment"
  }' | jq . || echo "❌ Failed"
echo ""

# Test 6: Get Swagger UI
echo -e "${YELLOW}[TEST 6] OpenAPI/Swagger Documentation${NC}"
echo "curl -s $BASE_URL/docs | head -n 20"
echo -e "${GREEN}Checking if Swagger UI is available at: $BASE_URL/docs${NC}"
curl -s -I "$BASE_URL/docs" | head -n 1 || echo "❌ Failed"
echo -e "✅ Visit ${GREEN}$BASE_URL/docs${NC} in your browser to see interactive API docs\n"

# Test 7: Performance Test (Multiple Requests)
echo -e "${YELLOW}[TEST 7] Performance Test (10 concurrent requests)${NC}"
echo -e "${GREEN}Sending 10 health check requests...${NC}"
for i in {1..10}; do
  curl -s "$BASE_URL/health" > /dev/null &
  echo -n "."
done
wait
echo -e "\n✅ Performance test completed\n"

echo -e "${YELLOW}========================================================${NC}"
echo -e "${GREEN}✅ Test Suite Complete${NC}"
echo -e "${YELLOW}========================================================${NC}\n"
echo "For more information, visit: $BASE_URL/docs"
echo ""
