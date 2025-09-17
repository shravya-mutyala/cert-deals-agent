#!/bin/bash

echo "🚀 Deploying Certification Coupon Hunter..."

# Install CDK dependencies
echo "Installing CDK dependencies..."
cd cdk
pip install -r requirements.txt

# Install Lambda dependencies
echo "Installing Lambda dependencies..."
cd ../lambda/scraper
pip install -r requirements.txt -t .
cd ../matcher  
pip install -r requirements.txt -t .
cd ../..

# Bootstrap CDK (run once per account/region)
echo "Bootstrapping CDK..."
cdk bootstrap

# Deploy the stack
echo "Deploying stack..."
cd cdk
cdk deploy --require-approval never

echo "✅ Deployment complete!"
echo "📝 Next steps:"
echo "1. Update frontend/index.html with your API Gateway URL"
echo "2. Upload frontend to S3 bucket for hosting"
echo "3. Test the scraper Lambda function"
echo "4. Configure EventBridge schedule"