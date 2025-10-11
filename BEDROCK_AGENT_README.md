# Certification Hunter with Bedrock Agent

This project now uses **Amazon Bedrock Agent as the primary system** with the original Strands API as a fallback. The Bedrock Agent provides enhanced capabilities for discovering certification deals, challenges, and career planning.

## Architecture Overview

```
Frontend → Bedrock Chat Lambda → Bedrock Agent (Primary)
                               ↓ (fallback)
                               → Strands API (Fallback)
```

### Primary System: Bedrock Agent
- **Model**: Claude 3.5 Sonnet (anthropic.claude-3-5-sonnet-20241022-v2:0)
- **Custom Tools**:
  - Web Discovery: Finds certification deals and challenges from official sources
  - Career Planner: Creates personalized certification roadmaps
  - Learning Resources: Retrieves curated learning materials

### Fallback System: Strands API
- Original Lambda-based system
- Provides backup functionality when Bedrock Agent is unavailable
- Maintains all existing features

## Key Features

### 🔍 Enhanced Deal Discovery
- Searches official certification provider websites
- Finds certification challenges (like AWS AI Practitioner Challenge)
- Discovers promotional campaigns and special offers
- Focuses on current year deals and upcoming opportunities

### 🎯 Intelligent Career Planning
- Personalized certification roadmaps
- Experience-level appropriate recommendations
- Multi-cloud provider support (AWS, Azure, GCP, Salesforce, Databricks)
- Timeline estimation and next steps

### 📚 Learning Resource Integration
- Official documentation and training platforms
- Hands-on labs and practice environments
- Provider-specific learning paths

## Deployment

### Prerequisites
- AWS CLI configured with appropriate permissions
- AWS CDK installed (`npm install -g aws-cdk`)
- Python 3.11+
- Bedrock access in your AWS account

### Quick Deploy
```bash
python deploy_bedrock_agent.py
```

### Manual Deploy
```bash
# Install dependencies
cd cdk
pip install -r requirements.txt

# Bootstrap CDK (if first time)
cdk bootstrap

# Deploy Bedrock Agent stack
cdk deploy BedrockAgentStack

# Deploy fallback stack
cdk deploy CertificationHunterStack
```

## Configuration

### Environment Variables

**Bedrock Chat Lambda**:
- `BEDROCK_AGENT_ID`: Auto-populated from CDK
- `BEDROCK_AGENT_ALIAS_ID`: Auto-populated from CDK
- `STRANDS_API_ENDPOINT`: URL to fallback Strands API

**Web Discovery Tool**:
- `GOOGLE_SEARCH_API_KEY`: Google Custom Search API key
- `GOOGLE_SEARCH_ENGINE_ID`: Google Custom Search Engine ID

**Learning Resources Tool**:
- `LEARNING_RESOURCES_TABLE`: DynamoDB table name (auto-populated)

### API Endpoints

After deployment, you'll get:
- **Primary**: `https://your-api-gateway.com/chat` (Bedrock Agent)
- **Fallback**: `https://your-strands-api.com/strands` (Original system)

## Usage Examples

### Finding Certification Deals
```javascript
// Frontend request
{
  "message": "Find AWS AI Practitioner certification deals"
}

// Bedrock Agent will:
// 1. Use web discovery tool to search official AWS sites
// 2. Look for current challenges and promotions
// 3. Return formatted results with links and eligibility
```

### Career Path Planning
```javascript
{
  "message": "Plan career path from Developer to Cloud Architect using AWS"
}

// Bedrock Agent will:
// 1. Use career planner tool
// 2. Generate personalized certification sequence
// 3. Provide timeline and next steps
```

### Learning Resources
```javascript
{
  "message": "Get learning resources for Azure"
}

// Bedrock Agent will:
// 1. Query learning resources tool
// 2. Return curated Azure learning materials
// 3. Include official Microsoft resources
```

## Bedrock Agent Tools

### 1. Web Discovery Tool (`web_discovery.py`)
- **Purpose**: Discover certification deals and challenges
- **Providers**: AWS, Azure, GCP, Salesforce, Databricks
- **Features**:
  - Official website scraping
  - Challenge detection (e.g., AWS certification challenges)
  - Deal validation and scoring
  - Current year filtering

### 2. Career Planner Tool (`career_planner.py`)
- **Purpose**: Generate personalized certification roadmaps
- **Features**:
  - Role-based recommendations
  - Experience-level appropriate paths
  - Timeline estimation
  - Learning resource suggestions

### 3. Learning Resources Tool (`learning_resources.py`)
- **Purpose**: Retrieve curated learning materials
- **Data Source**: DynamoDB table with provider-specific resources
- **Features**:
  - Official documentation links
  - Training platform recommendations
  - Hands-on lab suggestions

## Fallback Mechanism

The system automatically falls back to the Strands API if:
- Bedrock Agent is unavailable
- Agent invocation fails
- Response timeout occurs

The fallback maintains full functionality:
- Deal discovery
- Learning resources
- User profile management
- Search capabilities

## Frontend Integration

The frontend automatically detects which system responded:
- **Bedrock Agent**: Shows "AI Agent" responses
- **Strands Fallback**: Shows "Fallback System" responses

Both systems provide consistent user experience with proper error handling.

## Monitoring and Debugging

### CloudWatch Logs
- Bedrock Agent: `/aws/bedrock/agent/your-agent-id`
- Lambda Functions: `/aws/lambda/function-name`

### Common Issues
1. **Bedrock Access**: Ensure your AWS account has Bedrock access
2. **Model Access**: Request access to Claude 3.5 Sonnet model
3. **API Keys**: Configure Google Search API credentials
4. **Permissions**: Verify Lambda execution roles have required permissions

## Cost Optimization

- Bedrock Agent: Pay-per-use model invocation
- Lambda: Pay-per-request with generous free tier
- DynamoDB: On-demand billing for learning resources
- API Gateway: Pay-per-request

## Security

- All API endpoints use HTTPS
- CORS properly configured
- IAM roles follow least privilege principle
- No sensitive data stored in frontend
- API keys managed through environment variables

## Future Enhancements

1. **Multi-language Support**: Extend agent instructions for multiple languages
2. **Advanced Analytics**: Track user preferences and success rates
3. **Real-time Notifications**: Alert users about new deals
4. **Integration APIs**: Connect with external certification platforms
5. **Mobile App**: Native mobile application

## Support

For issues or questions:
1. Check CloudWatch logs for error details
2. Verify AWS permissions and Bedrock access
3. Test fallback system independently
4. Review environment variable configuration

## Contributing

1. Fork the repository
2. Create feature branch
3. Test with both Bedrock Agent and fallback
4. Submit pull request with detailed description

---

**Note**: This system provides intelligent certification guidance while maintaining reliability through the fallback mechanism. The Bedrock Agent enhances user experience with natural language processing and advanced reasoning capabilities.