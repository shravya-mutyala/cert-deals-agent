#!/usr/bin/env python3
"""
Check what's actually deployed on the website
"""

import requests
import re

def check_website():
    """Check the deployed website"""
    website_url = "http://certificationhunterstack-assetsbucket5cb76180-2eykyyvbomlz.s3-website-us-east-1.amazonaws.com"
    
    print(f"🌐 Checking website: {website_url}")
    
    try:
        # Check index.html
        print("\n📄 Checking index.html...")
        response = requests.get(f"{website_url}/index.html", timeout=10)
        
        if response.status_code == 200:
            content = response.text
            
            # Look for API_BASE
            api_match = re.search(r"const API_BASE = '([^']+)';", content)
            if api_match:
                api_url = api_match.group(1)
                print(f"✅ Found API_BASE: {api_url}")
                
                # Check if it's the correct URL
                expected_url = "https://ehvx4tl0lc.execute-api.us-east-1.amazonaws.com/prod/strands"
                if api_url == expected_url:
                    print("✅ API URL is correct!")
                else:
                    print(f"❌ API URL mismatch!")
                    print(f"   Expected: {expected_url}")
                    print(f"   Found: {api_url}")
            else:
                print("❌ Could not find API_BASE in deployed file")
                
        else:
            print(f"❌ Could not fetch index.html: {response.status_code}")
            
        # Check agent-chat.html
        print("\n📄 Checking agent-chat.html...")
        response = requests.get(f"{website_url}/agent-chat.html", timeout=10)
        
        if response.status_code == 200:
            content = response.text
            
            # Look for BEDROCK_AGENT_API
            api_match = re.search(r"const BEDROCK_AGENT_API = '([^']+)';", content)
            if api_match:
                api_url = api_match.group(1)
                print(f"✅ Found BEDROCK_AGENT_API: {api_url}")
                
                # Check if it's the correct URL
                expected_url = "https://ehvx4tl0lc.execute-api.us-east-1.amazonaws.com/prod/strands"
                if api_url == expected_url:
                    print("✅ API URL is correct!")
                else:
                    print(f"❌ API URL mismatch!")
                    print(f"   Expected: {expected_url}")
                    print(f"   Found: {api_url}")
            else:
                print("❌ Could not find BEDROCK_AGENT_API in deployed file")
                
        else:
            print(f"❌ Could not fetch agent-chat.html: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error checking website: {e}")

def check_s3_direct():
    """Check S3 bucket directly"""
    print(f"\n🪣 Checking S3 bucket contents...")
    
    try:
        import boto3
        session = boto3.Session(profile_name='msr-aws')
        s3 = session.client('s3')
        
        bucket_name = "certificationhunterstack-assetsbucket5cb76180-2eykyyvbomlz"
        
        # List objects
        response = s3.list_objects_v2(Bucket=bucket_name)
        
        if 'Contents' in response:
            print("📁 Files in S3 bucket:")
            for obj in response['Contents']:
                print(f"   - {obj['Key']} (modified: {obj['LastModified']})")
        else:
            print("❌ No files found in S3 bucket")
            
    except Exception as e:
        print(f"❌ Error checking S3: {e}")

if __name__ == '__main__':
    check_website()
    check_s3_direct()