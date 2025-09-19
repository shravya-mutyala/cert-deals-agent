# PowerShell deployment script for Windows
Write-Host "Deploying Certification Coupon Hunter to AWS..." -ForegroundColor Green

# Load environment variables from .env file
if (Test-Path ".env") {
    Write-Host "Loading environment variables from .env..." -ForegroundColor Yellow
    Get-Content ".env" | ForEach-Object {
        if ($_ -match "^([^#][^=]+)=(.*)$") {
            [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
        }
    }
} else {
    Write-Host "Warning: .env file not found. Using system environment variables." -ForegroundColor Yellow
}

# Run pre-deployment checks
Write-Host "Running pre-deployment checks..." -ForegroundColor Yellow
python pre-deploy-check.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "Pre-deployment checks failed. Please fix the issues and try again." -ForegroundColor Red
    exit 1
}

Write-Host "Pre-deployment checks passed!" -ForegroundColor Green

# Check prerequisites
Write-Host "Checking prerequisites..." -ForegroundColor Yellow

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Python not found. Please install Python 3.8+" -ForegroundColor Red
    exit 1
}

# Check AWS CLI
try {
    $awsVersion = aws --version 2>&1
    Write-Host "AWS CLI: $awsVersion" -ForegroundColor Green
} catch {
    Write-Host "AWS CLI not found. Please install AWS CLI" -ForegroundColor Red
    exit 1
}

# Check CDK
try {
    $cdkVersion = cdk --version 2>&1
    Write-Host "CDK: $cdkVersion" -ForegroundColor Green
} catch {
    Write-Host "CDK not found. Please install: npm install -g aws-cdk" -ForegroundColor Red
    exit 1
}

# Check AWS credentials
Write-Host "Checking AWS credentials..." -ForegroundColor Yellow
try {
    $identity = aws sts get-caller-identity 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "AWS credentials configured" -ForegroundColor Green
    } else {
        Write-Host "AWS credentials not configured. Run: aws configure" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "AWS credentials issue" -ForegroundColor Red
    exit 1
}

# Install CDK dependencies
Write-Host "Installing CDK dependencies..." -ForegroundColor Yellow
Set-Location "cdk"
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to install CDK dependencies" -ForegroundColor Red
    exit 1
}

# Install Lambda dependencies
Write-Host "Installing Lambda dependencies..." -ForegroundColor Yellow
Set-Location "../lambda/scraper"
pip install -r requirements.txt -t .
Set-Location "../matcher"
pip install -r requirements.txt -t .
Set-Location "../.."

# Bootstrap CDK (if needed)
Write-Host "Bootstrapping CDK (if needed)..." -ForegroundColor Yellow
Set-Location "cdk"
cdk bootstrap aws://$env:AWS_ACCOUNT_ID/us-east-1
if ($LASTEXITCODE -ne 0) {
    Write-Host "CDK bootstrap failed" -ForegroundColor Red
    exit 1
}

# Deploy the stacks
Write-Host "Deploying stacks to AWS..." -ForegroundColor Yellow
cdk deploy --all --require-approval never
if ($LASTEXITCODE -ne 0) {
    Write-Host "CDK deployment failed" -ForegroundColor Red
    exit 1
}

# Update frontend with API URL and upload to S3
Write-Host "Updating frontend with API Gateway URL..." -ForegroundColor Yellow
Set-Location ".."
python update-frontend.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "Frontend update failed" -ForegroundColor Red
    exit 1
}

# Get final outputs
Write-Host "Getting deployment outputs..." -ForegroundColor Yellow
$apiUrl = aws cloudformation describe-stacks --stack-name CertificationHunterStack --query 'Stacks[0].Outputs[?OutputKey==`CertificationHunterAPIEndpoint`].OutputValue' --output text 2>$null
$bucketName = aws cloudformation describe-stacks --stack-name CertificationHunterStack --query 'Stacks[0].Outputs[?OutputKey==`AssetsBucketName`].OutputValue' --output text 2>$null
$websiteUrl = aws cloudformation describe-stacks --stack-name CertificationHunterStack --query 'Stacks[0].Outputs[?OutputKey==`WebsiteURL`].OutputValue' --output text 2>$null
$agentId = aws cloudformation describe-stacks --stack-name CertificationHunterAgentStack --query 'Stacks[0].Outputs[?OutputKey==`BedrockAgentId`].OutputValue' --output text 2>$null

Write-Host ""
Write-Host "Deployment complete!" -ForegroundColor Green
Write-Host "Deployment Summary:" -ForegroundColor Cyan
Write-Host "   Stack Name: CertificationHunterStack" -ForegroundColor White

if ($apiUrl) {
    Write-Host "   API Gateway URL: $apiUrl" -ForegroundColor White
}
if ($bucketName) {
    Write-Host "   S3 Bucket: $bucketName" -ForegroundColor White
}
if ($websiteUrl) {
    Write-Host "   Website URL: $websiteUrl" -ForegroundColor White
}
if ($agentId) {
    Write-Host "   Bedrock Agent ID: $agentId" -ForegroundColor White
}

Write-Host ""
Write-Host "Your Certification Coupon Hunter is now live!" -ForegroundColor Green
if ($websiteUrl) {
    Write-Host "Open your website: $websiteUrl" -ForegroundColor Cyan
}
Write-Host "Test the deployment: python test-scraper.py" -ForegroundColor Yellow
Write-Host ""
Write-Host "Ready for your hackathon demo!" -ForegroundColor Magenta