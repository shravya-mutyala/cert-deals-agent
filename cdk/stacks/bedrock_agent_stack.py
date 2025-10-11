from aws_cdk import (
    Stack,
    CfnOutput,
    CfnResource,
    aws_lambda as _lambda,
    aws_iam as iam,
    aws_apigateway as apigateway,
    Duration
)
from constructs import Construct

class BedrockAgentStack(Stack):
    """Enhanced stack with Bedrock Agent integration"""
    
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # Create the Bedrock Agent
        self.agent = self._create_bedrock_agent()
        
        # Create action groups (tools)
        self._create_action_groups()
        
        # Create agent alias
        self.agent_alias = self._create_agent_alias()
        
        # Create main chat Lambda that uses Bedrock Agent with Strands fallback
        self.chat_lambda = self._create_chat_lambda()
        
        # Create API Gateway
        self._create_api_gateway()
    
    def _create_bedrock_agent(self):
        """Create the main Bedrock Agent"""
        
        # Agent execution role
        agent_role = iam.Role(
            self, "AgentExecutionRole",
            assumed_by=iam.ServicePrincipal("bedrock.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonBedrockFullAccess")
            ]
        )
        
        # Create the agent using CloudFormation resource
        agent = CfnResource(
            self, "CertificationHunterAgent",
            type="AWS::Bedrock::Agent",
            properties={
                "AgentName": "certification-hunter-agent",
                "AgentResourceRoleArn": agent_role.role_arn,
                "FoundationModel": "anthropic.claude-3-5-sonnet-20241022-v2:0",
                "Instruction": """You are an expert Certification Deal Hunter and Career Advisor AI agent. Your mission is to help developers and IT professionals discover certification deals, challenges, and plan their career paths.

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

Use your tools proactively to discover the most current and relevant information for users.""",
                "IdleSessionTtlInSeconds": 1800,
                "AgentCollaboration": "DISABLED"
            }
        )
        
        return agent
    
    def _create_action_groups(self):
        """Create action groups (tools) for the agent"""
        
        # 1. Web Discovery Tool
        web_discovery_lambda = _lambda.Function(
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
        
        web_discovery_action_group = CfnResource(
            self, "WebDiscoveryActionGroup",
            type="AWS::Bedrock::AgentActionGroup",
            properties={
                "AgentId": self.agent.ref,
                "AgentVersion": "DRAFT",
                "ActionGroupName": "web_discovery",
                "Description": "Discover certification deals, challenges, and promotions from official provider websites",
                "ActionGroupExecutor": {
                    "Lambda": web_discovery_lambda.function_arn
                },
                "ApiSchema": {
                    "Payload": """{
                        "openapi": "3.0.0",
                        "info": {"title": "Web Discovery API", "version": "1.0.0"},
                        "paths": {
                            "/discover_deals": {
                                "post": {
                                    "description": "Discover certification deals, challenges, and promotions from specified cloud providers",
                                    "requestBody": {
                                        "required": true,
                                        "content": {
                                            "application/json": {
                                                "schema": {
                                                    "type": "object",
                                                    "properties": {
                                                        "providers": {
                                                            "type": "array",
                                                            "items": {
                                                                "type": "string",
                                                                "enum": ["AWS", "AZURE", "GCP", "SALESFORCE", "DATABRICKS"]
                                                            },
                                                            "description": "List of cloud providers to search for deals"
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    },
                                    "responses": {
                                        "200": {
                                            "description": "Certification deals and challenges discovered successfully",
                                            "content": {
                                                "application/json": {
                                                    "schema": {
                                                        "type": "object",
                                                        "properties": {
                                                            "message": {"type": "string"},
                                                            "deals": {"type": "array"},
                                                            "total_found": {"type": "integer"}
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }"""
                }
            }
        )
        
        # 2. Career Planning Tool
        career_planner_lambda = _lambda.Function(
            self, "CareerPlannerTool",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="career_planner.handler", 
            code=_lambda.Code.from_asset("../lambda/agent_tools"),
            timeout=Duration.minutes(2),
            description="AI-powered career path planning"
        )
        
        # 3. Learning Resources Tool
        learning_resources_lambda = _lambda.Function(
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
        
        career_planner_action_group = CfnResource(
            self, "CareerPlannerActionGroup",
            type="AWS::Bedrock::AgentActionGroup",
            properties={
                "AgentId": self.agent.ref,
                "AgentVersion": "DRAFT",
                "ActionGroupName": "career_planner",
                "Description": "Plan certification paths based on career goals",
                "ActionGroupExecutor": {
                    "Lambda": career_planner_lambda.function_arn
                },
                "ApiSchema": {
                    "Payload": """{
                        "openapi": "3.0.0",
                        "info": {"title": "Career Planner API", "version": "1.0.0"},
                        "paths": {
                            "/plan_path": {
                                "post": {
                                    "description": "Generate certification roadmap for career goals",
                                    "requestBody": {
                                        "required": true,
                                        "content": {
                                            "application/json": {
                                                "schema": {
                                                    "type": "object",
                                                    "properties": {
                                                        "current_role": {"type": "string"},
                                                        "target_role": {"type": "string"},
                                                        "experience_level": {"type": "string"},
                                                        "preferred_cloud": {"type": "string"}
                                                    }
                                                }
                                            }
                                        }
                                    },
                                    "responses": {"200": {"description": "Career path generated"}}
                                }
                            }
                        }
                    }"""
                }
            }
        )
        
        # 3. Learning Resources Action Group
        learning_resources_action_group = CfnResource(
            self, "LearningResourcesActionGroup",
            type="AWS::Bedrock::AgentActionGroup",
            properties={
                "AgentId": self.agent.ref,
                "AgentVersion": "DRAFT",
                "ActionGroupName": "learning_resources",
                "Description": "Get learning resources for cloud providers",
                "ActionGroupExecutor": {
                    "Lambda": learning_resources_lambda.function_arn
                },
                "ApiSchema": {
                    "Payload": """{
                        "openapi": "3.0.0",
                        "info": {"title": "Learning Resources API", "version": "1.0.0"},
                        "paths": {
                            "/get_resources": {
                                "post": {
                                    "description": "Get learning resources for specified provider",
                                    "requestBody": {
                                        "required": true,
                                        "content": {
                                            "application/json": {
                                                "schema": {
                                                    "type": "object",
                                                    "properties": {
                                                        "provider": {
                                                            "type": "string",
                                                            "enum": ["AWS", "AZURE", "GCP", "SALESFORCE", "DATABRICKS"],
                                                            "description": "Cloud provider name"
                                                        }
                                                    },
                                                    "required": ["provider"]
                                                }
                                            }
                                        }
                                    },
                                    "responses": {"200": {"description": "Learning resources retrieved successfully"}}
                                }
                            }
                        }
                    }"""
                }
            }
        )
        
        # Grant Lambda invoke permissions
        web_discovery_lambda.add_permission(
            "BedrockAgentInvoke",
            principal=iam.ServicePrincipal("bedrock.amazonaws.com"),
            action="lambda:InvokeFunction"
        )
        
        career_planner_lambda.add_permission(
            "BedrockAgentInvoke", 
            principal=iam.ServicePrincipal("bedrock.amazonaws.com"),
            action="lambda:InvokeFunction"
        )
        
        learning_resources_lambda.add_permission(
            "BedrockAgentInvoke",
            principal=iam.ServicePrincipal("bedrock.amazonaws.com"),
            action="lambda:InvokeFunction"
        )
        
        # Grant DynamoDB permissions to learning resources Lambda
        learning_resources_lambda.add_to_role_policy(iam.PolicyStatement(
            actions=[
                "dynamodb:Query",
                "dynamodb:GetItem"
            ],
            resources=["arn:aws:dynamodb:*:*:table/learning-resources"]
        ))
    
    def _create_agent_alias(self):
        """Create agent alias for production use"""
        
        # Create agent alias
        agent_alias = CfnResource(
            self, "CertificationHunterAgentAlias",
            type="AWS::Bedrock::AgentAlias",
            properties={
                "AgentAliasName": "production",
                "AgentId": self.agent.ref,
                "Description": "Production alias for Certification Hunter Agent"
            }
        )
        
        self.agent_alias = agent_alias
        return agent_alias
    
    def _create_chat_lambda(self):
        """Create main chat Lambda that uses Bedrock Agent with Strands fallback"""
        
        chat_function = _lambda.Function(
            self, "ChatFunction",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="lambda_function.lambda_handler",
            code=_lambda.Code.from_asset("../lambda/bedrock_chat_lambda"),
            timeout=Duration.minutes(5),
            memory_size=512,
            description="Main chat function with Bedrock Agent and Strands fallback",
            environment={
                "BEDROCK_AGENT_ID": self.agent.ref,
                "BEDROCK_AGENT_ALIAS_ID": self.agent_alias.ref,
                "STRANDS_API_ENDPOINT": "https://your-strands-api-endpoint.com/strands"  # Update with actual endpoint
            }
        )
        
        # Grant Bedrock permissions
        chat_function.add_to_role_policy(iam.PolicyStatement(
            actions=[
                "bedrock:InvokeAgent",
                "bedrock:InvokeModel"
            ],
            resources=["*"]
        ))
        
        return chat_function
    
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
        chat.add_method("POST", apigateway.LambdaIntegration(self.chat_lambda))
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
            self, "BedrockAgentId",
            value=self.agent.ref,
            description="Bedrock Agent ID"
        )
        
        CfnOutput(
            self, "BedrockAgentArn",
            value=self.agent.get_att("AgentArn").to_string(),
            description="Bedrock Agent ARN"
        )
        
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