# Certification Coupon Hunter

An autonomous AWS-native AI agent that discovers, verifies, and matches certification discounts to user profiles.

## Architecture Overview

- **Amazon Bedrock**: Core reasoning engine for policy parsing and eligibility matching
- **AWS Lambda + API Gateway**: Web scraping and API endpoints
- **DynamoDB**: Offer storage and user matching
- **EventBridge**: Scheduled autonomous discovery
- **S3 + CloudFront**: Static hosting and asset storage

## Quick Start

1. Set up AWS infrastructure with CDK
2. Deploy Lambda functions for web scraping
3. Configure Bedrock agents for reasoning
4. Set up EventBridge schedules
5. Build minimal frontend

## Development Plan

See `docs/development-plan.md` for detailed implementation steps.