# Strands Agent Lambda - Modular Architecture

This directory contains the refactored certification deals lambda function, now organized into focused, testable modules.

## Architecture Overview

The lambda function has been refactored from a monolithic 1000+ line file into a modular architecture with clear separation of concerns:

### Directory Structure

```
lambda/strands_agent_lambda/
├── lambda_function.py          # Main handler (< 200 lines)
├── requirements.txt            # Dependencies
├── README.md                   # This file
├── services/                   # Business logic services
│   ├── __init__.py
│   ├── discovery_service.py    # Main orchestration service
│   ├── search_service.py       # Google Custom Search integration
│   ├── scraper_service.py      # Web scraping functionality
│   ├── result_formatter.py     # Search result formatting
│   ├── user_service.py         # User management
│   └── analytics_service.py    # Market trends analysis
├── repositories/               # Data access layer
│   ├── __init__.py
│   ├── base_repository.py      # Base DynamoDB operations
│   ├── offers_repository.py    # Deals data access
│   └── users_repository.py     # User data access
├── utils/                      # Common utilities
│   ├── __init__.py
│   ├── constants.py            # Configuration constants
│   ├── date_utils.py           # Date/time utilities
│   └── json_encoder.py         # JSON encoding utilities
└── tests/                      # Unit tests
    ├── __init__.py
    ├── test_search_service.py
    └── test_result_formatter.py
```

## Services

### DiscoveryService
- **Purpose**: Main orchestration service for deal discovery
- **Responsibilities**: Coordinates search, scraping, formatting, and storage
- **Dependencies**: SearchService, ScraperService, ResultFormatterService, OffersRepository

### SearchService
- **Purpose**: Google Custom Search API integration
- **Responsibilities**: Query enhancement, API calls, retry logic
- **Dependencies**: None (pure service)

### ScraperService
- **Purpose**: Web scraping fallback functionality
- **Responsibilities**: Provider-specific scraping, fallback deal creation
- **Dependencies**: None (pure service)

### ResultFormatterService
- **Purpose**: Search result processing and validation
- **Responsibilities**: Format results, extract deal information, calculate confidence scores
- **Dependencies**: None (pure service)

### UserService
- **Purpose**: User profile and recommendation management
- **Responsibilities**: Save profiles, generate recommendations
- **Dependencies**: UsersRepository, OffersRepository

### AnalyticsService
- **Purpose**: Market trends and system monitoring
- **Responsibilities**: Analyze deal data, log errors
- **Dependencies**: OffersRepository

## Repositories

### BaseRepository
- **Purpose**: Common DynamoDB operations
- **Responsibilities**: put_item, get_item, scan operations
- **Dependencies**: boto3

### OffersRepository
- **Purpose**: Certification offers data access
- **Responsibilities**: Store deals with TTL, query by provider
- **Dependencies**: BaseRepository

### UsersRepository
- **Purpose**: User profile data access
- **Responsibilities**: Save/retrieve user profiles
- **Dependencies**: BaseRepository

## Key Improvements

1. **Modularity**: Each service has a single responsibility
2. **Testability**: Services can be tested in isolation
3. **Maintainability**: Changes to one module don't affect others
4. **Extensibility**: New providers/features can be added easily
5. **Error Handling**: Consistent error handling across modules
6. **Dependency Injection**: Services accept dependencies for testing

## Usage

### Lambda Handler
The main lambda handler routes requests based on the `action` parameter:

```python
# Discover deals
event = {'action': 'discover_deals', 'providers': ['AWS', 'Azure']}

# Get user recommendations
event = {'action': 'get_recommendations', 'user_id': 'user123'}

# Save user profile
event = {
    'action': 'save_user_profile',
    'user_id': 'user123',
    'current_role': 'Developer',
    'target_role': 'Cloud Architect',
    'preferred_cloud': 'AWS'
}

# Analyze market trends
event = {'action': 'analyze_trends'}
```

### Legacy Support
Legacy function calls are still supported for backward compatibility:

```python
# These still work
result = discover_certification_deals(['AWS', 'Azure'])
recommendations = get_user_recommendations('user123')
```

## Testing

Run unit tests:

```bash
cd lambda/strands_agent_lambda
python -m pytest tests/
```

Or run individual test files:

```bash
python tests/test_search_service.py
python tests/test_result_formatter.py
```

## Environment Variables

The lambda function uses the same environment variables as before:

- `GOOGLE_SEARCH_API_KEY`: Google Custom Search API key
- `GOOGLE_SEARCH_ENGINE_ID`: Google Custom Search Engine ID
- `OFFERS_TABLE`: DynamoDB table for offers (default: certification-offers)
- `USERS_TABLE`: DynamoDB table for users (default: certification-users)
- `DEAL_TTL_DAYS`: TTL for deals in days (default: 365)
- `GOOGLE_MAX_RETRIES`: Max retry attempts (default: 1)
- `GOOGLE_HTTP_TIMEOUT`: HTTP timeout in seconds (default: 8)
- `DEALS_MAX_AGE_MONTHS`: Max age for search results (default: 12)

## Migration Notes

The refactored lambda function maintains full backward compatibility with the existing API. No changes are required to calling code or infrastructure.

The main `lambda_function.py` file is now under 200 lines as required, with all complex logic moved to focused service modules.