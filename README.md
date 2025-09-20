# 🎯 Certification Deals Hunter

An intelligent web application that discovers and matches certification deals to user profiles using AWS Lambda, DynamoDB, and real-time web scraping.

## 🌟 Features

- **🔍 Real-time Deal Discovery**: Scrapes certification providers (AWS, Azure, Google Cloud) for current deals
- **🎯 Personalized Matching**: AI-powered recommendations based on user profiles
- **💬 Interactive Chat Agent**: Conversational interface for deal discovery and career advice
- **📊 Market Analysis**: Trends and insights from collected certification data
- **🚀 Auto-scroll UI**: Seamless user experience with automatic navigation
- **☁️ Serverless Architecture**: Built on AWS Lambda, DynamoDB, and API Gateway

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │   API Gateway    │    │  Lambda Function│
│   (HTML/JS)     │───▶│                  │───▶│   (Python)      │
│                 │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
                                                         ▼
                                               ┌─────────────────┐
                                               │   DynamoDB      │
                                               │   Tables        │
                                               │                 │
                                               └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- AWS CLI configured with appropriate permissions
- AWS CDK installed (`npm install -g aws-cdk`)
- Python 3.11+

### 1. Clone and Setup

```bash
git clone <repository-url>
cd cert-deals-agent
```

### 2. Deploy Infrastructure

```bash
cd cdk
cdk bootstrap  # First time only
cdk deploy CertificationHunterStack
```

### 3. Access the Application

After deployment, CDK will output your application URLs:
- **Frontend**: Open `frontend/index.html` in your browser
- **API Endpoint**: Use the `StrandsAgentEndpoint` output value

## 📁 Project Structure

```
cert-deals-agent/
├── 📁 frontend/                 # Web application
│   ├── index.html              # Main application page
│   ├── agent-chat.html         # Chat interface
│   └── logos/                  # Provider logos
├── 📁 lambda/                  # AWS Lambda functions
│   └── strands_agent_lambda/   # Main Lambda function
│       └── lambda_function.py  # Core application logic
├── 📁 cdk/                     # AWS CDK infrastructure
│   ├── app.py                  # CDK application entry point
│   └── stacks/                 # CDK stack definitions
├── 📁 docs/                    # Documentation
├── deploy_strands_to_aws.py    # Main deployment script
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 🎯 Usage

### Main Application

1. **Fill Your Profile**: Enter your name, location, target certifications, and preferred providers
2. **Find Deals**: Click "Find My Certification Deals" - the page auto-scrolls to results
3. **View Results**: See personalized deals with discounts, eligibility, and source links

### Chat Agent

1. **Open Chat**: Click "Chat with AI Agent" button
2. **Ask Questions**: 
   - "Find me AWS deals"
   - "What are the latest Azure offers?"
   - "Show me market trends"
   - "Give me recommendations"

## 🔧 API Actions

The Lambda function supports these actions:

- `discover_deals`: Find and store certification deals
- `save_profile`: Save user preferences
- `get_recommendations`: Get personalized suggestions
- `analyze_trends`: Market analysis and insights

## 🌐 Supported Providers

- **AWS**: Amazon Web Services certifications
- **Azure**: Microsoft Azure certifications  
- **Google Cloud**: Google Cloud Platform certifications
- **Extensible**: Easy to add new providers

## 🛠️ Development

### Local Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Test Lambda function locally
python -c "from lambda.strands_agent_lambda.lambda_function import lambda_handler; print(lambda_handler({'action': 'discover_deals'}, {}))"
```

### Adding New Providers

1. Add scraping logic in `lambda_function.py`
2. Update provider list in frontend
3. Add provider logos to `frontend/logos/`

## 📊 Data Storage

### DynamoDB Tables

- **certification-offers**: Stores discovered deals
- **certification-users**: Stores user profiles and preferences

### Data Flow

1. User submits profile → Saved to `certification-users`
2. System discovers deals → Stored in `certification-offers`
3. Recommendations generated → Based on user profile + available deals

## 🔒 Security

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
- ✅ Checks prerequisites
- ✅ Installs dependencies
- ✅ Deploys CDK infrastructure
- ✅ Tests the deployment
- ✅ Provides endpoint URLs

### Manual Deployment

```bash
cd cdk
cdk deploy CertificationHunterStack --require-approval never
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

---

**Built with ❤️ for the developer community**

Need help? Open an issue or check the documentation in the `docs/` folder.