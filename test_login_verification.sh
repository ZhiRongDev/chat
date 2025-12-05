#!/bin/bash
# Test script to verify that unverified users cannot login

echo "Testing Login Verification Flow"
echo "================================"
echo ""

# Test 1: Register a new user
echo "1. Registering new user..."
REGISTER_RESPONSE=$(curl -s -X POST http://localhost:5000/api/v1/user/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test_unverified@example.com",
    "password": "testpassword123"
  }')
echo "Registration response: $REGISTER_RESPONSE"
echo ""

# Test 2: Try to login with unverified user (should fail with 403)
echo "2. Attempting to login with unverified user..."
LOGIN_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST http://localhost:5000/api/v1/user/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test_unverified@example.com",
    "password": "testpassword123"
  }')

HTTP_STATUS=$(echo "$LOGIN_RESPONSE" | grep "HTTP_STATUS:" | cut -d: -f2)
RESPONSE_BODY=$(echo "$LOGIN_RESPONSE" | sed '/HTTP_STATUS:/d')

echo "HTTP Status: $HTTP_STATUS"
echo "Response: $RESPONSE_BODY"
echo ""

# Verify result
if [ "$HTTP_STATUS" = "403" ]; then
    echo "✅ SUCCESS: Unverified user was blocked from logging in (HTTP 403)"
    echo "The system correctly prevents unverified users from accessing the application."
else
    echo "❌ FAILURE: Unverified user was able to login (HTTP $HTTP_STATUS)"
    echo "This is a security issue - unverified users should not be able to login!"
fi
echo ""
echo "Note: In production, the user would need to click the verification link in their email"
echo "to set is_verified=True before they can successfully login."
