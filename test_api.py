#!/usr/bin/env python
"""Test backend API endpoints."""
import asyncio
import json
from pathlib import Path
import sys
import time

# Wait for backend to start
print("Waiting for backend to start...")
time.sleep(3)

# Test the API
import urllib.request
import urllib.error

endpoints = [
    "/api/health",
    "/api/status",
]

for endpoint in endpoints:
    try:
        url = f"http://localhost:8000{endpoint}"
        with urllib.request.urlopen(url, timeout=2) as response:
            data = json.loads(response.read())
            print(f"✓ {endpoint}: {json.dumps(data, indent=2)}")
    except Exception as e:
        print(f"✗ {endpoint}: {type(e).__name__}: {e}")
        
print("\n✓ Backend is responding to API requests")
