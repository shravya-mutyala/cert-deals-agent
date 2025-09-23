#!/usr/bin/env python3
"""
Update frontend files with deployed API Gateway URL and re-upload to S3
"""

import boto3
import json
import os
import re
from pathlib import Path

def get_stack_outputs(stack_name, profile_name='msr-aws'):
    """Get CloudFormation stack outputs"""
    try:
        session = boto3.Session(profile_name=profile_name)
        cf = session.client('cloudformation')
        response = cf.describe_stacks(StackName=stack_name)
        
        outputs = {}
        if response['Stacks']:
            stack_outputs = response['Stacks'][0].get('Outputs', [])
            for output in stack_outputs:
                outputs[output['OutputKey']] = output['OutputValue']
        
        return outputs
    except Exception as e:
        print(f"Error getting stack outputs: {e}")
        return {}

def update_frontend_files(api_url):
    """Update frontend files with the correct API URL"""
    frontend_dir = Path('frontend')
    
    # Files to update
    files_to_update = [
        'index.html',
        'agent-chat.html'
    ]
    
    updated_files = []
    
    for filename in files_to_update:
        file_path = frontend_dir / filename
        
        if not file_path.exists():
            print(f"Warning: {file_path} not found, skipping...")
            continue
            
        print(f"Updating {file_path}...")
        
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Store original content for comparison
        original_content = content
        
        # Update API_BASE in index.html
        if filename == 'index.html':
            # Replace the hardcoded API_BASE URL
            content = re.sub(
                r"const API_BASE = '[^']*';",
                f"const API_BASE = '{api_url}strands';",
                content
            )
        
        # Update BEDROCK_AGENT_API in agent-chat.html  
        elif filename == 'agent-chat.html':
            # Replace the hardcoded BEDROCK_AGENT_API URL
            content = re.sub(
                r"const BEDROCK_AGENT_API = '[^']*';",
                f"const BEDROCK_AGENT_API = '{api_url}strands';",
                content
            )
        
        # Check if content was actually changed
        if content != original_content:
            # Write the updated content back
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            updated_files.append(str(file_path))
            print(f"✓ Updated {file_path}")
        else:
            print(f"- No changes needed for {file_path}")
    
    return updated_files

def upload_to_s3(bucket_name, profile_name='msr-aws'):
    """Upload frontend files to S3 bucket"""
    try:
        session = boto3.Session(profile_name=profile_name)
        s3 = session.client('s3')
        frontend_dir = Path('frontend')
        
        uploaded_files = []
        
        # Upload all files in frontend directory
        for file_path in frontend_dir.rglob('*'):
            if file_path.is_file():
                # Calculate relative path for S3 key
                s3_key = str(file_path.relative_to(frontend_dir)).replace('\\', '/')
                
                # Determine content type
                content_type = 'text/html'
                if file_path.suffix == '.css':
                    content_type = 'text/css'
                elif file_path.suffix == '.js':
                    content_type = 'application/javascript'
                elif file_path.suffix == '.png':
                    content_type = 'image/png'
                elif file_path.suffix == '.jpg' or file_path.suffix == '.jpeg':
                    content_type = 'image/jpeg'
                elif file_path.suffix == '.svg':
                    content_type = 'image/svg+xml'
                
                print(f"Uploading {file_path} to s3://{bucket_name}/{s3_key}")
                
                s3.upload_file(
                    str(file_path),
                    bucket_name,
                    s3_key,
                    ExtraArgs={
                        'ContentType': content_type,
                        'CacheControl': 'no-cache, no-store, must-revalidate'  # Force refresh
                    }
                )
                uploaded_files.append(s3_key)
        
        return uploaded_files
        
    except Exception as e:
        print(f"Error uploading to S3: {e}")
        return []

def invalidate_cloudfront(distribution_id=None, profile_name='msr-aws'):
    """Invalidate CloudFront cache if distribution exists"""
    try:
        if not distribution_id:
            print("No CloudFront distribution ID provided, skipping cache invalidation")
            return
            
        session = boto3.Session(profile_name=profile_name)
        cf = session.client('cloudfront')
        
        response = cf.create_invalidation(
            DistributionId=distribution_id,
            InvalidationBatch={
                'Paths': {
                    'Quantity': 1,
                    'Items': ['/*']
                },
                'CallerReference': str(int(time.time()))
            }
        )
        
        print(f"CloudFront invalidation created: {response['Invalidation']['Id']}")
        
    except Exception as e:
        print(f"CloudFront invalidation failed (this is OK if not using CloudFront): {e}")

def main():
    """Main function"""
    print("Updating frontend with deployed API Gateway URL...")
    
    # Get stack outputs
    stack_name = 'CertificationHunterStack'
    outputs = get_stack_outputs(stack_name)
    
    if not outputs:
        print(f"Could not get outputs from stack {stack_name}")
        return 1
    
    # Get required outputs
    api_url = outputs.get('CertificationHunterAPIEndpoint')
    bucket_name = outputs.get('AssetsBucketName')
    website_url = outputs.get('WebsiteURL')
    
    if not api_url:
        print("Could not find API Gateway endpoint in stack outputs")
        return 1
        
    if not bucket_name:
        print("Could not find S3 bucket name in stack outputs")
        return 1
    
    print(f"API Gateway URL: {api_url}")
    print(f"S3 Bucket: {bucket_name}")
    print(f"Website URL: {website_url}")
    
    # Update frontend files
    print("\nUpdating frontend files...")
    updated_files = update_frontend_files(api_url)
    
    if updated_files:
        print(f"✓ Updated {len(updated_files)} files:")
        for file in updated_files:
            print(f"  - {file}")
    else:
        print("No files needed updating")
    
    # Upload to S3
    print(f"\nUploading frontend to S3 bucket: {bucket_name}")
    uploaded_files = upload_to_s3(bucket_name)
    
    if uploaded_files:
        print(f"Uploaded {len(uploaded_files)} files to S3")
    else:
        print("Failed to upload files to S3")
        return 1
    
    # Invalidate CloudFront cache (if applicable)
    cloudfront_id = outputs.get('CloudFrontDistributionId')
    if cloudfront_id:
        print(f"\nInvalidating CloudFront cache...")
        invalidate_cloudfront(cloudfront_id)
    
    print(f"\nFrontend update complete!")
    print(f"Your website is available at: {website_url}")
    print(f"It may take a few minutes for changes to propagate")
    
    return 0

if __name__ == '__main__':
    import sys
    import time
    
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nUpdate cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)