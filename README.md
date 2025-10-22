# 🎯 Certification Deals Hunter

An intelligent web application that discovers and matches certification deals to user profiles using AWS Lambda, DynamoDB, and AI-powered search capabilities.

## 🌟 Current Features

- **🔍 Smart Deal Discovery**: Uses Google Search API and web scraping to find current certification deals
- **🎯 Personalized Matching**: AI-powered recommendations based on user profiles and preferences
- **💬 Interactive Chat Interface**: Conversational AI agent for deal discovery and career guidance
- **📊 Multi-Provider Support**: Covers AWS, Azure, Google Cloud, Databricks, and Salesforce certifications
- **🚀 Responsive Web UI**: Clean, modern interface with auto-scroll and real-time updates
- **☁️ Serverless Architecture**: Built on AWS Lambda, DynamoDB, and API Gateway

## 🏗️ Architecture

<img width="1864" height="717" alt="image" src="https://github.com/user-attachments/assets/45ac6c66-f400-4be6-82a3-5188e4193b41" />


## 🚀 Quick Start

### Prerequisites

- AWS CLI configured with appropriate permissions
- AWS CDK installed (`npm install -g aws-cdk`)
- Python 3.11+
- Google Search API credentials (optional, for enhanced search)

### 1. Environment Setup

```bash
# Clone the repository
git clone <repository-url>
cd cert-deals-agent

# Set up environment variables
cp .env.example .env
# Edit .env with your AWS account details and API keys
```

### 2. Deploy Infrastructure

```bash
# Use the automated deployment script
python deploy_strands_to_aws.py

# Or deploy manually
cd cdk
cdk bootstrap  # First time only
cdk deploy CertificationHunterStack
```

### 3. Access the Application

After deployment, you'll get:
- **Website URL**: Your hosted frontend application
- **API Endpoint**: For direct API access
- **Chat Interface**: AI-powered conversational agent

## 📁 Project Structure

```
cert-deals-agent/
├── 📁 frontend/                # Web application
│   ├── index.html              # Main application interface
│   ├── agent-chat.html         # AI chat interface
│   └── logos/                  # Provider logos and assets
├── 📁 lambda/                  # AWS Lambda functions
│   └── strands_agent_lambda/   # Main Lambda function
│       └── lambda_function.py  # Core application logic
├── 📁 cdk/                     # AWS CDK infrastructure
│   ├── app.py                  # CDK application entry point
│   └── stacks/                 # CDK stack definitions
├── 📁 docs/                    # Documentation
├── 📁 tests/                   # Test files
├── deploy_strands_to_aws.py    # Automated deployment script
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 🎯 Usage

### Main Application

1. **Complete Your Profile**: Enter your details, target certifications, and preferred providers
2. **Discover Deals**: Click "Find My Certification Deals" to get personalized recommendations
3. **Review Results**: Browse deals with discounts, eligibility requirements, and direct links
4. **Save Preferences**: Your profile is saved for future personalized recommendations

### AI Chat Agent

1. **Access Chat**: Click "Chat with AI Agent" for conversational assistance
2. **Ask Questions**: 
   - "Find me AWS certification deals"
   - "What's the best path to become a cloud architect?"
   - "Compare Azure vs AWS certification costs"
   - "Show me deals expiring soon"
3. **Get Recommendations**: Receive personalized career and certification guidance

## 🔧 API Actions

The Lambda function supports these actions:

- `discover_deals`: Find and store certification deals using Google Search API and web scraping
- `save_profile`: Save user preferences and profile information
- `get_recommendations`: Get personalized deal recommendations based on user profile
- `analyze_trends`: Market analysis and insights from collected data
- `search_deals`: Search for specific types of certification deals
- `get_user_profile`: Retrieve saved user profile and preferences

## 🌐 Supported Providers

- **AWS**: Amazon Web Services certifications
- **Azure**: Microsoft Azure certifications  
- **Google Cloud**: Google Cloud Platform certifications
- **Databricks**: Databricks Certification Platform
- **Salesforce**: Salesforce Certification Platform

## 🛠️ Development

### Local Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Test API endpoint
python tests/test_api.py

# Test Lambda function locally
python -c "from lambda.strands_agent_lambda.lambda_function import lambda_handler; print(lambda_handler({'action': 'discover_deals'}, {}))"
```

### Adding New Features

1. **New Provider**: Add scraping logic in `lambda_function.py`
2. **New UI Component**: Extend frontend HTML/CSS/JS files
3. **New API Action**: Add handler in Lambda function
4. **New Infrastructure**: Update CDK stack definitions

## 📊 Data Storage

### DynamoDB Tables

- **certification-offers**: Stores discovered deals with metadata, confidence scores, and expiry dates
- **certification-users**: Stores user profiles, preferences, and interaction history

### Data Flow

1. **Discovery**: Google Search API + web scraping → deals stored in `certification-offers`
2. **User Profile**: Form submission → saved to `certification-users`
3. **Matching**: AI-powered matching → personalized recommendations
4. **Analytics**: Usage patterns and deal effectiveness tracking

##  Security

- CORS enabled for frontend access
- Environment variables for sensitive configuration
- AWS IAM roles with least privilege access
- Input validation and error handling

## 🚀 Deployment

### Automated Deployment

```bash
python deploy_strands_to_aws.py
```

This script:
-  Checks prerequisites
-  Installs dependencies
-  Deploys CDK infrastructure
-  Tests the deployment
-  Provides endpoint URLs

### Manual Deployment

```bash
cd cdk
cdk deploy CertificationHunterStack
```

## 🐛 Troubleshooting

### Common Issues

1. **Lambda Import Errors**: Ensure dependencies are properly installed
2. **CORS Issues**: Check API Gateway CORS configuration
3. **DynamoDB Access**: Verify IAM permissions
4. **Frontend Not Loading**: Check API endpoint URL in HTML files

### Debug Mode

Enable detailed logging by checking browser console and CloudWatch logs.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- AWS for serverless infrastructure
- Certification providers for deal information
- Open source community for tools and libraries
