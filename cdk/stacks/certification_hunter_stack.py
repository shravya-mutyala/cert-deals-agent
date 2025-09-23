from aws_cdk import (
    Stack,
    CfnOutput,
    aws_dynamodb as dynamodb,
    aws_lambda as _lambda,
    aws_apigateway as apigateway,
    aws_s3 as s3,
    aws_s3_deployment as s3deploy,
    aws_events as events,
    aws_events_targets as targets,
    aws_iam as iam,
    Duration,
    RemovalPolicy
)
from constructs import Construct
import os

class CertificationHunterStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # DynamoDB Tables
        self.offers_table = dynamodb.Table(
            self, "OffersTable",
            table_name="certification-offers",
            partition_key=dynamodb.Attribute(name="offer_id", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="provider", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )

        self.users_table = dynamodb.Table(
            self, "UsersTable", 
            table_name="certification-users",
            partition_key=dynamodb.Attribute(name="user_id", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )

        # S3 Bucket for static website hosting
        self.assets_bucket = s3.Bucket(
            self, "AssetsBucket",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            website_index_document="index.html",
            public_read_access=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ACLS
        )

        # Lambda Functions
        self.strands_agent_function = self._create_strands_agent_lambda()
        
        # API Gateway
        self.api = self._create_api()
        
        # EventBridge for scheduling
        self._create_scheduler()



    def _create_strands_agent_lambda(self):
        """Create Strands Agent Lambda function"""
        function = _lambda.Function(
            self, "StrandsAgentFunction",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="lambda_function.lambda_handler",
            code=_lambda.Code.from_asset("../lambda/strands_agent_lambda"),
            timeout=Duration.minutes(5),
            memory_size=512,
            environment={
                "OFFERS_TABLE": self.offers_table.table_name,
                "USERS_TABLE": self.users_table.table_name,
                "GOOGLE_SEARCH_API_KEY": os.environ.get("GOOGLE_SEARCH_API_KEY", "AIzaSyDCk-_SnedDJTgf3Xk9OCntP_fhkjlgvyU"),
                "GOOGLE_SEARCH_ENGINE_ID": os.environ.get("GOOGLE_SEARCH_ENGINE_ID", "5054e8a14948642be")
            }
        )
        
        # Grant DynamoDB permissions
        self.offers_table.grant_read_write_data(function)
        self.users_table.grant_read_write_data(function)
        
        # Bedrock permissions (if needed for future enhancements)
        function.add_to_role_policy(iam.PolicyStatement(
            actions=["bedrock:InvokeModel"],
            resources=["*"]
        ))
        
        return function

    def _create_api(self):
        api = apigateway.RestApi(
            self, "CertificationHunterAPI",
            rest_api_name="Certification Hunter API"
        )
        
        # All endpoints use the strands agent function
        offers = api.root.add_resource("offers")
        offers.add_method("GET", apigateway.LambdaIntegration(self.strands_agent_function))
        
        # Users endpoint  
        users = api.root.add_resource("users")
        users.add_method("POST", apigateway.LambdaIntegration(self.strands_agent_function))
        
        # Strands Agent endpoint
        strands = api.root.add_resource("strands")
        strands.add_method("POST", apigateway.LambdaIntegration(self.strands_agent_function))
        strands.add_method("OPTIONS", apigateway.MockIntegration(
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
        
        return api

    def _create_scheduler(self):
        # Daily scraping schedule (using strands agent function)
        rule = events.Rule(
            self, "DailyScrapeRule",
            schedule=events.Schedule.cron(hour="6", minute="0")
        )
        rule.add_target(targets.LambdaFunction(self.strands_agent_function))
        
        # Deploy frontend
        self._deploy_frontend()
        
        # Stack outputs
        CfnOutput(
            self, "CertificationHunterAPIEndpoint",
            value=self.api.url,
            description="API Gateway endpoint URL"
        )
        
        CfnOutput(
            self, "AssetsBucketName", 
            value=self.assets_bucket.bucket_name,
            description="S3 bucket for frontend assets"
        )
        
        CfnOutput(
            self, "OffersTableName",
            value=self.offers_table.table_name,
            description="DynamoDB table for offers"
        )
        
        CfnOutput(
            self, "UsersTableName",
            value=self.users_table.table_name,
            description="DynamoDB table for users"
        )
        
        # Website URL output
        CfnOutput(
            self, "WebsiteURL",
            value=self.assets_bucket.bucket_website_url,
            description="Website URL"
        )
        
        # Strands Agent endpoint
        CfnOutput(
            self, "StrandsAgentEndpoint",
            value=f"{self.api.url}strands",
            description="Strands Agent API endpoint"
        )

    def _deploy_frontend(self):
        """Deploy frontend to S3"""
        
        # Deploy all frontend assets to S3
        s3deploy.BucketDeployment(
            self, "DeployFrontend",
            sources=[s3deploy.Source.asset("../frontend")],
            destination_bucket=self.assets_bucket
        )