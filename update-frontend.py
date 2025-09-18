#!/usr/bin/env python3
"""
Script to update frontend with API Gateway URL and upload to S3
"""

import boto3
import json
import sys
import os

def get_stack_outputs():
    """Get CloudFormation stack outputs"""
    cf = boto3.client('cloudformation')
    
    try:
        response = cf.describe_stacks(StackName='CertificationHunterStack')
        outputs = {}
        
        for output in response['Stacks'][0].get('Outputs', []):
            outputs[output['OutputKey']] = output['OutputValue']
        
        return outputs
    except Exception as e:
        print(f"Error getting stack outputs: {e}")
        return None

def update_and_upload_frontend(api_url, bucket_name):
    """Update frontend HTML with API URL and upload to S3"""
    
    try:
        # Read the original HTML file
        with open('frontend/index.html', 'r') as f:
            html_content = f.read()
        
        # Replace the placeholder with actual API URL
        updated_html = html_content.replace(
            "const API_BASE = 'YOUR_API_GATEWAY_URL';",
            f"const API_BASE = '{api_url}';"
        )
        
        # Write updated HTML to a temporary file
        with open('frontend/index_updated.html', 'w') as f:
            f.write(updated_html)
        
        # Upload to S3
        s3 = boto3.client('s3')
        
        # Upload updated HTML
        s3.upload_file(
            'frontend/index_updated.html',
            bucket_name,
            'index.html',
            ExtraArgs={'ContentType': 'text/html'}
        )
        
        # Clean up temp file
        os.remove('frontend/index_updated.html')
        
        print(f"Frontend updated and uploaded to S3")
        return True
        
    except Exception as e:
        print(f"Error updating frontend: {e}")
        return False

def main():
    """Main function"""
    
    print("Updating frontend with API Gateway URL...")
    
    # Get stack outputs
    outputs = get_stack_outputs()
    if not outputs:
        sys.exit(1)
    
    api_url = outputs.get('CertificationHunterAPIEndpoint')
    bucket_name = outputs.get('AssetsBucketName')
    website_url = outputs.get('WebsiteURL')
    
    if not api_url or not bucket_name:
        print("Could not find required stack outputs")
        sys.exit(1)
    
    print(f"API Gateway URL: {api_url}")
    print(f"S3 Bucket: {bucket_name}")
    
    # Update and upload frontend
    if update_and_upload_frontend(api_url, bucket_name):
        print(f"\nDeployment Complete!")
        print(f"Website URL: {website_url}")
        print(f"Your Certification Coupon Hunter is live!")
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()