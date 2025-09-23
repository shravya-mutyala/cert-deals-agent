#!/usr/bin/env python3
"""
Test the deployed API to make sure it's working
"""

import requests
import json

def test_api():
    """Test the API endpoint"""
    api_url = "https://ehvx4tl0lc.execute-api.us-east-1.amazonaws.com/prod/strands"
    
    print(f"🧪 Testing API endpoint: {api_url}")
    
    # Test payload
    test_payload = {
        "action": "discover_deals",
        "provider": "AWS",
        "certification_name": "AWS Cloud Practitioner",
        "student_status": False,
        "user_name": "Test User"
    }
    
    try:
        print("📤 Sending test request...")
        response = requests.post(
            api_url,
            headers={'Content-Type': 'application/json'},
            json=test_payload,
            timeout=30
        )
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API is working!")
            print(f"📋 Response: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ API returned error: {response.status_code}")
            print(f"📋 Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏰ Request timed out - API might be slow or not responding")
    except requests.exceptions.ConnectionError:
        print("🔌 Connection error - check if API Gateway is deployed")
    except Exception as e:
        print(f"❌ Error testing API: {e}")

if __name__ == '__main__':
    test_api()