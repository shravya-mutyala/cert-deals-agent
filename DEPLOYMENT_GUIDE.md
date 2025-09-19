# 🚀 Complete Deployment Guide

## Prerequisites

### 1. AWS Account Setup
- **Account ID**: YOUR_AWS_ACCOUNT_ID
- **Region**: us-east-1 (recommended)
- **IAM User/Role**: Admin permissions required

### 2. Required Tools
```bash
# Check if you have these installed:
python --version    # Python 3.8+
aws --version      # AWS CLI v2
cdk --version      # AWS CDK v2
node --version     # Node.js 16+
```

### 3. Install Missing Tools
```bash
# AWS CLI
pip install awscli

# CDK
npm install -g aws-cdk

# Python dependencies
pip install boto3 requests beautifulsoup4
```

## Step-by-Step Deployment

### Step 1: Configure AWS Credentials
```bash
# Configure AWS CLI with your credentials
aws configure

# Enter your:
# - AWS Access Key ID
# - AWS Secret Access Key
# - Default region: us-east-1
# - Default output format: json

# Verify configuration
aws sts get-caller-identity
```

### Step 2: Enable Bedrock Model Access
1. Go to **AWS Console** → **Amazon Bedrock**
2. Click **Model access** in left sidebar
3. Click **Request model access**
4. Enable **Anthropic Claude 3 Sonnet**
5. Submit request (usually approved instantly)

### Step 3: Clone and Setup Project
```bash
# If you haven't already cloned your repo
git clone <your-repo-url>
cd cert-deals-agent

# Copy and configure environment file
cp .env.example .env
# Edit .env file and replace YOUR_AWS_ACCOUNT_ID with your actual AWS account ID

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate        # Linux/Mac
# OR
venv\Scripts\activate.bat       # Windows

# Install dependencies
pip install --upgrade pip
```

### Step 4: Run Pre-Deployment Checks
```bash
# This will check everything is ready
python pre-deploy-check.py
```

### Step 5: Deploy to AWS
```bash
# Option 1: Use the automated script
chmod +x deploy.sh
./deploy.sh

# Option 2: Use Makefile
make setup
source venv/bin/activate
make install
make deploy

# Option 3: Manual deployment
cd cdk
pip install -r requirements.txt
cdk bootstrap
cdk deploy --all --require-approval never
```

### Step 6: Verify Deployment
```bash
# Test the deployed functions
python test-scraper.py

# Check AWS Console
# - CloudFormation: Both stacks should be CREATE_COMPLETE
# - Lambda: Functions should be deployed
# - S3: Website should be accessible
# - Bedrock: Agent should be created
```

## Expected Outputs

After successful deployment, you'll see:

```
✅ Deployment complete!
📋 Deployment Summary:
   Stack Name: CertificationHunterStack
   Agent Stack Name: CertificationHunterAgentStack
   API Gateway URL: https://abc123.execute-api.us-east-1.amazonaws.com/prod/
   S3 Bucket: certificationhunterstack-assetsbucket12345-xyz
   Website URL: http://certificationhunterstack-assetsbucket12345-xyz.s3-website-us-east-1.amazonaws.com
   Bedrock Agent ID: ABCD1234
```

## Access Your Application

### 1. Main Web Interface
- **URL**: From deployment output (S3 website URL)
- **Features**: Traditional form-based interface

### 2. AI Agent Chat
- **URL**: `<website-url>/agent-chat.html`
- **Features**: Conversational AI interface

### 3. API Endpoints
- **Base URL**: From deployment output (API Gateway URL)
- **Endpoints**:
  - `POST /users` - Create user profile
  - `GET /offers?user_id=<id>` - Get matched offers

## Troubleshooting

### Common Issues

1. **"CDK not bootstrapped"**
   ```bash
   cdk bootstrap aws://YOUR_AWS_ACCOUNT_ID/us-east-1
   ```

2. **"Bedrock access denied"**
   - Go to AWS Console → Bedrock → Model access
   - Request access to Claude 3 Sonnet

3. **"Stack already exists"**
   ```bash
   # Delete existing stack if needed
   cdk destroy CertificationHunterStack
   cdk destroy CertificationHunterAgentStack
   ```

4. **"Lambda timeout"**
   - Check CloudWatch logs
   - Increase timeout in CDK if needed

5. **"Website not loading"**
   - Check S3 bucket policy
   - Verify website hosting is enabled

### Debug Commands

```bash
# Check stack status
aws cloudformation describe-stacks --stack-name CertificationHunterStack

# Check Lambda logs
aws logs tail /aws/lambda/CertificationHunterStack-ScraperFunction --follow

# Test API directly
curl -X POST <api-url>/users -d '{"user_id":"test","location":"US"}'
```

## Cost Estimation

### Monthly Costs (Estimated)
- **Lambda**: $1-5 (based on usage)
- **DynamoDB**: $1-3 (on-demand pricing)
- **API Gateway**: $1-2 (per million requests)
- **S3**: $0.50-1 (storage and requests)
- **Bedrock**: $3-10 (based on AI usage)

**Total**: ~$6-21/month for moderate usage

### Cost Optimization
- Use DynamoDB on-demand billing
- Enable S3 lifecycle policies
- Monitor Bedrock usage
- Set up billing alerts

## Security Best Practices

1. **IAM Roles**: Use least privilege principle
2. **API Keys**: Don't hardcode in frontend
3. **CORS**: Configure properly for your domain
4. **Encryption**: Enable at rest and in transit
5. **Monitoring**: Set up CloudWatch alarms

## Next Steps After Deployment

1. **Test thoroughly** with real certification searches
2. **Customize** the AI agent instructions for your use case
3. **Add monitoring** and alerting
4. **Set up CI/CD** for future updates
5. **Configure custom domain** if needed

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review AWS CloudWatch logs
3. Verify all prerequisites are met
4. Check AWS service limits and quotas

---

**Your Certification Coupon Hunter is now live on AWS!** 🎉