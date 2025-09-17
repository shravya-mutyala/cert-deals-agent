#!/usr/bin/env python3
"""
Test script to manually trigger the scraper function
"""

import boto3
import json

def test_scraper():
    """Test the scraper Lambda function"""
    
    lambda_client = boto3.client('lambda')
    
    try:
        # Invoke the scraper function
        response = lambda_client.invoke(
            FunctionName='CertificationHunterStack-ScraperFunction',
            InvocationType='RequestResponse',
            Payload=json.dumps({})
        )
        
        # Parse response
        payload = json.loads(response['Payload'].read())
        print("✅ Scraper test successful!")
        print(f"Response: {json.dumps(payload, indent=2)}")
        
    except Exception as e:
        print(f"❌ Scraper test failed: {str(e)}")

def test_matcher():
    """Test the matcher function with sample data"""
    
    lambda_client = boto3.client('lambda')
    
    # Sample API Gateway event
    test_event = {
        'httpMethod': 'POST',
        'path': '/users',
        'body': json.dumps({
            'user_id': 'test-user-123',
            'location': 'United States',
            'student_status': True,
            'target_certifications': ['AWS Solutions Architect', 'Salesforce Admin'],
            'preferred_providers': ['AWS', 'Salesforce']
        })
    }
    
    try:
        response = lambda_client.invoke(
            FunctionName='CertificationHunterStack-MatcherFunction',
            InvocationType='RequestResponse',
            Payload=json.dumps(test_event)
        )
        
        payload = json.loads(response['Payload'].read())
        print("✅ Matcher test successful!")
        print(f"Response: {json.dumps(payload, indent=2)}")
        
    except Exception as e:
        print(f"❌ Matcher test failed: {str(e)}")

if __name__ == "__main__":
    print("🧪 Testing Certification Coupon Hunter functions...")
    print("\n1. Testing Scraper Function:")
    test_scraper()
    
    print("\n2. Testing Matcher Function:")
    test_matcher()
    
    print("\n✨ Testing complete!")