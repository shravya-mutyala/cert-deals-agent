from aws_cdk import (
    Stack,
    CfnOutput,
    aws_lambda as _lambda,
    aws_iam as iam,
    aws_apigateway as apigateway,
    Duration
)
from constructs import Construct

class SimpleBedrockStack(Stack):
    """Simplified stack with Lambda functions for Bedrock Agent tools"""
    
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # Create Lambda functions for Bedrock Agent tools
        self._create_lambda_functions()
        
        # Create main chat Lambda
        self._create_chat_lambda()
        
        # Create API Gateway
        self._create_api_gateway()
    
    def _create_lambda_functions(self):
        """Create Lambda functions for Bedrock Agent tools"""
        
        # 1. Web Discovery Tool
        self.web_discovery_lambda = _lambda.Function(
            self, "WebDiscoveryTool",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="web_discovery.handler",
            code=_lambda.Code.from_asset("../lambda/agent_tools"),
            timeout=Duration.minutes(5),
            description="Autonomous web scraping and deal discovery",
            environment={
                "GOOGLE_SEARCH_API_KEY": "AIzaSyDCk-_SnedDJTgf3Xk9OCntP_fhkjlgvyU",
                "GOOGLE_SEARCH_ENGINE_ID": "5054e8a14948642be"
            }
        )
        
        # 2. Career Planning Tool
        self.career_planner_lambda = _lambda.Function(
            self, "CareerPlannerTool",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="career_planner.handler", 
            code=_lambda.Code.from_asset("../lambda/agent_tools"),
            timeout=Duration.minutes(2),
            description="AI-powered career path planning"
        )
        
        # 3. Learning Resources Tool
        self.learning_resources_lambda = _lambda.Function(
            self, "LearningResourcesTool",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="learning_resources.handler",
            code=_lambda.Code.from_asset("../lambda/agent_tools"),
            timeout=Duration.minutes(2),
            description="Retrieve learning resources from DynamoDB",
            environment={
                "LEARNING_RESOURCES_TABLE": "learning-resources"
            }
        )
        
        # Grant DynamoDB permissions to learning resources Lambda
        self.learning_resources_lambda.add_to_role_policy(iam.PolicyStatement(
            actions=[
                "dynamodb:Query",
                "dynamodb:GetItem"
            ],
            resources=["arn:aws:dynamodb:*:*:table/learning-resources"]
        ))
    
    def _create_chat_lambda(self):
        """Create main chat Lambda that will use Bedrock Agent with Strands fallback"""
        
        self.chat_function = _lambda.Function(
            self, "ChatFunction",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="lambda_function.lambda_handler",
            code=_lambda.Code.from_asset("../lambda/bedrock_chat_lambda"),
            timeout=Duration.minutes(5),
            memory_size=512,
            description="Main chat function with Bedrock Agent and Strands fallback",
            environment={
                "BEDROCK_AGENT_ID": "PLACEHOLDER_AGENT_ID",  # Will be updated manually
                "BEDROCK_AGENT_ALIAS_ID": "TSTALIASID",
                "STRANDS_API_ENDPOINT": "https://ehvx4tl0lc.execute-api.us-east-1.amazonaws.com/prod/strands"
            }
        )
        
        # Grant Bedrock permissions
        self.chat_function.add_to_role_policy(iam.PolicyStatement(
            actions=[
                "bedrock:InvokeAgent",
                "bedrock:InvokeModel"
            ],
            resources=["*"]
        ))
    
    def _create_api_gateway(self):
        """Create API Gateway for the chat function"""
        
        # Create API Gateway
        api = apigateway.RestApi(
            self, "CertificationHunterAPI",
            rest_api_name="Certification Hunter API with Bedrock Agent",
            description="API for Certification Hunter with Bedrock Agent and Strands fallback"
        )
        
        # Chat endpoint
        chat = api.root.add_resource("chat")
        chat.add_method("POST", apigateway.LambdaIntegration(self.chat_function))
        chat.add_method("OPTIONS", apigateway.MockIntegration(
            integration_responses=[{
                'statusCode': '200',
                'responseParameters': {
                    'method.response.header.Access-Control-Allow-Headers': "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'",
                    'method.response.header.Access-Control-Allow-Origin': "'*'",
                    'method.response.header.Access-Control-Allow-Methods': "'GET,POST,OPTIONS'"
                }
            }],
            request_templates={'application/json': '{"statusCode": 200}'}
        ), method_responses=[{
            'statusCode': '200',
            'responseParameters': {
                'method.response.header.Access-Control-Allow-Headers': True,
                'method.response.header.Access-Control-Allow-Origin': True,
                'method.response.header.Access-Control-Allow-Methods': True
            }
        }])
        
        # Output API information
        CfnOutput(
            self, "ChatAPIEndpoint",
            value=f"{api.url}chat",
            description="Chat API endpoint with Bedrock Agent"
        )
        
        CfnOutput(
            self, "APIGatewayURL",
            value=api.url,
            description="API Gateway base URL"
        )
        
        CfnOutput(
            self, "WebDiscoveryLambdaArn",
            value=self.web_discovery_lambda.function_arn,
            description="Web Discovery Lambda ARN for Bedrock Agent"
        )
        
        CfnOutput(
            self, "CareerPlannerLambdaArn",
            value=self.career_planner_lambda.function_arn,
            description="Career Planner Lambda ARN for Bedrock Agent"
        )
        
        CfnOutput(
            self, "LearningResourcesLambdaArn",
            value=self.learning_resources_lambda.function_arn,
            description="Learning Resources Lambda ARN for Bedrock Agent"
        )