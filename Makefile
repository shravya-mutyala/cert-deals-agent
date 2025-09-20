# Certification Deals Hunter - Development Commands

.PHONY: setup install deploy clean lint test help

# Setup virtual environment and install dependencies
setup:
	python3 -m venv venv
	@echo "✅ Virtual environment created"
	@echo "📝 Next steps:"
	@echo "  1. Activate: source venv/bin/activate (Linux/Mac) or venv\\Scripts\\activate.bat (Windows)"
	@echo "  2. Install: make install"
	@echo "  3. Deploy: make deploy"

# Install all dependencies (run after activating venv)
install:
	pip install --upgrade pip
	pip install -r requirements.txt
	cd cdk && pip install -r requirements.txt
	@echo "✅ Dependencies installed"
	@echo "📝 Ready to deploy: make deploy"

# Deploy to AWS using the main deployment script
deploy:
	python deploy_strands_to_aws.py

# Run code formatting and linting
lint:
	black lambda/strands_agent_lambda/lambda_function.py
	flake8 lambda/strands_agent_lambda/lambda_function.py --max-line-length=100

# Test Lambda function locally
test:
	python -c "from lambda.strands_agent_lambda.lambda_function import lambda_handler; print(lambda_handler({'action': 'discover_deals', 'providers': ['AWS']}, {}))"

# Clean up generated files and cache
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -name "*.zip" -delete
	find . -name "response.json" -delete
	rm -rf lambda_layer/ 2>/dev/null || true
	rm -rf cdk.out/ 2>/dev/null || true
	@echo "✅ Cleaned up temporary files"

# Complete development workflow
dev: install lint test
	@echo "🎉 Development setup complete!"

# Help
help:
	@echo "🎯 Certification Deals Hunter - Development Commands"
	@echo "=================================================="
	@echo ""
	@echo "Quick Start:"
	@echo "  1. make setup              - Create virtual environment"
	@echo "  2. source venv/bin/activate - Activate environment (Linux/Mac)"
	@echo "     OR venv\\Scripts\\activate.bat - Activate environment (Windows)"
	@echo "  3. make install            - Install dependencies"
	@echo "  4. make deploy             - Deploy to AWS"
	@echo ""
	@echo "Development:"
	@echo "  make lint                  - Format and lint code"
	@echo "  make test                  - Test Lambda function locally"
	@echo "  make dev                   - Complete development setup"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean                 - Clean up temporary files"
	@echo ""
	@echo "Prerequisites:"
	@echo "  - AWS CLI configured (aws configure)"
	@echo "  - CDK installed (npm install -g aws-cdk)"
	@echo "  - Python 3.11+"