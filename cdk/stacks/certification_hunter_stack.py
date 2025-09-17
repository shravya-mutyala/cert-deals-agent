from aws_cdk import (
    Stack,
    aws_dynamodb as dynamodb,
    aws_lambda as _lambda,
    aws_apigateway as apigateway,
    aws_s3 as s3,
    aws_events as events,
    aws_events_targets as targets,
    aws_iam as iam,
    Duration,
    RemovalPolicy
)
from constructs import Construct

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

        # S3 Bucket for assets
        self.assets_bucket = s3.Bucket(
            self, "AssetsBucket",
            bucket_name="certification-hunter-assets",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )

        # Lambda Functions
        self.scraper_function = self._create_scraper_lambda()
        self.matcher_function = self._create_matcher_lambda()
        
        # API Gateway
        self.api = self._create_api()
        
        # EventBridge for scheduling
        self._create_scheduler()

    def _create_scraper_lambda(self):
        function = _lambda.Function(
            self, "ScraperFunction",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="scraper.handler",
            code=_lambda.Code.from_asset("lambda/scraper"),
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
            code=_lambda.Code.from_asset("lambda/matcher"),
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
        
        return api

    def _create_scheduler(self):
        # Daily scraping schedule
        rule = events.Rule(
            self, "DailyScrapeRule",
            schedule=events.Schedule.cron(hour="6", minute="0")
        )
        rule.add_target(targets.LambdaFunction(self.scraper_function))