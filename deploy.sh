#!/bin/bash

echo "Deploying Certification Coupon Hunter to AWS..."

# Load environment variables from .env file
if [ -f .env ]; then
    echo "Loading environment variables from .env..."
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "Warning: .env file not found. Using system environment variables."
fi

# Run pre-deployment checks
echo "Running pre-deployment checks..."
python pre-deploy-check.py
if [ $? -ne 0 ]; then
    echo "ERROR: Pre-deployment checks failed. Please fix the issues and try again."
    exit 1
fi

echo "SUCCESS: Pre-deployment checks passed!"

# Check prerequisites
echo "Checking prerequisites..."
if ! command -v aws &> /dev/null; then
    echo "ERROR: AWS CLI not found. Please install AWS CLI and configure credentials."
    exit 1
fi

if ! command -v cdk &> /dev/null; then
    echo "ERROR: CDK not found. Please install: npm install -g aws-cdk"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 not found. Please install Python 3.8+"
    exit 1
fi

# Check AWS credentials
echo "Checking AWS credentials..."
if ! aws sts get-caller-identity &> /dev/null; then
    echo "ERROR: AWS credentials not configured. Run: aws configure"
    exit 1
fi

echo "SUCCESS: Prerequisites check passed"

# Install CDK dependencies
echo "Installing CDK dependencies..."
cd cdk
pip install -r requirements.txt

# Install Lambda dependencies in their directories
echo "Installing Lambda dependencies..."
cd ../lambda/scraper
pip install -r requirements.txt -t .
cd ../matcher  
pip install -r requirements.txt -t .
cd ../..

# Bootstrap CDK (run once per account/region)
echo "Bootstrapping CDK (if needed)..."
cd cdk
cdk bootstrap

# Deploy the stack
echo "Deploying stack to AWS..."
cdk deploy --require-approval never

# Get outputs
echo "Getting deployment outputs..."
API_URL=$(aws cloudformation describe-stacks --stack-name CertificationHunterStack --query 'Stacks[0].Outputs[?OutputKey==`CertificationHunterAPIEndpoint`].OutputValue' --output text 2>/dev/null || echo "")
BUCKET_NAME=$(aws cloudformation describe-stacks --stack-name CertificationHunterStack --query 'Stacks[0].Outputs[?OutputKey==`AssetsBucketName`].OutputValue' --output text 2>/dev/null || echo "")

echo ""
# Update frontend with API URL and upload to S3
echo "Updating frontend with API Gateway URL..."
cd ..
python update-frontend.py

echo ""
echo "SUCCESS: Deployment complete!"
echo "INFO: Deployment Summary:"
echo "   Stack Name: CertificationHunterStack"

# Get final outputs
API_URL=$(aws cloudformation describe-stacks --stack-name CertificationHunterStack --query 'Stacks[0].Outputs[?OutputKey==`CertificationHunterAPIEndpoint`].OutputValue' --output text 2>/dev/null || echo "")
BUCKET_NAME=$(aws cloudformation describe-stacks --stack-name CertificationHunterStack --query 'Stacks[0].Outputs[?OutputKey==`AssetsBucketName`].OutputValue' --output text 2>/dev/null || echo "")
WEBSITE_URL=$(aws cloudformation describe-stacks --stack-name CertificationHunterStack --query 'Stacks[0].Outputs[?OutputKey==`WebsiteURL`].OutputValue' --output text 2>/dev/null || echo "")

if [ ! -z "$API_URL" ]; then
    echo "   API Gateway URL: $API_URL"
fi
if [ ! -z "$BUCKET_NAME" ]; then
    echo "   S3 Bucket: $BUCKET_NAME"
fi
if [ ! -z "$WEBSITE_URL" ]; then
    echo "   Website URL: $WEBSITE_URL"
fi

echo ""
echo "SUCCESS: Your Certification Coupon Hunter is now live!"
echo "INFO: Open your website: $WEBSITE_URL"
echo "INFO: Test the deployment: python test-scraper.py"
echo ""
echo "SUCCESS: Ready for your hackathon demo!"