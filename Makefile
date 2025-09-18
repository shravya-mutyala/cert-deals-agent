# Certification Coupon Hunter - Development Commands

.PHONY: setup install deploy test-aws clean help

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
	cd cdk && pip install -r requirements.txt
	@echo "✅ Dependencies installed"
	@echo "📝 Ready to deploy: make deploy"

# Deploy to AWS
deploy:
	chmod +x deploy.sh
	./deploy.sh

# Test deployed functions
test-aws:
	python test-scraper.py

# Update and upload frontend to S3
upload-frontend:
	python update-frontend.py

# Clean up generated files
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find lambda/ -name "boto3*" -type d -exec rm -rf {} + 2>/dev/null || true
	find lambda/ -name "botocore*" -type d -exec rm -rf {} + 2>/dev/null || true
	find lambda/ -name "requests*" -type d -exec rm -rf {} + 2>/dev/null || true

# Complete deployment workflow
full-deploy: deploy test-aws upload-frontend
	@echo "🎉 Complete deployment finished!"
	@echo "📝 Your Certification Coupon Hunter is live!"

# Help
help:
	@echo "🚀 Certification Coupon Hunter - AWS Deployment"
	@echo "================================================"
	@echo ""
	@echo "Quick Start:"
	@echo "  1. make setup              - Create virtual environment"
	@echo "  2. source venv/bin/activate - Activate environment"
	@echo "  3. make install            - Install dependencies"
	@echo "  4. make deploy             - Deploy to AWS"
	@echo "  5. make test-aws           - Test deployment"
	@echo "  6. make upload-frontend    - Upload frontend to S3"
	@echo ""
	@echo "Other commands:"
	@echo "  make full-deploy           - Complete deployment workflow"
	@echo "  make clean                 - Clean up generated files"
	@echo ""
	@echo "Prerequisites:"
	@echo "  - AWS CLI configured (aws configure)"
	@echo "  - CDK installed (npm install -g aws-cdk)"
	@echo "  - Python 3.8+"