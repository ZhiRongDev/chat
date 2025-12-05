#!/bin/bash
# Test the complete email verification flow

echo "Testing Email Verification Flow"
echo "================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

API_BASE="http://localhost:5000/api/v1"
TEST_EMAIL="test_verify_$(date +%s)@example.com"
TEST_PASSWORD="testpass123"

echo -e "${YELLOW}Step 1: Register a new user${NC}"
echo "Email: $TEST_EMAIL"
REGISTER_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST "$API_BASE/user/register" \
  -H "Content-Type: application/json" \
  -d "{
    \"username\": \"$TEST_EMAIL\",
    \"password\": \"$TEST_PASSWORD\"
  }")

HTTP_STATUS=$(echo "$REGISTER_RESPONSE" | grep "HTTP_STATUS:" | cut -d: -f2)
RESPONSE_BODY=$(echo "$REGISTER_RESPONSE" | sed '/HTTP_STATUS:/d')

if [ "$HTTP_STATUS" = "200" ]; then
    echo -e "${GREEN}✅ Registration successful${NC}"
    echo "Response: $RESPONSE_BODY"
else
    echo -e "${RED}❌ Registration failed (HTTP $HTTP_STATUS)${NC}"
    echo "Response: $RESPONSE_BODY"
    exit 1
fi
echo ""

echo -e "${YELLOW}Step 2: Try to login (should fail with 403)${NC}"
LOGIN_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST "$API_BASE/user/login" \
  -H "Content-Type: application/json" \
  -d "{
    \"username\": \"$TEST_EMAIL\",
    \"password\": \"$TEST_PASSWORD\"
  }")

HTTP_STATUS=$(echo "$LOGIN_RESPONSE" | grep "HTTP_STATUS:" | cut -d: -f2)
RESPONSE_BODY=$(echo "$LOGIN_RESPONSE" | sed '/HTTP_STATUS:/d')

if [ "$HTTP_STATUS" = "403" ]; then
    echo -e "${GREEN}✅ Login blocked for unverified user (HTTP 403)${NC}"
    echo "Response: $RESPONSE_BODY"
else
    echo -e "${RED}❌ ERROR: Unverified user was able to login (HTTP $HTTP_STATUS)${NC}"
    echo "Response: $RESPONSE_BODY"
    exit 1
fi
echo ""

echo -e "${YELLOW}Step 3: Generate verification token${NC}"
# In a real scenario, the user would get this token from their email
# For testing, we'll generate one manually using the same secret
VERIFICATION_TOKEN=$(python3 -c "
from app.auth import create_access_token, CreateAccessTokenPayload
from datetime import timedelta
token = create_access_token(
    CreateAccessTokenPayload(sub='$TEST_EMAIL', verify=True),
    expires_delta=timedelta(hours=24)
)
print(token)
" 2>/dev/null)

if [ -z "$VERIFICATION_TOKEN" ]; then
    echo -e "${RED}❌ Failed to generate verification token${NC}"
    echo -e "${YELLOW}Note: This requires the backend Python environment to be available${NC}"
    echo -e "${YELLOW}In production, the token is sent via email and users click the link${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Verification token generated${NC}"
echo "Token: ${VERIFICATION_TOKEN:0:50}..."
echo ""

echo -e "${YELLOW}Step 4: Verify email using the token${NC}"
VERIFY_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST "$API_BASE/user/verify-email" \
  -H "Content-Type: application/json" \
  -d "{
    \"token\": \"$VERIFICATION_TOKEN\"
  }")

HTTP_STATUS=$(echo "$VERIFY_RESPONSE" | grep "HTTP_STATUS:" | cut -d: -f2)
RESPONSE_BODY=$(echo "$VERIFY_RESPONSE" | sed '/HTTP_STATUS:/d')

if [ "$HTTP_STATUS" = "200" ]; then
    echo -e "${GREEN}✅ Email verification successful${NC}"
    echo "Response: $RESPONSE_BODY"
else
    echo -e "${RED}❌ Email verification failed (HTTP $HTTP_STATUS)${NC}"
    echo "Response: $RESPONSE_BODY"
    exit 1
fi
echo ""

echo -e "${YELLOW}Step 5: Try to login again (should succeed now)${NC}"
LOGIN_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST "$API_BASE/user/login" \
  -H "Content-Type: application/json" \
  -d "{
    \"username\": \"$TEST_EMAIL\",
    \"password\": \"$TEST_PASSWORD\"
  }")

HTTP_STATUS=$(echo "$LOGIN_RESPONSE" | grep "HTTP_STATUS:" | cut -d: -f2)
RESPONSE_BODY=$(echo "$LOGIN_RESPONSE" | sed '/HTTP_STATUS:/d')

if [ "$HTTP_STATUS" = "200" ]; then
    echo -e "${GREEN}✅ Login successful after verification${NC}"
    echo "Response: $RESPONSE_BODY"
else
    echo -e "${RED}❌ Login still failed (HTTP $HTTP_STATUS)${NC}"
    echo "Response: $RESPONSE_BODY"
    exit 1
fi
echo ""

echo "================================"
echo -e "${GREEN}✅ ALL TESTS PASSED!${NC}"
echo ""
echo "Summary:"
echo "1. ✅ User registered with is_verified=False"
echo "2. ✅ Login blocked for unverified user (403 Forbidden)"
echo "3. ✅ Verification token generated"
echo "4. ✅ Email verified successfully (is_verified=True)"
echo "5. ✅ Login succeeded after verification"
echo ""
echo "The email verification system is working correctly!"
