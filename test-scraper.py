#!/usr/bin/env python3
"""
Test deployed AWS Lambda functions
"""

import boto3
import json
import sys

def get_function_names():
    """Get actual Lambda function names from CloudFormation"""
    try:
        cf = boto3.client('cloudformation')
        response = cf.describe_stack_resources(StackName='CertificationHunterStack')
        
        scraper_function = None
        matcher_function = None
        
        for resource in response['StackResources']:
            if resource['ResourceType'] == 'AWS::Lambda::Function':
                if 'Scraper' in resource['LogicalResourceId']:
                    scraper_function = resource['PhysicalResourceId']
                elif 'Matcher' in resource['LogicalResourceId']:
                    matcher_function = resource['PhysicalResourceId']
        
        return scraper_function, matcher_function
    except Exception as e:
        print(f"Could not get function names: {e}")
        return None, None

def test_scraper():
    """Test the scraper Lambda function"""
    
    scraper_function, _ = get_function_names()
    if not scraper_function:
        print("Could not find scraper function")
        return False
    
    lambda_client = boto3.client('lambda')
    
    try:
        print(f"Testing function: {scraper_function}")
        
        # Invoke the scraper function
        response = lambda_client.invoke(
            FunctionName=scraper_function,
            InvocationType='RequestResponse',
            Payload=json.dumps({})
        )
        
        # Parse response
        payload = json.loads(response['Payload'].read())
        
        if response['StatusCode'] == 200:
            print("Scraper test successful!")
            print(f"Response: {json.dumps(payload, indent=2)}")
            return True
        else:
            print(f"Scraper returned status {response['StatusCode']}")
            print(f"Response: {json.dumps(payload, indent=2)}")
            return False
        
    except Exception as e:
        print(f"Scraper test failed: {str(e)}")
        return False

def test_matcher():
    """Test the matcher function with sample data"""
    
    _, matcher_function = get_function_names()
    if not matcher_function:
        print("Could not find matcher function")
        return False
    
    lambda_client = boto3.client('lambda')
    
    # Sample API Gateway event for creating a user
    test_event = {
        'httpMethod': 'POST',
        'path': '/users',
        'body': json.dumps({
            'user_id': 'test-user-123',
            'location': 'United States',
            'student_status': True,
            'target_certifications': [
                'AWS Solutions Architect', 
                'Azure Administrator', 
                'Google Cloud Professional', 
                'Databricks Data Engineer'
            ],
            'preferred_providers': ['AWS', 'Microsoft', 'Google Cloud', 'Databricks', 'Salesforce']
        })
    }
    
    try:
        print(f"Testing function: {matcher_function}")
        
        # Test user creation
        response = lambda_client.invoke(
            FunctionName=matcher_function,
            InvocationType='RequestResponse',
            Payload=json.dumps(test_event)
        )
        
        payload = json.loads(response['Payload'].read())
        
        if response['StatusCode'] == 200:
            print("User creation test successful!")
            print(f"Response: {json.dumps(payload, indent=2)}")
            
            # Test getting offers for the user
            get_offers_event = {
                'httpMethod': 'GET',
                'path': '/offers',
                'queryStringParameters': {'user_id': 'test-user-123'}
            }
            
            response = lambda_client.invoke(
                FunctionName=matcher_function,
                InvocationType='RequestResponse',
                Payload=json.dumps(get_offers_event)
            )
            
            payload = json.loads(response['Payload'].read())
            print("Get offers test successful!")
            print(f"Response: {json.dumps(payload, indent=2)}")
            
            return True
        else:
            print(f"Matcher returned status {response['StatusCode']}")
            print(f"Response: {json.dumps(payload, indent=2)}")
            return False
        
    except Exception as e:
        print(f"Matcher test failed: {str(e)}")
        return False

def test_api_gateway():
    """Test API Gateway endpoints"""
    
    try:
        cf = boto3.client('cloudformation')
        response = cf.describe_stacks(StackName='CertificationHunterStack')
        
        api_url = None
        for output in response['Stacks'][0].get('Outputs', []):
            if output['OutputKey'] == 'CertificationHunterAPIEndpoint':
                api_url = output['OutputValue']
                break
        
        if api_url:
            print(f"API Gateway URL: {api_url}")
            print("Test the API manually:")
            print(f"   curl -X POST {api_url}/users -d '{{\"user_id\":\"test\",\"location\":\"US\"}}'")
            print(f"   curl {api_url}/offers?user_id=test")
            return True
        else:
            print("Could not find API Gateway URL")
            return False
            
    except Exception as e:
        print(f"API Gateway test failed: {e}")
        return False

def main():
    """Run all tests"""
    
    print("Testing Deployed Certification Coupon Hunter")
    print("=" * 60)
    
    # Check AWS credentials
    try:
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        print(f"AWS Account: {identity['Account']}")
        print(f"AWS User/Role: {identity['Arn']}")
    except Exception as e:
        print(f"AWS credentials issue: {e}")
        sys.exit(1)
    
    # Run tests
    tests_passed = 0
    total_tests = 3
    
    print("\n1. Testing Scraper Function:")
    if test_scraper():
        tests_passed += 1
    
    print("\n2. Testing Matcher Function:")
    if test_matcher():
        tests_passed += 1
    
    print("\n3. Testing API Gateway:")
    if test_api_gateway():
        tests_passed += 1
    
    # Summary
    print("\n" + "=" * 60)
    print(f"📊 Tests Results: {tests_passed}/{total_tests} passed")
    
    if tests_passed == total_tests:
        print("All tests passed! Your deployment is working correctly.")
        print("\nNext steps:")
        print("1. Update frontend/index.html with the API Gateway URL")
        print("2. Upload frontend to S3 bucket")
        print("3. Configure EventBridge schedule for automatic scraping")
    else:
        print("Some tests failed. Check the AWS Console for more details:")
        print("- CloudFormation: Check stack status")
        print("- Lambda: Check function logs")
        print("- IAM: Verify permissions")
    
    return tests_passed == total_tests

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nTesting interrupted")
        sys.exit(1)