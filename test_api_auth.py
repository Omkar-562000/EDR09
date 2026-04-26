#!/usr/bin/env python
"""Test backend API with authentication."""
import json
import urllib.request
import urllib.parse
import http.cookiejar

# Create a cookie jar to handle sessions
cookie_jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))

BASE_URL = "http://localhost:8000"

def make_request(method, endpoint, data=None):
    """Make an HTTP request and return parsed JSON."""
    url = f"{BASE_URL}{endpoint}"
    
    if data:
        json_data = json.dumps(data).encode('utf-8')
        req = urllib.request.Request(
            url,
            data=json_data,
            headers={"Content-Type": "application/json"},
            method=method
        )
    else:
        req = urllib.request.Request(url, method=method)
    
    try:
        response = opener.open(req)
        return json.loads(response.read())
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")
        return None

# Test signup
print("1. Signing up...")
result = make_request("POST", "/api/auth/signup", {
    "email": "test@example.com",
    "password": "password123"
})
print(f"   Result: {result}")

# Test login
print("\n2. Logging in...")
result = make_request("POST", "/api/auth/login", {
    "email": "test@example.com",
    "password": "password123"
})
print(f"   Result: {result}")

# Test get status
print("\n3. Getting status...")
result = make_request("GET", "/api/status")
if result:
    print(f"   Status: {json.dumps(result, indent=2)}")

# Test get events
print("\n4. Getting events...")
result = make_request("GET", "/api/events?limit=10")
if result:
    print(f"   Events count: {len(result)}")
    if result:
        print(f"   First event: {result[0]}")

# Test get detections
print("\n5. Getting detections...")
result = make_request("GET", "/api/detections?limit=10")
if result:
    print(f"   Detections count: {len(result)}")
    if result:
        print(f"   First detection: {result[0]}")
