#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default to localhost:3000 (Vercel dev default)
BASE_URL="${1:-http://localhost:3000}"

echo -e "${YELLOW}Testing GitLab MCP API at ${BASE_URL}${NC}"
echo ""

# Test 1: Index endpoint
echo -e "${GREEN}Test 1: GET /api/${NC}"
response=$(curl -s -w "\nHTTP_CODE:%{http_code}" "$BASE_URL/api/")
http_code=$(echo "$response" | grep "HTTP_CODE" | cut -d: -f2)
body=$(echo "$response" | sed '/HTTP_CODE/d')
if [ "$http_code" = "200" ]; then
    echo "$body" | jq '.' 2>/dev/null || echo "$body"
else
    echo -e "${RED}Failed with HTTP $http_code${NC}"
    echo "$body"
fi
echo ""

# Test 2: User endpoint
echo -e "${GREEN}Test 2: GET /api/user${NC}"
response=$(curl -s -w "\nHTTP_CODE:%{http_code}" "$BASE_URL/api/user")
http_code=$(echo "$response" | grep "HTTP_CODE" | cut -d: -f2)
body=$(echo "$response" | sed '/HTTP_CODE/d')
if [ "$http_code" = "200" ]; then
    echo "$body" | jq '.' 2>/dev/null || echo "$body"
else
    echo -e "${RED}Failed with HTTP $http_code${NC}"
    echo "$body"
fi
echo ""

# Test 3: Projects endpoint
echo -e "${GREEN}Test 3: GET /api/projects?owned=true&limit=3${NC}"
response=$(curl -s -w "\nHTTP_CODE:%{http_code}" "$BASE_URL/api/projects?owned=true&limit=3")
http_code=$(echo "$response" | grep "HTTP_CODE" | cut -d: -f2)
body=$(echo "$response" | sed '/HTTP_CODE/d')
if [ "$http_code" = "200" ]; then
    echo "$body" | jq '.' 2>/dev/null || echo "$body"
else
    echo -e "${RED}Failed with HTTP $http_code${NC}"
    echo "$body"
fi
echo ""

# Test 4: Groups endpoint
echo -e "${GREEN}Test 4: GET /api/groups?limit=3${NC}"
response=$(curl -s -w "\nHTTP_CODE:%{http_code}" "$BASE_URL/api/groups?limit=3")
http_code=$(echo "$response" | grep "HTTP_CODE" | cut -d: -f2)
body=$(echo "$response" | sed '/HTTP_CODE/d')
if [ "$http_code" = "200" ]; then
    echo "$body" | jq '.' 2>/dev/null || echo "$body"
else
    echo -e "${RED}Failed with HTTP $http_code${NC}"
    echo "$body"
fi
echo ""

echo -e "${YELLOW}Testing complete!${NC}"
echo ""
echo "Usage: ./test_api.sh [base_url]"
echo "Example: ./test_api.sh http://localhost:3000"
echo "Example: ./test_api.sh https://your-project.vercel.app"

