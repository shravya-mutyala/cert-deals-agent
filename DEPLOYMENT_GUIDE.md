# Quick Deployment Guide

## Prerequisites Check
Before deploying, ensure you have:

1. **AWS CLI** configured with profile `msr-aws`
2. **AWS CDK** installed (`npm install -g aws-cdk`)
3. **Python 3.11+** installed
4. **Bedrock access** enabled in your AWS account
5. **Claude 3.5 Sonnet** model access requested

## Quick Deploy

```bash
# Run the deployment script
python deploy_bedrock_agent.py
```

## Manual Deploy (if script fails)

```bash
# 1. Install CDK dependencies
cd cdk
pip install -r requirements.txt

# 2. Bootstrap CDK (first time only)
AWS_PROFILE=msr-aws cdk bootstrap

# 3. Deploy Bedrock Agent stack
AWS_PROFILE=msr-aws cdk deploy BedrockAgentStack --require-approval never

# 4. Deploy fallback stack
AWS_PROFILE=msr-aws cdk deploy CertificationHunterStack --require-approval never
```

## Post-Deployment

1. **Get API endpoints** from CloudFormation outputs
2. **Update frontend** with the new Bedrock API endpoint
3. **Test the system** with sample queries
4. **Configure fallback** by updating STRANDS_API_ENDPOINT

## Testing

```bash
# Test Bedrock Agent
curl -X POST https://your-bedrock-api.com/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Find AWS certification deals"}'
```

## Troubleshooting

- **Bedrock Access**: Check AWS console for Bedrock service availability
- **Model Access**: Request Claude 3.5 Sonnet access in Bedrock console
- **Permissions**: Verify IAM roles have required permissions
- **Profile**: Ensure `msr-aws` profile is configured correctly

## Clean Up

```bash
# Remove stacks
AWS_PROFILE=msr-aws cdk destroy BedrockAgentStack
AWS_PROFILE=msr-aws cdk destroy CertificationHunterStack
```