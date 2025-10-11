#!/usr/bin/env python3
"""
Main Lambda function for Certification Hunter with Bedrock Agent as primary
and Strands Agent as fallback
"""

import json
import boto3
import os
from datetime import datetime
import requests

# Initialize Bedrock Agent Runtime client
bedrock_agent_runtime = boto3.client('bedrock-agent-runtime')

def lambda_handler(event, context):
    """Main handler that routes to Bedrock Agent or falls back to Strands"""
    
    print(f"INFO: Lambda invoked with event: {json.dumps(event, default=str)}")
    
    try:
        # Handle CORS preflight requests
        http_method = event.get('httpMethod', event.get('requestContext', {}).get('http', {}).get('method', ''))
        if http_method == 'OPTIONS':
            return handle_options_request()
        
        # Extract user message from event
        user_message = extract_user_message(event)
        
        if not user_message:
            return create_error_response("No message provided", 400)
        
        print(f"INFO: Processing user message: {user_message}")
        
        # Try Bedrock Agent first
        try:
            bedrock_response = invoke_bedrock_agent(user_message)
            if bedrock_response:
                print("INFO: Successfully processed with Bedrock Agent")
                return create_success_response(bedrock_response, "bedrock_agent")
        except Exception as e:
            print(f"WARNING: Bedrock Agent failed: {e}")
        
        # Fallback to Strands Agent
        try:
            print("INFO: Falling back to Strands Agent")
            strands_response = invoke_strands_fallback(event)
            if strands_response:
                print("INFO: Successfully processed with Strands fallback")
                return create_success_response(strands_response, "strands_fallback")
        except Exception as e:
            print(f"ERROR: Strands fallback also failed: {e}")
        
        # If both fail, return error
        return create_error_response("Both primary and fallback systems are unavailable", 503)
        
    except Exception as e:
        print(f"ERROR: Lambda handler error: {e}")
        return create_error_response(f"Internal server error: {str(e)}", 500)


def extract_user_message(event):
    """Extract user message from various event formats"""
    
    # Try body first (API Gateway)
    if 'body' in event and event['body']:
        try:
            body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
            
            # Check for message field
            if 'message' in body:
                return body['message']
            
            # Check for query field (search requests)
            if 'query' in body:
                return body['query']
            
            # Check for action-based requests
            action = body.get('action', '')
            if action == 'discover_deals':
                providers = body.get('providers', ['AWS'])
                return f"Find certification deals for {', '.join(providers)}"
            elif action == 'get_learning_resources':
                provider = body.get('provider', 'AWS')
                return f"Get learning resources for {provider}"
            elif action == 'save_profile' or action == 'save_user_profile':
                current_role = body.get('current_role', 'Developer')
                target_role = body.get('target_role', 'Cloud Architect')
                return f"Plan career path from {current_role} to {target_role}"
                
        except json.JSONDecodeError:
            pass
    
    # Try direct fields
    if 'message' in event:
        return event['message']
    
    if 'query' in event:
        return event['query']
    
    return None


def invoke_bedrock_agent(user_message):
    """Invoke Bedrock Agent with user message"""
    
    try:
        # Get agent configuration from environment or use defaults
        agent_id = os.environ.get('BEDROCK_AGENT_ID')
        agent_alias_id = os.environ.get('BEDROCK_AGENT_ALIAS_ID', 'TSTALIASID')
        
        if not agent_id:
            print("WARNING: BEDROCK_AGENT_ID not configured")
            return None
        
        # Invoke the agent
        response = bedrock_agent_runtime.invoke_agent(
            agentId=agent_id,
            agentAliasId=agent_alias_id,
            sessionId=f"session_{int(datetime.now().timestamp())}",
            inputText=user_message
        )
        
        # Process the response stream
        agent_response = ""
        for event in response['completion']:
            if 'chunk' in event:
                chunk = event['chunk']
                if 'bytes' in chunk:
                    agent_response += chunk['bytes'].decode('utf-8')
        
        if agent_response:
            return {
                'message': agent_response,
                'source': 'bedrock_agent',
                'timestamp': datetime.now().isoformat()
            }
        
        return None
        
    except Exception as e:
        print(f"ERROR: Bedrock Agent invocation failed: {e}")
        raise


def invoke_strands_fallback(event):
    """Invoke Strands Agent as fallback"""
    
    try:
        # Get Strands API endpoint
        strands_endpoint = os.environ.get('STRANDS_API_ENDPOINT')
        
        if not strands_endpoint:
            print("WARNING: STRANDS_API_ENDPOINT not configured")
            return None
        
        # Forward the request to Strands API
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # Prepare request body
        if 'body' in event and event['body']:
            request_body = event['body']
            if isinstance(request_body, str):
                request_body = json.loads(request_body)
        else:
            request_body = event
        
        # Make request to Strands API
        response = requests.post(
            strands_endpoint,
            json=request_body,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            strands_data = response.json()
            
            # Format response for consistency
            if 'result' in strands_data:
                return {
                    'message': format_strands_response(strands_data['result']),
                    'source': 'strands_fallback',
                    'timestamp': datetime.now().isoformat(),
                    'raw_data': strands_data['result']
                }
            else:
                return {
                    'message': 'Request processed by fallback system',
                    'source': 'strands_fallback',
                    'timestamp': datetime.now().isoformat(),
                    'raw_data': strands_data
                }
        else:
            print(f"ERROR: Strands API returned status {response.status_code}")
            return None
            
    except Exception as e:
        print(f"ERROR: Strands fallback failed: {e}")
        raise


def format_strands_response(result):
    """Format Strands response for user display"""
    
    try:
        response_type = result.get('response_type', 'unknown')
        
        if response_type == 'deal_results':
            deals = result.get('deals', [])
            if deals:
                message = f"Found {len(deals)} certification deals:\n\n"
                for i, deal in enumerate(deals[:5], 1):
                    title = deal.get('title', 'Unknown Deal')
                    provider = deal.get('provider', 'Unknown')
                    discount = deal.get('discount_amount', 'See details')
                    url = deal.get('source_url', '#')
                    message += f"{i}. **{title}** ({provider})\n"
                    message += f"   Discount: {discount}\n"
                    message += f"   Link: {url}\n\n"
                return message
            else:
                return "No certification deals found at the moment."
        
        elif response_type == 'learning_resources':
            resources = result.get('resources', [])
            provider = result.get('provider', 'Unknown')
            if resources:
                message = f"Learning resources for {provider}:\n\n"
                for i, resource in enumerate(resources[:5], 1):
                    name = resource.get('name', 'Unknown Resource')
                    url = resource.get('url', '#')
                    description = resource.get('description', 'No description')
                    message += f"{i}. **{name}**\n"
                    message += f"   {description}\n"
                    message += f"   Link: {url}\n\n"
                return message
            else:
                return f"No learning resources found for {provider}."
        
        elif response_type == 'search_results':
            summary = result.get('summary', '')
            if summary:
                return f"Search Results:\n\n{summary}"
            else:
                return "Search completed but no results found."
        
        else:
            # Generic formatting
            message = result.get('message', 'Request processed successfully')
            return message
            
    except Exception as e:
        print(f"ERROR: Error formatting Strands response: {e}")
        return "Response received from fallback system"


def create_success_response(data, source):
    """Create successful response"""
    
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
            'data': data,
            'source': source,
            'timestamp': datetime.now().isoformat()
        }, default=str)
    }


def create_error_response(message, status_code):
    """Create error response"""
    
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
        },
        'body': json.dumps({
            'success': False,
            'error': message,
            'timestamp': datetime.now().isoformat()
        })
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


# For testing
if __name__ == "__main__":
    test_event = {
        'body': json.dumps({
            'message': 'Find AWS certification deals'
        })
    }
    
    result = lambda_handler(test_event, None)
    print(json.dumps(result, indent=2, default=str))