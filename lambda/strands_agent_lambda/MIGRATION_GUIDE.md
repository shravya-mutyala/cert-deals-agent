# Migration Guide: Monolithic to Modular Lambda

This guide helps you understand the changes made during the refactoring and how to work with the new modular architecture.

## What Changed

### Before (Monolithic)
- Single `lambda_function.py` file with 1000+ lines
- All functionality mixed together
- Hard to test individual components
- Difficult to modify without affecting other features

### After (Modular)
- Main handler under 200 lines
- Functionality split into focused services
- Each module has a single responsibility
- Easy to test and modify independently

## File Structure Comparison

### Before
```
lambda/strands_agent_lambda/
└── lambda_function.py (1000+ lines)
```

### After
```
lambda/strands_agent_lambda/
├── lambda_function.py (< 200 lines)
├── services/
│   ├── discovery_service.py
│   ├── search_service.py
│   ├── scraper_service.py
│   ├── result_formatter.py
│   ├── user_service.py
│   └── analytics_service.py
├── repositories/
│   ├── base_repository.py
│   ├── offers_repository.py
│   └── users_repository.py
├── utils/
│   ├── constants.py
│   ├── date_utils.py
│   └── json_encoder.py
└── tests/
    └── (comprehensive test suite)
```

## API Compatibility

### Lambda Handler
The lambda handler now supports structured actions:

```python
# New structured approach
event = {
    'action': 'discover_deals',
    'providers': ['AWS', 'Azure']
}

# Legacy function calls still work
result = discover_certification_deals(['AWS', 'Azure'])
```

### Supported Actions

1. **discover_deals**
   ```python
   event = {
       'action': 'discover_deals',
       'providers': ['AWS', 'Azure', 'Google Cloud']  # optional
   }
   ```

2. **get_recommendations**
   ```python
   event = {
       'action': 'get_recommendations',
       'user_id': 'user123'
   }
   ```

3. **save_user_profile**
   ```python
   event = {
       'action': 'save_user_profile',
       'user_id': 'user123',
       'current_role': 'Developer',
       'target_role': 'Cloud Architect',
       'preferred_cloud': 'AWS'
   }
   ```

4. **analyze_trends**
   ```python
   event = {
       'action': 'analyze_trends'
   }
   ```

## Code Migration Examples

### Old Way (Direct Function Calls)
```python
# Old monolithic approach
from lambda_function import discover_certification_deals, get_user_recommendations

deals = discover_certification_deals(['AWS'])
recommendations = get_user_recommendations('user123')
```

### New Way (Service-Based)
```python
# New modular approach
from services.discovery_service import DiscoveryService
from services.user_service import UserService

discovery_service = DiscoveryService()
user_service = UserService()

deals = discovery_service.discover_certification_deals(['AWS'])
recommendations = user_service.get_user_recommendations('user123')
```

### Lambda Handler Usage
```python
# Both old and new approaches work
from lambda_function import lambda_handler

# New structured approach (recommended)
event = {'action': 'discover_deals', 'providers': ['AWS']}
result = lambda_handler(event, context)

# Legacy functions still available
from lambda_function import discover_certification_deals
deals = discover_certification_deals(['AWS'])
```

## Testing Migration

### Before (Hard to Test)
```python
# Testing the monolithic function was difficult
# Had to mock many dependencies at once
# Tests were brittle and hard to maintain
```

### After (Easy to Test)
```python
# Test individual services in isolation
from services.search_service import SearchService
import unittest
from unittest.mock import patch

class TestSearchService(unittest.TestCase):
    def test_enhance_query(self):
        service = SearchService()
        result = service.enhance_search_query("AWS cert")
        self.assertIn("AWS cert", result)
```

## Deployment Changes

### No Infrastructure Changes Required
- Same Lambda function name
- Same environment variables
- Same IAM permissions
- Same triggers and integrations

### Package Structure
```bash
# Create deployment package
python package.py

# Or manually zip
zip -r lambda.zip lambda_function.py services/ repositories/ utils/
```

## Environment Variables

All existing environment variables are still supported:

- `GOOGLE_SEARCH_API_KEY`
- `GOOGLE_SEARCH_ENGINE_ID`
- `OFFERS_TABLE`
- `USERS_TABLE`
- `DEAL_TTL_DAYS`
- `GOOGLE_MAX_RETRIES`
- `GOOGLE_HTTP_TIMEOUT`
- `DEALS_MAX_AGE_MONTHS`

## Benefits of the New Architecture

### 1. Maintainability
- Each service has a clear purpose
- Changes to one service don't affect others
- Easier to understand and modify

### 2. Testability
- Unit tests for individual services
- Mock dependencies easily
- Better test coverage

### 3. Extensibility
- Add new providers without modifying existing code
- New features can be added as separate services
- Plugin-like architecture

### 4. Error Handling
- Consistent error handling across services
- Better error isolation
- Improved debugging

### 5. Performance
- Services can be optimized independently
- Better resource utilization
- Easier to identify bottlenecks

## Common Migration Issues

### Import Errors
```python
# Wrong
from lambda_function import OFFICIAL_SITES

# Right
from utils.constants import OFFICIAL_SITES
```

### Service Dependencies
```python
# Services are initialized in lambda_function.py
# Use them through the handler or import directly

# Through handler (recommended)
event = {'action': 'discover_deals'}
result = lambda_handler(event, context)

# Direct import (for advanced usage)
from services.discovery_service import DiscoveryService
service = DiscoveryService()
```

### Testing Setup
```python
# Add parent directory to path in tests
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
```

## Rollback Plan

If issues arise, you can rollback by:

1. Keep the old `lambda_function.py` as `lambda_function_old.py`
2. Restore the old file if needed
3. All environment variables and infrastructure remain the same

## Next Steps

1. **Test the new architecture** with your existing workloads
2. **Update any direct imports** to use the new structure
3. **Add new tests** for any custom functionality
4. **Consider extending** the architecture for new features

## Support

The new architecture maintains full backward compatibility. All existing functionality works exactly as before, but now with better organization and testability.

For questions or issues during migration, refer to:
- `README.md` for architecture overview
- `examples/` directory for usage examples
- `tests/` directory for testing examples