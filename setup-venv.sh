#!/bin/bash

echo "🐍 Setting up Python Virtual Environment for Certification Coupon Hunter"

# Check if Python 3.11+ is available
python_version=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
echo "Found Python version: $python_version"

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install development dependencies
echo "Installing development dependencies..."
pip install -r requirements-dev.txt

# Install CDK dependencies
echo "Installing CDK dependencies..."
cd cdk
pip install -r requirements.txt
cd ..

# Install Lambda dependencies locally for development
echo "Installing Lambda dependencies for local development..."
pip install boto3 requests beautifulsoup4 lxml

echo "SUCCESS: Virtual environment setup complete!"
echo ""
echo "INFO: To activate the environment in the future:"
echo "   source venv/bin/activate"
echo ""
echo "📝 To deactivate:"
echo "   deactivate"
echo ""
echo "🧪 Ready to test:"
echo "   python debug_local.py"