#!/usr/bin/env python3
"""
Simple script to re-deploy frontend files to S3 without changing API URLs
Useful when you've made frontend changes and just want to push them
"""

import boto3
import json
from pathlib import Path

def get_bucket_name(profile_name='msr-aws'):
    """Get S3 bucket name from CloudFormation stack"""
    try:
        session = boto3.Session(profile_name=profile_name)
        cf = session.client('cloudformation')
        response = cf.describe_stacks(StackName='CertificationHunterStack')
        
        if response['Stacks']:
            outputs = response['Stacks'][0].get('Outputs', [])
            for output in outputs:
                if output['OutputKey'] == 'AssetsBucketName':
                    return output['OutputValue']
        
        return None
    except Exception as e:
        print(f"Error getting bucket name: {e}")
        return None

def upload_frontend_to_s3(bucket_name, profile_name='msr-aws'):
    """Upload all frontend files to S3"""
    try:
        session = boto3.Session(profile_name=profile_name)
        s3 = session.client('s3')
        frontend_dir = Path('frontend')
        
        if not frontend_dir.exists():
            print("Frontend directory not found")
            return False
        
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
                elif file_path.suffix == '.ico':
                    content_type = 'image/x-icon'
                
                print(f"Uploading {s3_key}")
                
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
        
        return len(uploaded_files) > 0
        
    except Exception as e:
        print(f"Error uploading to S3: {e}")
        return False

def main():
    """Main function"""
    print("Re-deploying frontend files to S3...")
    
    # Get bucket name
    bucket_name = get_bucket_name()
    if not bucket_name:
        print("Could not find S3 bucket name from CloudFormation stack")
        return 1
    
    print(f"Target bucket: {bucket_name}")
    
    # Upload files
    success = upload_frontend_to_s3(bucket_name)
    
    if success:
        print("Frontend re-deployment complete!")
        print("Changes should be visible in a few minutes")
        
        # Get website URL
        try:
            session = boto3.Session(profile_name='msr-aws')
            cf = session.client('cloudformation')
            response = cf.describe_stacks(StackName='CertificationHunterStack')
            if response['Stacks']:
                outputs = response['Stacks'][0].get('Outputs', [])
                for output in outputs:
                    if output['OutputKey'] == 'WebsiteURL':
                        print(f"Website: {output['OutputValue']}")
                        break
        except:
            pass
            
        return 0
    else:
        print("Frontend re-deployment failed")
        return 1

if __name__ == '__main__':
    import sys
    
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nDeployment cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)