import json
import boto3
import os
from boto3.dynamodb.conditions import Key

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')
table_name = os.environ['LEARNING_RESOURCES_TABLE']
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    """
    Lambda function to retrieve learning resources from DynamoDB
    Supports filtering by provider and returning formatted resources
    """
    
    try:
        # Parse query parameters
        query_params = event.get('queryStringParameters') or {}
        provider = query_params.get('provider', '').upper()
        
        # CORS headers
        headers = {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'GET,OPTIONS'
        }
        
        # Handle OPTIONS request for CORS
        if event.get('httpMethod') == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({'message': 'CORS preflight'})
            }
        
        # If specific provider requested
        if provider and provider in ['AWS', 'AZURE', 'GCP', 'SALESFORCE', 'DATABRICKS']:
            response = table.query(
                KeyConditionExpression=Key('provider').eq(provider)
            )
            resources = response.get('Items', [])
        else:
            # Get all resources
            response = table.scan()
            resources = response.get('Items', [])
        
        # Format response
        formatted_resources = format_resources_response(resources, provider)
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'success': True,
                'provider': provider or 'ALL',
                'resources': formatted_resources,
                'count': len(resources)
            })
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'success': False,
                'error': str(e),
                'message': 'Failed to retrieve learning resources'
            })
        }

def format_resources_response(resources, provider=None):
    """Format resources for frontend consumption"""
    
    if not resources:
        return []
    
    # Group by provider
    grouped = {}
    for resource in resources:
        prov = resource['provider']
        if prov not in grouped:
            grouped[prov] = []
        grouped[prov].append({
            'name': resource['name'],
            'url': resource['url'],
            'description': resource['description'],
            'category': resource.get('category', 'General')
        })
    
    # If specific provider requested, return just that provider's resources
    if provider and provider in grouped:
        return [{
            'provider': provider,
            'resources': grouped[provider]
        }]
    
    # Return all providers
    result = []
    for prov, res_list in grouped.items():
        result.append({
            'provider': prov,
            'resources': res_list
        })
    
    return result