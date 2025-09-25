# Learning Resources System

This system implements a dynamic learning resources feature that replaces hardcoded links in the frontend with data stored in DynamoDB and retrieved via Lambda functions.

## Architecture

```
Frontend (agent-chat.html)
    ↓ Button Click
API Gateway
    ↓ HTTP Request
Strands Agent Lambda
    ↓ get_learning_resources action
DynamoDB (learning-resources table)
    ↓ Query by provider
Lambda Response
    ↓ Formatted resources
Frontend Display
```

## Components

### 1. DynamoDB Table: `learning-resources`
- **Partition Key**: `provider` (AWS, AZURE, GCP, SALESFORCE, DATABRICKS)
- **Sort Key**: `resource_id` (unique identifier for each resource)
- **Attributes**:
  - `name`: Display name of the resource
  - `url`: Link to the resource
  - `description`: Brief description
  - `category`: Resource category (Training Platform, Documentation, etc.)
  - `created_at`: Timestamp
  - `updated_at`: Timestamp

### 2. Lambda Functions

#### Learning Resources Lambda (`lambda/learning_resources_lambda/`)
- **Purpose**: Standalone function to query learning resources
- **Endpoint**: `GET /learning-resources?provider=AWS`
- **Response**: Formatted list of resources for the specified provider

#### Strands Agent Lambda (Updated)
- **New Action**: `get_learning_resources`
- **Purpose**: Integrated with existing agent for seamless frontend experience
- **Trigger**: When frontend buttons are clicked

#### Bedrock Agent Tools (`lambda/agent_tools/`)
- **learning_resources.py**: Tool for Bedrock Agent to access learning resources
- **Integration**: Allows Bedrock Agent to dynamically fetch resources

### 3. Frontend Updates (`frontend/agent-chat.html`)
- **Button Behavior**: Now triggers `get_learning_resources` action instead of static responses
- **Dynamic Loading**: Resources loaded from DynamoDB via API calls
- **Formatted Display**: Resources displayed with clickable links and descriptions

## Deployment

### Quick Deploy
```bash
python deploy_learning_resources.py
```

### Manual Deploy
```bash
# 1. Deploy CDK stack
cd cdk
cdk bootstrap
cdk deploy CertificationHunterStack --require-approval never

# 2. Populate DynamoDB
python populate_learning_resources.py

# 3. Test the system
python test_learning_resources_system.py
```

## Usage

### Frontend Usage
1. Open `frontend/agent-chat.html` in a browser
2. Click any "Find resources for learning [Provider]" button
3. Resources are dynamically loaded from DynamoDB
4. Links are clickable and open in new tabs

### API Usage
```bash
# Get AWS resources
curl "https://your-api-gateway-url/learning-resources?provider=AWS"

# Get all resources
curl "https://your-api-gateway-url/learning-resources"
```

### Programmatic Usage
```python
import boto3
import json

# Via Lambda
lambda_client = boto3.client('lambda')
response = lambda_client.invoke(
    FunctionName='CertificationHunterStack-StrandsAgentFunction',
    Payload=json.dumps({
        "action": "get_learning_resources",
        "provider": "AWS"
    })
)

# Via DynamoDB directly
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('learning-resources')
response = table.query(
    KeyConditionExpression=Key('provider').eq('AWS')
)
```

## Data Management

### Adding New Resources
```python
import boto3
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('learning-resources')

table.put_item(Item={
    'provider': 'AWS',
    'resource_id': 'new-resource-id',
    'name': 'New AWS Resource',
    'url': 'https://example.com',
    'description': 'Description of the resource',
    'category': 'Training',
    'created_at': datetime.utcnow().isoformat(),
    'updated_at': datetime.utcnow().isoformat()
})
```

### Updating Resources
```python
table.update_item(
    Key={
        'provider': 'AWS',
        'resource_id': 'existing-resource-id'
    },
    UpdateExpression='SET #name = :name, updated_at = :updated',
    ExpressionAttributeNames={'#name': 'name'},
    ExpressionAttributeValues={
        ':name': 'Updated Resource Name',
        ':updated': datetime.utcnow().isoformat()
    }
)
```

## Testing

### Run All Tests
```bash
python test_learning_resources_system.py
```

### Individual Tests
```bash
# Test DynamoDB
python -c "from test_learning_resources_system import test_dynamodb_direct; test_dynamodb_direct()"

# Test Lambda
python -c "from test_learning_resources_system import test_lambda_function; test_lambda_function()"

# Test API Gateway
python -c "from test_learning_resources_system import test_api_gateway; test_api_gateway()"
```

## Troubleshooting

### Common Issues

1. **Table Not Found**
   - Ensure CDK stack is deployed: `cd cdk && cdk deploy`
   - Check table exists: `aws dynamodb describe-table --table-name learning-resources`

2. **Lambda Function Not Found**
   - Check function exists: `aws lambda list-functions | grep LearningResources`
   - Redeploy stack if needed

3. **API Gateway 404**
   - Check API endpoint in CloudFormation outputs
   - Verify CORS configuration

4. **Empty Results**
   - Run populate script: `python populate_learning_resources.py`
   - Check DynamoDB table has data

### Logs
- **Lambda Logs**: CloudWatch → Log Groups → `/aws/lambda/CertificationHunterStack-*`
- **API Gateway Logs**: CloudWatch → Log Groups → `API-Gateway-Execution-Logs_*`

## Benefits

1. **Dynamic Content**: Resources can be updated without code changes
2. **Scalable**: Easy to add new providers and resources
3. **Maintainable**: Centralized data management
4. **Consistent**: Same data source for all interfaces
5. **Trackable**: Usage analytics and resource popularity
6. **Bedrock Integration**: AI agent can access and recommend resources

## Future Enhancements

1. **Admin Interface**: Web UI for managing resources
2. **Analytics**: Track resource usage and popularity
3. **Personalization**: Recommend resources based on user profile
4. **Caching**: Redis/ElastiCache for improved performance
5. **Search**: Full-text search across resources
6. **Categories**: Advanced filtering and categorization
7. **Ratings**: User ratings and reviews for resources