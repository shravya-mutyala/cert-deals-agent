# 📁 Project Structure

This document outlines the clean, organized structure of the Certification Deals Hunter project.

## 🏗️ Directory Layout

```
cert-deals-agent/
├── 📁 frontend/                    # Web Application
│   ├── index.html                 # Main application interface
│   ├── agent-chat.html            # AI chat interface
│   └── 📁 logos/                  # Provider logos and assets
│       ├── aws.png
│       ├── azure.png
│       ├── gcp.png
│       ├── databricks.png
│       └── salesforce.png
│
├── 📁 lambda/                     # AWS Lambda Functions
│   └── 📁 strands_agent_lambda/   # Main Lambda function
│       ├── lambda_function.py     # Core application logic
│       └── requirements.txt       # Python dependencies
│
├── 📁 cdk/                        # AWS CDK Infrastructure
│   ├── app.py                     # CDK application entry point
│   ├── cdk.json                   # CDK configuration
│   ├── requirements.txt           # CDK dependencies
│   └── 📁 stacks/                 # CDK stack definitions
│       └── certification_hunter_stack.py
│
├── 📁 docs/                       # Documentation
│   ├── PROJECT_STRUCTURE.md      # This file
│   └── development-plan.md        # Development roadmap
│
├── deploy_strands_to_aws.py       # Main deployment script
├── strands_agent.py               # Core agent logic
├── requirements.txt               # Root Python dependencies
├── .env.example                   # Environment variables template
├── .gitignore                     # Git ignore rules
├── Makefile                       # Build automation
├── deploy.sh                      # Shell deployment script
├── deploy.ps1                     # PowerShell deployment script
├── setup-venv.sh                  # Virtual environment setup (Unix)
├── setup-venv.bat                 # Virtual environment setup (Windows)
└── README.md                      # Main project documentation
```

## 📋 File Descriptions

### Frontend (`frontend/`)
- **`index.html`**: Main web application with profile form and deal discovery
- **`agent-chat.html`**: Interactive chat interface for conversational AI
- **`logos/`**: Provider logos for visual branding

### Lambda Function (`lambda/strands_agent_lambda/`)
- **`lambda_function.py`**: Core serverless function handling:
  - Deal discovery and web scraping
  - User profile management
  - Personalized recommendations
  - Market trend analysis
- **`requirements.txt`**: Python packages needed by Lambda

### Infrastructure (`cdk/`)
- **`app.py`**: CDK application defining AWS resources
- **`stacks/certification_hunter_stack.py`**: Main infrastructure stack
- **`cdk.json`**: CDK configuration and feature flags
- **`requirements.txt`**: CDK and AWS construct dependencies

### Documentation (`docs/`)
- **`PROJECT_STRUCTURE.md`**: This file - project organization
- **`development-plan.md`**: Development roadmap and future features

### Root Files
- **`deploy_strands_to_aws.py`**: Automated deployment script
- **`strands_agent.py`**: Core agent business logic
- **`requirements.txt`**: Main Python dependencies
- **`.env.example`**: Template for environment variables
- **`.gitignore`**: Comprehensive ignore rules for clean repository
- **`Makefile`**: Build and deployment automation
- **`README.md`**: Main project documentation and quick start guide

## 🧹 Cleaned Up Files

The following files were removed during cleanup to maintain a clean repository:

### Removed Test Files
- `test_*.py` - Various test scripts
- `*_test.py` - Test implementations
- `test-scraper.py` - Scraper testing

### Removed Duplicate Deployment Scripts
- `deploy_fixed_lambda.py`
- `deploy_strands_agent.py`
- `deploy_with_profile.py`
- `setup_aws_deployment.py`
- `setup_frontend_test.py`

### Removed Example/Demo Files
- `simple_strands_example.py`
- `simple_working_lambda.py`
- `strands_integration_example.py`
- `create_lambda_layer.py`

### Removed Duplicate Documentation
- `DEPLOYMENT_GUIDE.md`
- `SETUP.md`
- `STRANDS_INTEGRATION_GUIDE.md`
- `enhanced-agent-design.md`
- `manual-deploy-windows.md`

### Removed Legacy Lambda Functions
- `lambda/agent_tools/` - Replaced by consolidated function
- `lambda/matcher/` - Replaced by consolidated function
- `lambda/scraper/` - Replaced by consolidated function

### Removed Temporary/Build Artifacts
- `lambda_layer/` - Build artifact directory
- `lambda_layer_requirements.txt` - Temporary requirements
- `response.json` - Test output file
- Various `.zip` files - Deployment packages

## 🎯 Benefits of Clean Structure

1. **Easy Navigation**: Clear separation of concerns
2. **Maintainable**: Single source of truth for each component
3. **Scalable**: Easy to add new features and providers
4. **Professional**: Clean, organized codebase
5. **Deployable**: Streamlined deployment process
6. **Documented**: Comprehensive documentation

## 🔄 Development Workflow

1. **Frontend Changes**: Edit files in `frontend/`
2. **Backend Logic**: Modify `lambda/strands_agent_lambda/lambda_function.py`
3. **Infrastructure**: Update CDK stacks in `cdk/stacks/`
4. **Deploy**: Run `python deploy_strands_to_aws.py`
5. **Test**: Use the web interface or API directly

## 📝 Adding New Features

1. **New Provider**: Add scraping logic to Lambda function
2. **New UI Component**: Extend frontend HTML/CSS/JS
3. **New API Action**: Add handler in Lambda function
4. **New Infrastructure**: Extend CDK stack definition

This clean structure ensures the project remains maintainable and professional as it grows.