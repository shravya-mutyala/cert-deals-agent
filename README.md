# 🎯 Certification Coupon Hunter

An autonomous AWS-native AI agent that discovers, verifies, and matches certification discounts to user profiles.

## 🚀 One-Command Deploy

```bash
# Setup environment
make setup && source venv/bin/activate && make install

# Deploy everything (infrastructure + frontend)
make deploy

# That's it! Your app is live! 🎉
```

## 🤖 AI Agent Architecture

### **Core Agent (Bedrock AgentCore)**
- **Amazon Bedrock Agent**: Autonomous certification advisor with multi-step reasoning
- **Agent Tools**: Web discovery, career planning, eligibility analysis
- **Claude 3 Sonnet**: Advanced reasoning for complex decision-making

### **Supporting Infrastructure**
- **AWS Lambda**: Serverless agent tools and API logic
- **DynamoDB**: Knowledge base and user profiles
- **API Gateway**: RESTful endpoints and agent integration
- **EventBridge**: Autonomous scheduling and triggers
- **S3**: Static hosting and asset storage

## 🎯 AI Agent Capabilities

### **Autonomous Decision Making**
- **Proactive Discovery**: Agent decides what to scrape and when
- **Intelligent Filtering**: AI evaluates deal quality and relevance
- **Multi-step Planning**: Complex reasoning for career path optimization

### **Advanced Reasoning**
- **Context Awareness**: Remembers user preferences and history
- **Cross-provider Analysis**: Compares deals across all platforms
- **Career Intelligence**: Maps certifications to career progression

### **Tool Integration**
- **Web Discovery Tool**: Autonomous deal hunting with AI validation
- **Career Planner Tool**: AI-powered certification roadmaps
- **Eligibility Analyzer**: Complex rule evaluation and matching

## 🎯 Supported Certifications

### **AWS**
- Solutions Architect (Associate/Professional)
- Developer Associate, SysOps Administrator
- Security, Data Analytics, Machine Learning Specialty

### **Microsoft Azure**
- Fundamentals (AZ-900), Administrator (AZ-104)
- Developer (AZ-204), Architect (AZ-305)
- Security, Data Engineer, AI Engineer

### **Google Cloud**
- Associate Cloud Engineer
- Professional Cloud Architect, Data Engineer
- Professional DevOps Engineer, Security Engineer

### **Databricks**
- Data Engineer Associate/Professional
- Data Scientist Associate/Professional
- Machine Learning Associate/Professional

### **Salesforce**
- Administrator, Platform Developer
- Sales Cloud, Service Cloud, Marketing Cloud

## 📋 Prerequisites

- AWS Account with CLI configured (`aws configure`)
- CDK installed (`npm install -g aws-cdk`)
- Python 3.8+

## 🎯 Perfect for Hackathons

- **Real Business Value**: Solves actual developer pain points
- **AI Showcase**: Demonstrates Bedrock capabilities
- **AWS Native**: Uses multiple AWS services effectively
- **Scalable**: Production-ready architecture