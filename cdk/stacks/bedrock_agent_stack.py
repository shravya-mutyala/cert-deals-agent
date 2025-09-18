from aws_cdk import (
    Stack,
    CfnOutput,
    aws_bedrock as bedrock,
    aws_lambda as _lambda,
    aws_iam as iam,
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
        self._create_agent_alias()
    
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
        
        # Create the agent
        agent = bedrock.CfnAgent(
            self, "CertificationHunterAgent",
            agent_name="certification-hunter-agent",
            agent_resource_role_arn=agent_role.role_arn,
            foundation_model="anthropic.claude-3-sonnet-20240229-v1:0",
            instruction="""
You are an expert Certification Deal Hunter and Career Advisor AI agent. Your mission is to help developers and IT professionals:

1. **Discover Certification Deals**: Autonomously find, verify, and rank certification discounts across AWS, Azure, Google Cloud, Databricks, and Salesforce
2. **Analyze Eligibility**: Evaluate complex eligibility requirements and match them to user profiles
3. **Plan Career Paths**: Recommend certification sequences based on career goals and current skills
4. **Optimize Savings**: Compare deals across providers and suggest the best value propositions
5. **Proactive Alerts**: Notify users of expiring deals and new opportunities

**Key Capabilities:**
- Multi-step reasoning for complex certification planning
- Autonomous decision-making for deal discovery and validation
- Context-aware recommendations based on user history
- Integration with multiple external tools and databases
- Learning from user feedback to improve suggestions

**Personality**: Professional, knowledgeable, and proactive. Always explain your reasoning and provide actionable insights.
            """,
            idle_session_ttl_in_seconds=1800,
            agent_collaboration="DISABLED"
        )
        
        return agent
    
    def _create_action_groups(self):
        """Create action groups (tools) for the agent"""
        
        # 1. Web Discovery Tool
        web_discovery_lambda = _lambda.Function(
            self, "WebDiscoveryTool",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="web_discovery.handler",
            code=_lambda.Code.from_asset("lambda/agent_tools"),
            timeout=Duration.minutes(5),
            description="Autonomous web scraping and deal discovery"
        )
        
        bedrock.CfnAgentActionGroup(
            self, "WebDiscoveryActionGroup",
            agent_id=self.agent.attr_agent_id,
            agent_version="DRAFT",
            action_group_name="web_discovery",
            description="Discover certification deals from provider websites",
            action_group_executor={
                "lambda": web_discovery_lambda.function_arn
            },
            api_schema={
                "payload": """{
                    "openapi": "3.0.0",
                    "info": {"title": "Web Discovery API", "version": "1.0.0"},
                    "paths": {
                        "/discover_deals": {
                            "post": {
                                "description": "Discover certification deals from specified providers",
                                "parameters": [
                                    {
                                        "name": "providers",
                                        "in": "query", 
                                        "description": "List of providers to search",
                                        "required": true,
                                        "schema": {"type": "array", "items": {"type": "string"}}
                                    }
                                ],
                                "responses": {"200": {"description": "Deals discovered successfully"}}
                            }
                        }
                    }
                }"""
            }
        )
        
        # 2. Career Planning Tool
        career_planner_lambda = _lambda.Function(
            self, "CareerPlannerTool",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="career_planner.handler", 
            code=_lambda.Code.from_asset("lambda/agent_tools"),
            timeout=Duration.minutes(2),
            description="AI-powered career path planning"
        )
        
        bedrock.CfnAgentActionGroup(
            self, "CareerPlannerActionGroup",
            agent_id=self.agent.attr_agent_id,
            agent_version="DRAFT",
            action_group_name="career_planner",
            description="Plan certification paths based on career goals",
            action_group_executor={
                "lambda": career_planner_lambda.function_arn
            },
            api_schema={
                "payload": """{
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
    
    def _create_agent_alias(self):
        """Create agent alias for production use"""
        
        # Prepare the agent first
        bedrock.CfnAgentAlias(
            self, "CertificationHunterAgentAlias",
            agent_alias_name="production",
            agent_id=self.agent.attr_agent_id,
            description="Production alias for Certification Hunter Agent"
        )
        
        # Output agent information
        CfnOutput(
            self, "BedrockAgentId",
            value=self.agent.attr_agent_id,
            description="Bedrock Agent ID"
        )
        
        CfnOutput(
            self, "BedrockAgentArn",
            value=self.agent.attr_agent_arn,
            description="Bedrock Agent ARN"
        )