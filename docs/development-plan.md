# Development Plan - Certification Coupon Hunter

## Phase 1: MVP Foundation (Day 1)

### 1. Infrastructure Setup
- [ ] AWS CDK project initialization
- [ ] DynamoDB tables for offers and users
- [ ] Basic Lambda function for web scraping
- [ ] S3 bucket for static assets

### 2. Core Data Model
- [ ] Offer schema (provider, discount, eligibility, expiry)
- [ ] User profile schema (certifications, location, student status)
- [ ] Matching logic foundation

### 3. Basic Web Scraper
- [ ] AWS certification page scraper
- [ ] Salesforce Trailhead offers
- [ ] Simple HTML parsing with safety checks

## Phase 2: AI Integration (Day 2)

### 1. Bedrock Integration
- [ ] Policy text parsing with Claude
- [ ] Eligibility reasoning engine
- [ ] Offer ranking and deduplication

### 2. Agent Orchestration
- [ ] Bedrock Agents setup
- [ ] Tool integration (scraper, database)
- [ ] Autonomous discovery workflow

## Phase 3: User Experience (Day 2-3)

### 1. API Layer
- [ ] REST API with API Gateway
- [ ] User profile management
- [ ] Offer matching endpoints

### 2. Frontend
- [ ] Simple React app
- [ ] Offer dashboard
- [ ] Profile configuration

### 3. Notifications
- [ ] EventBridge scheduled checks
- [ ] Email alerts via SES
- [ ] Calendar integration

## Demo Strategy

Focus on 2-3 certification providers with clear, demonstrable savings to show real value.