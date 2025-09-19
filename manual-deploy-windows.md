# Manual Deployment Steps for Windows

## Step-by-Step CDK Deployment

### 1. Install Dependencies
```powershell
# Navigate to CDK directory
cd cdk

# Install Python dependencies
pip install -r requirements.txt

# Go back to root
cd ..
```

### 2. Install Lambda Dependencies
```powershell
# Install scraper dependencies
cd lambda/scraper
pip install -r requirements.txt -t .

# Install matcher dependencies
cd ../matcher
pip install -r requirements.txt -t .

# Go back to root
cd ../..
```

### 3. Bootstrap CDK (if not done already)
```powershell
cd cdk
cdk bootstrap aws://xxxxxxxxxxxx/us-east-1
```

### 4. Deploy Both Stacks
```powershell
# Deploy all stacks at once
cdk deploy --all --require-approval never

# OR deploy individually
cdk deploy CertificationHunterStack --require-approval never
cdk deploy CertificationHunterAgentStack --require-approval never
```

### 5. Update Frontend
```powershell
# Go back to root directory
cd ..

# Update frontend with API URLs
python update-frontend.py
```

### 6. Test Deployment
```powershell
# Test the deployed functions
python test-scraper.py
```

## Using AWS Profile

If you have multiple AWS profiles, specify the profile:

```powershell
# Set AWS profile for this session
$env:AWS_PROFILE = "your-profile-name"

# Or use --profile flag with each command
cdk deploy --all --require-approval never --profile your-profile-name
aws sts get-caller-identity --profile your-profile-name
```

## Troubleshooting

### If CDK Deploy Fails:
```powershell
# Check CDK version
cdk --version

# Check AWS credentials
aws sts get-caller-identity

# Check existing stacks
aws cloudformation list-stacks --stack-status-filter CREATE_COMPLETE UPDATE_COMPLETE

# If stack exists and failed, delete it first
cdk destroy CertificationHunterStack
cdk destroy CertificationHunterAgentStack
```

### If Lambda Dependencies Fail:
```powershell
# Clean and reinstall
cd lambda/scraper
Remove-Item -Recurse -Force boto3*, botocore*, requests*, bs4* -ErrorAction SilentlyContinue
pip install -r requirements.txt -t .

cd ../matcher
Remove-Item -Recurse -Force boto3*, botocore* -ErrorAction SilentlyContinue
pip install -r requirements.txt -t .
```