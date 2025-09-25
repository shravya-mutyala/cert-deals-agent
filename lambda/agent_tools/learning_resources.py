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
        
        # Extract parameters from the agent request
        parameters = event.get('parameters', [])
        provider = None
        
        # Find the provider parameter
        for param in parameters:
            if param.get('name') == 'provider':
                provider = param.get('value', '').upper()
                break
        
        if not provider:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Provider parameter is required',
                    'message': 'Please specify a provider: AWS, AZURE, GCP, SALESFORCE, or DATABRICKS'
                })
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
                'statusCode': 200,
                'body': json.dumps({
                    'provider': provider,
                    'message': f'No learning resources found for {provider}',
                    'resources': []
                })
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
        
        # Return formatted response for Bedrock Agent
        return {
            'statusCode': 200,
            'body': json.dumps({
                'provider': provider,
                'message': f'Found {len(resources)} learning resources for {provider}',
                'resources': formatted_resources,
                'count': len(resources)
            })
        }
        
    except Exception as e:
        print(f"Error in learning_resources handler: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'message': 'Failed to retrieve learning resources'
            })
        }