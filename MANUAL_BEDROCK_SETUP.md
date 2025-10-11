# Manual Bedrock Agent Setup Guide

Since Bedrock Agent resources are not yet available in CloudFormation, you'll need to set up the Bedrock Agent manually through the AWS Console.

## 🎉 Deployment Status

✅ **Lambda Functions Deployed Successfully!**
- Web Discovery Tool: `arn:aws:lambda:us-east-1:829734435862:function:SimpleBedrockStack-WebDiscoveryTool18B9CED8-eQACJxbWXKIz`
- Career Planner Tool: `arn:aws:lambda:us-east-1:829734435862:function:SimpleBedrockStack-CareerPlannerToolCFE45591-IhOtikSTYAST`
- Learning Resources Tool: `arn:aws:lambda:us-east-1:829734435862:function:SimpleBedrockStack-LearningResourcesTool766D55B0-uhoED490w1Oi`
- Chat API Endpoint: `https://dxivqp5s1f.execute-api.us-east-1.amazonaws.com/prod/chat`

## Manual Bedrock Agent Setup

### Step 1: Create Bedrock Agent

1. Go to AWS Console → Amazon Bedrock → Agents
2. Click "Create Agent"
3. Configure:
   - **Agent name**: `certification-hunter-agent`
   - **Description**: `AI agent for certification deal hunting and career planning`
   - **Foundation model**: `Claude 3.5 Sonnet v2`
   - **Instructions**: Copy the instructions from below

### Agent Instructions
```
You are an expert Certification Deal Hunter and Career Advisor AI agent. Your mission is to help developers and IT professionals discover certification deals, challenges, and plan their career paths.

**Core Capabilities:**

1. **Certification Deal Discovery**: Find official certification deals, challenges, and promotions from AWS, Azure, Google Cloud, Databricks, and Salesforce. Focus on:
   - Official certification challenges (like AWS AI Practitioner Challenge)
   - Exam vouchers and discounts
   - Student and partner promotions
   - Time-limited offers and special events

2. **Career Path Planning**: Create personalized certification roadmaps based on:
   - Current role and target role
   - Experience level and preferred cloud provider
   - Industry trends and job market demands
   - Logical skill progression paths

3. **Learning Resource Guidance**: Provide curated learning resources for each cloud provider including official documentation, training platforms, and hands-on labs.

**Search Strategy for Deals:**
- Always search official provider websites and pages
- Look for certification challenges and promotional campaigns
- Focus on current year deals and upcoming opportunities
- Verify deal authenticity and eligibility requirements
- Prioritize official sources over third-party sites

**When asked about specific certifications:**
- Use web discovery to find current deals and challenges
- Provide career planning advice for certification paths
- Suggest relevant learning resources
- Give realistic timelines and next steps

**Response Style:**
- Be specific and actionable
- Provide direct links when available
- Explain eligibility requirements clearly
- Prioritize official and verified sources
- Always mention if deals have expiration dates or special requirements

Use your tools proactively to discover the most current and relevant information for users.
```

### Step 2: Add Action Groups (Tools)

**⚠️ IMPORTANT**: The schema files have been updated with required `operationId` fields for Claude 3.5 compatibility. Make sure to use the updated schema files!

You need to create **3 separate Action Groups** in the Bedrock Agent console. Each Action Group represents one tool/capability:

#### Action Group 1: Web Discovery Tool
1. In the Bedrock Agent console, click **"Add Action Group"**
2. Configure:
   - **Action Group Name**: `web_discovery`
   - **Description**: `Discover certification deals, challenges, and promotions from official provider websites`
   - **Action Group Type**: Select **"Define with function details"**
   - **Lambda Function**: `arn:aws:lambda:us-east-1:829734435862:function:SimpleBedrockStack-WebDiscoveryTool18B9CED8-eQACJxbWXKIz`
   - **API Schema**: Select **"Define with API schemas"** and paste the content from `web_discovery_schema.json`

#### Action Group 2: Career Planner Tool
1. Click **"Add Action Group"** again (this creates a second action group)
2. Configure:
   - **Action Group Name**: `career_planner`
   - **Description**: `Plan certification paths based on career goals`
   - **Action Group Type**: Select **"Define with function details"**
   - **Lambda Function**: `arn:aws:lambda:us-east-1:829734435862:function:SimpleBedrockStack-CareerPlannerToolCFE45591-IhOtikSTYAST`
   - **API Schema**: Select **"Define with API schemas"** and paste the content from `career_planner_schema.json`

#### Action Group 3: Learning Resources Tool
1. Click **"Add Action Group"** again (this creates a third action group)
2. Configure:
   - **Action Group Name**: `learning_resources`
   - **Description**: `Get learning resources for cloud providers`
   - **Action Group Type**: Select **"Define with function details"**
   - **Lambda Function**: `arn:aws:lambda:us-east-1:829734435862:function:SimpleBedrockStack-LearningResourcesTool766D55B0-uhoED490w1Oi`
   - **API Schema**: Select **"Define with API schemas"** and paste the content from `learning_resources_schema.json`

**Important**: Each Action Group is a separate tool that the agent can use. You should see all 3 Action Groups listed in your agent configuration when done.

### Visual Guide for Action Groups

```
Bedrock Agent: certification-hunter-agent
├── Action Group 1: web_discovery (→ WebDiscoveryTool Lambda)
├── Action Group 2: career_planner (→ CareerPlannerTool Lambda)  
└── Action Group 3: learning_resources (→ LearningResourcesTool Lambda)
```

### Step-by-Step Process:
1. **Create Agent** (Step 1)
2. **Add First Action Group** → Web Discovery
3. **Add Second Action Group** → Career Planner
4. **Add Third Action Group** → Learning Resources
5. **Create Alias** (Step 3)
6. **Update Lambda Environment Variables** (Step 4)

### Step 3: Create Agent Alias
1. After creating the agent, create an alias named `production`
2. Note the Agent ID and Alias ID

### Step 4: Update Chat Lambda Environment Variables
1. Go to AWS Console → Lambda → Functions
2. Find the chat function: `SimpleBedrockStack-ChatFunction3D7C447E-*`
3. Update environment variables:
   - `BEDROCK_AGENT_ID`: Your agent ID from Step 3
   - `BEDROCK_AGENT_ALIAS_ID`: Your alias ID from Step 3

## Testing

### Test the Chat API
```bash
curl -X POST https://dxivqp5s1f.execute-api.us-east-1.amazonaws.com/prod/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Find AWS certification deals"}'
```

### Test Individual Lambda Functions
```bash
# Test Web Discovery
aws lambda invoke --function-name SimpleBedrockStack-WebDiscoveryTool18B9CED8-eQACJxbWXKIz \
  --payload '{"parameters":[{"name":"providers","value":["AWS"]}]}' \
  response.json

# Test Career Planner
aws lambda invoke --function-name SimpleBedrockStack-CareerPlannerToolCFE45591-IhOtikSTYAST \
  --payload '{"parameters":[{"name":"current_role","value":"Developer"},{"name":"target_role","value":"Cloud Architect"}]}' \
  response.json
```

## Frontend

The frontend is already configured to use the new API endpoint:
- **Chat API**: `https://dxivqp5s1f.execute-api.us-east-1.amazonaws.com/prod/chat`
- **Fallback API**: `https://ehvx4tl0lc.execute-api.us-east-1.amazonaws.com/prod/strands`

## Next Steps

1. ✅ Lambda functions deployed
2. ⏳ Create Bedrock Agent manually (follow steps above)
3. ⏳ Update chat Lambda environment variables
4. ⏳ Test the complete system
5. ⏳ Deploy fallback stack if needed

## Troubleshooting

### Common Issues with Action Groups
- **"Function not found"**: Make sure you're using the exact Lambda ARN from the deployment output
- **"Permission denied"**: The Lambda functions already have the correct IAM roles, but you may need to add Bedrock invoke permissions
- **"Schema validation failed"**: Copy the exact JSON content from the schema files
- **"Only seeing 1 Action Group"**: You need to click "Add Action Group" 3 times to create 3 separate action groups

### General Issues
- **Bedrock Access**: Ensure your AWS account has Bedrock enabled
- **Model Access**: Request access to Claude 3.5 Sonnet in Bedrock console
- **Lambda Permissions**: The functions already have proper IAM roles
- **API Gateway**: The chat endpoint is ready and configured

### Verification Steps
After setup, you should see:
- ✅ 1 Bedrock Agent named `certification-hunter-agent`
- ✅ 3 Action Groups: `web_discovery`, `career_planner`, `learning_resources`
- ✅ 1 Agent Alias named `production`
- ✅ Chat Lambda updated with correct Agent ID and Alias ID

## Clean Up

To remove the deployed resources:
```bash
cd cdk
$env:AWS_PROFILE="msr-aws"; cdk destroy SimpleBedrockStack
```