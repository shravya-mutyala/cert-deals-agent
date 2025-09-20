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
        self.scraper_function = self._create_scraper_lambda()
        self.matcher_function = self._create_matcher_lambda()
        self.strands_agent_function = self._create_strands_agent_lambda()
        
        # API Gateway
        self.api = self._create_api()
        
        # EventBridge for scheduling
        self._create_scheduler()

    def _create_scraper_lambda(self):
        function = _lambda.Function(
            self, "ScraperFunction",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="scraper.handler",
            code=_lambda.Code.from_asset("../lambda/scraper"),
            timeout=Duration.minutes(5),
            environment={
                "OFFERS_TABLE": self.offers_table.table_name,
                "ASSETS_BUCKET": self.assets_bucket.bucket_name
            }
        )
        
        self.offers_table.grant_write_data(function)
        self.assets_bucket.grant_write(function)
        
        # Bedrock permissions
        function.add_to_role_policy(iam.PolicyStatement(
            actions=["bedrock:InvokeModel", "bedrock:InvokeAgent"],
            resources=["*"]
        ))
        
        return function

    def _create_matcher_lambda(self):
        function = _lambda.Function(
            self, "MatcherFunction",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="matcher.handler", 
            code=_lambda.Code.from_asset("../lambda/matcher"),
            timeout=Duration.minutes(2),
            environment={
                "OFFERS_TABLE": self.offers_table.table_name,
                "USERS_TABLE": self.users_table.table_name
            }
        )
        
        self.offers_table.grant_read_data(function)
        self.users_table.grant_read_write_data(function)
        
        function.add_to_role_policy(iam.PolicyStatement(
            actions=["bedrock:InvokeModel"],
            resources=["*"]
        ))
        
        return function

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
                "USERS_TABLE": self.users_table.table_name
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
        
        # Offers endpoint
        offers = api.root.add_resource("offers")
        offers.add_method("GET", apigateway.LambdaIntegration(self.matcher_function))
        
        # Users endpoint  
        users = api.root.add_resource("users")
        users.add_method("POST", apigateway.LambdaIntegration(self.matcher_function))
        
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
        # Daily scraping schedule
        rule = events.Rule(
            self, "DailyScrapeRule",
            schedule=events.Schedule.cron(hour="6", minute="0")
        )
        rule.add_target(targets.LambdaFunction(self.scraper_function))
        
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