# Certification Coupon Hunter - Setup Guide

## Prerequisites

1. **AWS Account** with appropriate permissions
2. **AWS CLI** configured with credentials
3. **Python 3.11+** installed
4. **Node.js** (for CDK)
5. **AWS CDK** installed globally: `npm install -g aws-cdk`

## Quick Start (Hackathon Mode)

### 1. Deploy Infrastructure

```bash
# Make deploy script executable
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

### 2. Configure Bedrock Access

```bash
# Enable Bedrock models in your AWS region
aws bedrock put-model-invocation-logging-configuration \
  --logging-config cloudWatchConfig='{logGroupName=/aws/bedrock/modelinvocations,roleArn=arn:aws:iam::ACCOUNT:role/service-role/AmazonBedrockExecutionRoleForKnowledgeBase_XXXXX}'
```

### 3. Test Functions

```bash
python test-scraper.py
```

### 4. Deploy Frontend

```bash
# Get your API Gateway URL from CDK output
aws cloudformation describe-stacks --stack-name CertificationHunterStack \
  --query 'Stacks[0].Outputs[?OutputKey==`CertificationHunterAPIEndpoint`].OutputValue' \
  --output text

# Update frontend/index.html with the API URL
# Upload to S3 bucket for hosting
aws s3 cp frontend/ s3://certification-hunter-assets/ --recursive
```

## Architecture Components

### Core Services
- **Amazon Bedrock**: Claude 3 Sonnet for offer parsing and matching
- **AWS Lambda**: Serverless functions for scraping and matching
- **DynamoDB**: NoSQL storage for offers and user profiles
- **API Gateway**: REST API endpoints
- **EventBridge**: Scheduled scraping (daily at 6 AM UTC)
- **S3**: Static website hosting

### Data Flow
1. EventBridge triggers scraper Lambda daily
2. Scraper fetches certification pages, uses Bedrock to parse offers
3. Structured offers stored in DynamoDB
4. Users create profiles via API
5. Matcher Lambda uses Bedrock to match offers to user profiles
6. Frontend displays personalized results

## Demo Strategy

### For Hackathon Judges

1. **Show Real Value**: Demo with actual AWS/Salesforce certification pages
2. **Highlight AI**: Show Bedrock parsing complex eligibility text
3. **Demonstrate Matching**: Create different user profiles, show different results
4. **Explain Autonomy**: Show EventBridge scheduling, no manual intervention needed

### Key Demo Points

- "This saves developers real money on expensive certifications"
- "AI understands complex eligibility rules automatically"
- "Autonomous discovery means you never miss a deal"
- "Personalized matching prevents information overload"

## Customization for More Providers

### Adding New Certification Providers

1. **Update scraper.py**: Add new source in `sources` array
2. **Create extraction function**: Follow pattern of `extract_aws_offers()`
3. **Test with sample pages**: Use `test-scraper.py`

### Example: Adding Microsoft Learn

```python
{
    'name': 'Microsoft Learn',
    'url': 'https://docs.microsoft.com/en-us/learn/certifications/',
    'provider': 'Microsoft'
}
```

## Scaling Considerations

### For Production
- Add CloudWatch monitoring and alarms
- Implement rate limiting for web scraping
- Add SES/SNS for email notifications
- Use CloudFront for global frontend distribution
- Add authentication (Cognito)
- Implement caching (ElastiCache)

### Cost Optimization
- Use DynamoDB on-demand billing
- Optimize Lambda memory allocation
- Implement intelligent scraping (only when pages change)

## Troubleshooting

### Common Issues

1. **Bedrock Access Denied**: Ensure your region supports Claude 3 Sonnet
2. **Lambda Timeout**: Increase timeout for scraper function
3. **DynamoDB Throttling**: Switch to provisioned capacity if needed
4. **CORS Issues**: Update API Gateway CORS settings

### Debug Commands

```bash
# Check Lambda logs
aws logs tail /aws/lambda/CertificationHunterStack-ScraperFunction --follow

# Test DynamoDB access
aws dynamodb scan --table-name certification-offers --max-items 5

# Check EventBridge rules
aws events list-rules --name-prefix CertificationHunter
```

## Next Steps for Full Implementation

1. **Enhanced AI Prompts**: Fine-tune Bedrock prompts for better accuracy
2. **More Data Sources**: Add RSS feeds, official APIs where available
3. **User Notifications**: Implement SES email alerts
4. **Calendar Integration**: Generate ICS files for exam deadlines
5. **Mobile App**: React Native or Flutter frontend
6. **Analytics**: Track which offers users actually use

## Security Best Practices

- Use IAM roles with minimal permissions
- Enable CloudTrail for audit logging
- Encrypt DynamoDB tables at rest
- Use HTTPS only for all endpoints
- Implement input validation and sanitization
- Regular security scanning of dependencies

---

**Ready to hunt some certification deals! 🎯**