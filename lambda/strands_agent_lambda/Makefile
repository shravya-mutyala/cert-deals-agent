# Makefile for strands agent lambda

.PHONY: test test-unit test-integration clean package install-deps lint format

# Default target
all: test

# Install dependencies
install-deps:
	pip install -r requirements.txt
	pip install pytest pytest-mock boto3-stubs

# Run all tests
test:
	python run_tests.py

# Run unit tests only
test-unit:
	python -m pytest tests/ -m "not integration" -v

# Run integration tests only
test-integration:
	python -m pytest tests/ -m integration -v

# Run specific test file
test-search:
	python tests/test_search_service.py

test-formatter:
	python tests/test_result_formatter.py

test-user:
	python tests/test_user_service.py

test-discovery:
	python tests/test_discovery_service.py

test-handler:
	python tests/test_lambda_handler.py

# Lint code
lint:
	python -m flake8 --max-line-length=120 --ignore=E501,W503 services/ repositories/ utils/ lambda_function.py

# Format code
format:
	python -m black --line-length=120 services/ repositories/ utils/ lambda_function.py

# Clean up
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -f strands_agent_lambda.zip
	rm -rf package/

# Create deployment package
package: clean
	python package.py

# Run examples
example-local:
	python examples/local_testing.py

example-services:
	python examples/service_usage.py

# Check code quality
quality: lint test

# Development setup
dev-setup: install-deps
	@echo "Development environment ready!"
	@echo "Run 'make test' to run tests"
	@echo "Run 'make package' to create deployment package"

# Help
help:
	@echo "Available targets:"
	@echo "  test           - Run all tests"
	@echo "  test-unit      - Run unit tests only"
	@echo "  test-integration - Run integration tests only"
	@echo "  lint           - Lint code"
	@echo "  format         - Format code"
	@echo "  clean          - Clean up temporary files"
	@echo "  package        - Create deployment package"
	@echo "  dev-setup      - Set up development environment"
	@echo "  help           - Show this help message"