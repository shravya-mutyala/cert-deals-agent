# Tests

This directory contains all test files for the Certification Deals Hunter project.

## Test Files

- `test_api.py` - Tests the deployed API endpoint functionality
- More test files can be added here as needed

## Running Tests

```bash
# Run API tests
python tests/test_api.py

# Run all tests (when more are added)
python -m pytest tests/
```

## Test Environment

Make sure to set up your environment variables in `.env` file before running tests:

```
API_ENDPOINT=your_api_gateway_url
AWS_ACCOUNT_ID=your_account_id
AWS_REGION=us-east-1
```