#!/usr/bin/env python3
"""
Refactored Lambda function for certification deals
- Modular architecture with focused services
- Clean separation of concerns
- Improved testability and maintainability
"""

import json
from datetime import datetime
from services.discovery_service import DiscoveryService
from services.user_service import UserService
from services.analytics_service import AnalyticsService
from utils.json_encoder import DecimalEncoder

print("Lambda module loading...")

# Initialize services
discovery_service = DiscoveryService()
user_service = UserService()
analytics_service = AnalyticsService()


def lambda_handler(event, context):
    """Main Lambda handler - routes requests to appropriate services"""
    print(f"INFO: Lambda invoked with event: {json.dumps(event, default=str)}")
    
    try:
        # Handle CORS preflight requests
        http_method = event.get('httpMethod', event.get('requestContext', {}).get('http', {}).get('method', ''))
        if http_method == 'OPTIONS':
            return handle_options_request()
        
        # Extract action from event body if it's a POST request
        if 'body' in event and event['body']:
            try:
                body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
                action = body.get('action', 'discover_deals')
                print(f"INFO: Parsed body action: {action}")
                # Merge body into event for backward compatibility
                event.update(body)
            except json.JSONDecodeError as e:
                print(f"ERROR: Failed to parse JSON body: {e}")
                action = event.get('action', 'discover_deals')
        else:
            action = event.get('action', 'discover_deals')
        
        print(f"INFO: Final action determined: {action}")
        
        if action == 'discover_deals':
            return handle_discover_deals(event)
        elif action == 'get_recommendations':
            return handle_get_recommendations(event)
        elif action == 'save_user_profile' or action == 'save_profile':
            return handle_save_user_profile(event)
        elif action == 'analyze_trends':
            return handle_analyze_trends(event)
        elif action == 'intelligent_search' or action == 'google_search':
            print(f"INFO: Routing to Google search handler")
            return handle_google_search(event)
        else:
            print(f"ERROR: Unknown action received: {action}")
            print(f"ERROR: Available actions: discover_deals, get_recommendations, save_user_profile, save_profile, analyze_trends, intelligent_search, google_search")
            return create_error_response(f"Unknown action: {action}. Available actions: discover_deals, get_recommendations, save_user_profile, analyze_trends, google_search", 400)
            
    except Exception as e:
        print(f"ERROR: Lambda handler error: {e}")
        return create_error_response(f"Internal server error: {str(e)}", 500)


def handle_discover_deals(event):
    """Handle deal discovery requests"""
    # Check if this is a specific search request
    provider = event.get('provider')
    certification_name = event.get('certification_name')
    student_status = event.get('student_status', False)
    
    if provider and certification_name:
        # Specific search for one provider and certification
        result = discovery_service.discover_specific_certification_deal(
            provider, certification_name, student_status
        )
    else:
        # General search (legacy support)
        providers = event.get('providers', ['AWS', 'Azure', 'Google Cloud', 'Databricks', 'Salesforce'])
        result = discovery_service.discover_certification_deals(providers)
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
        },
        'body': json.dumps(result, cls=DecimalEncoder)
    }


def handle_get_recommendations(event):
    """Handle user recommendation requests"""
    user_id = event.get('user_id')
    if not user_id:
        return create_error_response("user_id is required", 400)
    
    result = user_service.get_user_recommendations(user_id)
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
        },
        'body': json.dumps(result, cls=DecimalEncoder)
    }


def handle_save_user_profile(event):
    """Handle user profile save requests"""
    user_id = event.get('user_id')
    current_role = event.get('current_role')
    target_role = event.get('target_role')
    preferred_cloud = event.get('preferred_cloud', 'AWS')
    
    if not all([user_id, current_role, target_role]):
        return create_error_response("user_id, current_role, and target_role are required", 400)
    
    result = user_service.save_user_profile(user_id, current_role, target_role, preferred_cloud)
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
        },
        'body': json.dumps(result, cls=DecimalEncoder)
    }


def handle_analyze_trends(event):
    """Handle market trends analysis requests"""
    result = analytics_service.analyze_market_trends()
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
        },
        'body': json.dumps(result, cls=DecimalEncoder)
    }


def handle_google_search(event):
    """Handle Google search requests from agent chat"""
    print(f"INFO: Google search handler called with event: {json.dumps(event, default=str)}")
    
    query = event.get('query', '')
    context = event.get('context', 'general')
    
    if not query:
        print("ERROR: No query provided for search")
        return create_error_response("Query is required for search", 400)
    
    print(f"INFO: Processing search query: {query}")
    
    try:
        # Try to use the discovery service which already has search capabilities
        print("INFO: Using discovery service for search")
        
        # Check if this looks like a deal-related query
        deal_keywords = ['deal', 'discount', 'voucher', 'challenge', 'promotion', 'offer', 'free', 'coupon']
        is_deal_query = any(keyword in query.lower() for keyword in deal_keywords)
        
        if is_deal_query and ('aws' in query.lower() or 'ai practitioner' in query.lower()):
            # Use the existing deal discovery for AWS AI Practitioner
            print("INFO: Detected AWS AI Practitioner deal query, using discovery service")
            result = discovery_service.discover_specific_certification_deal('AWS', 'AI Practitioner', False)
            
            # Format for chat
            formatted_results = {
                'response_type': 'deal_results',
                'query': query,
                'summary': f"Found {result.get('deals_discovered', 0)} deals for AWS AI Practitioner certification.",
                'deals': result.get('deals', []),
                'message': result.get('summary', 'Search completed')
            }
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
                },
                'body': json.dumps({
                    'success': True,
                    'result': formatted_results
                }, cls=DecimalEncoder)
            }
        else:
            # For general queries, try to use search service
            try:
                from services.search_service import SearchService
                search_service = SearchService()
                
                # Enhance the query for better results
                enhanced_query = search_service.enhance_search_query(query)
                search_results = search_service.search_google_api(enhanced_query)
                
                if search_results.get('success', False):
                    # Format results for chat display
                    formatted_results = format_search_results_for_chat(search_results, query)
                    
                    return {
                        'statusCode': 200,
                        'headers': {
                            'Content-Type': 'application/json',
                            'Access-Control-Allow-Origin': '*',
                            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
                        },
                        'body': json.dumps({
                            'success': True,
                            'result': formatted_results
                        }, cls=DecimalEncoder)
                    }
                else:
                    # Return fallback response
                    print(f"WARNING: Search failed: {search_results.get('error', 'Unknown error')}")
                    return create_fallback_search_response(query, search_results.get('error', 'Search unavailable'))
                    
            except ImportError as ie:
                print(f"WARNING: SearchService import failed: {ie}")
                return create_fallback_search_response(query, "Search service unavailable")
            
    except Exception as e:
        print(f"ERROR: Google search handler error: {e}")
        import traceback
        traceback.print_exc()
        return create_error_response(f"Search error: {str(e)}", 500)


def create_fallback_search_response(query, error_msg):
    """Create a fallback response when search fails"""
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
        },
        'body': json.dumps({
            'success': True,
            'result': {
                'response_type': 'fallback',
                'message': f"I couldn't search for '{query}' right now ({error_msg}), but I can help you with certification questions about AWS, Azure, Google Cloud, Databricks, or Salesforce. Try asking about specific certifications or use the resource buttons.",
                'query': query,
                'error': error_msg
            }
        }, cls=DecimalEncoder)
    }


def format_search_results_for_chat(search_results, original_query):
    """Format Google search results for chat display"""
    items = search_results.get('items', [])
    
    if not items:
        return {
            'response_type': 'no_results',
            'message': f"No results found for '{original_query}'. Try asking about specific certification topics.",
            'query': original_query
        }
    
    # Take top 5 results
    top_results = items[:5]
    
    # Create a summary
    summary_parts = []
    sources = []
    
    for i, item in enumerate(top_results):
        title = item.get('title', 'Untitled')
        snippet = item.get('snippet', 'No description available')
        link = item.get('link', '#')
        
        # Add to sources for reference
        sources.append({
            'title': title,
            'link': link,
            'snippet': snippet
        })
        
        # Create summary point
        summary_parts.append(f"**{i+1}. {title}**\n{snippet}")
    
    summary = "\n\n".join(summary_parts)
    
    return {
        'response_type': 'search_results',
        'query': original_query,
        'summary': summary,
        'sources': sources,
        'total_results': len(items)
    }


def handle_options_request():
    """Handle CORS preflight OPTIONS requests"""
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
            'Access-Control-Max-Age': '86400'
        },
        'body': ''
    }


def create_error_response(message, status_code):
    """Create standardized error response"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
        },
        'body': json.dumps({
            'error': message,
            'timestamp': json.dumps(datetime.now(), default=str)
        })
    }


# Legacy function support for backward compatibility
def discover_certification_deals(providers=None):
    """Legacy function wrapper for backward compatibility"""
    return discovery_service.discover_certification_deals(providers)


def get_user_recommendations(user_id):
    """Legacy function wrapper for backward compatibility"""
    return user_service.get_user_recommendations(user_id)


def save_user_profile(user_id, current_role, target_role, preferred_cloud='AWS'):
    """Legacy function wrapper for backward compatibility"""
    return user_service.save_user_profile(user_id, current_role, target_role, preferred_cloud)


def analyze_market_trends():
    """Legacy function wrapper for backward compatibility"""
    return analytics_service.analyze_market_trends()


# For testing and development
if __name__ == "__main__":
    # Test event
    test_event = {
        'action': 'discover_deals',
        'providers': ['AWS', 'Azure']
    }
    
    result = lambda_handler(test_event, None)
    print(json.dumps(result, indent=2, cls=DecimalEncoder))