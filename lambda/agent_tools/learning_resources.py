import json
import boto3
import os
from boto3.dynamodb.conditions import Key

def handler(event, context):
    """
    Bedrock Agent tool to retrieve learning resources from DynamoDB
    This function is called when the agent needs to get learning resources
    """
    
    try:
        # Parse the event from Bedrock Agent
        print(f"Received event: {json.dumps(event)}")
        
        # Extract parameters from Bedrock Agent request
        provider = None
        
        # Handle Bedrock Agent format
        if 'requestBody' in event:
            request_body = event['requestBody']
            if 'content' in request_body and 'application/json' in request_body['content']:
                properties = request_body['content']['application/json'].get('properties', [])
                for prop in properties:
                    if prop.get('name') == 'provider':
                        provider = prop.get('value', '').upper()
                        break
        
        # Handle legacy format
        if not provider:
            parameters = event.get('parameters', [])
            for param in parameters:
                if param.get('name') == 'provider':
                    provider = param.get('value', '').upper()
                    break
        
        if not provider:
            return {
                'messageVersion': '1.0',
                'response': {
                    'actionGroup': event.get('actionGroup', 'learning_resources'),
                    'apiPath': event.get('apiPath', '/get_resources'),
                    'httpMethod': event.get('httpMethod', 'POST'),
                    'httpStatusCode': 400,
                    'responseBody': {
                        'application/json': {
                            'body': json.dumps({
                                'error': 'Provider parameter is required',
                                'message': 'Please specify a provider: AWS, AZURE, GCP, SALESFORCE, or DATABRICKS'
                            })
                        }
                    }
                }
            }
        
        # Initialize DynamoDB
        dynamodb = boto3.resource('dynamodb')
        table_name = 'learning-resources'
        table = dynamodb.Table(table_name)
        
        # Query resources for the specified provider
        response = table.query(
            KeyConditionExpression=Key('provider').eq(provider)
        )
        
        resources = response.get('Items', [])
        
        if not resources:
            return {
                'messageVersion': '1.0',
                'response': {
                    'actionGroup': event.get('actionGroup', 'learning_resources'),
                    'apiPath': event.get('apiPath', '/get_resources'),
                    'httpMethod': event.get('httpMethod', 'POST'),
                    'httpStatusCode': 200,
                    'responseBody': {
                        'application/json': {
                            'body': json.dumps({
                                'provider': provider,
                                'message': f'No learning resources found for {provider}',
                                'resources': []
                            })
                        }
                    }
                }
            }
        
        # Format resources for the agent
        formatted_resources = []
        for resource in resources:
            formatted_resources.append({
                'name': resource['name'],
                'url': resource['url'],
                'description': resource['description'],
                'category': resource.get('category', 'General')
            })
        
        # Format response for Bedrock Agent
        response_body = {
            'provider': provider,
            'message': f'Found {len(resources)} learning resources for {provider}',
            'resources': formatted_resources,
            'count': len(resources)
        }
        
        return {
            'messageVersion': '1.0',
            'response': {
                'actionGroup': event.get('actionGroup', 'learning_resources'),
                'apiPath': event.get('apiPath', '/get_resources'),
                'httpMethod': event.get('httpMethod', 'POST'),
                'httpStatusCode': 200,
                'responseBody': {
                    'application/json': {
                        'body': json.dumps(response_body)
                    }
                }
            }
        }
        
    except Exception as e:
        print(f"Error in learning_resources handler: {str(e)}")
        return {
            'messageVersion': '1.0',
            'response': {
                'actionGroup': event.get('actionGroup', 'learning_resources'),
                'apiPath': event.get('apiPath', '/get_resources'),
                'httpMethod': event.get('httpMethod', 'POST'),
                'httpStatusCode': 500,
                'responseBody': {
                    'application/json': {
                        'body': json.dumps({
                            'error': str(e),
                            'message': 'Failed to retrieve learning resources'
                        })
                    }
                }
            }
        }