#!/usr/bin/env python3
"""
Matcher Lambda function - Minimal implementation
This function is called by the CDK stack but functionality is now handled by strands_agent_lambda
"""

import json
import boto3
from datetime import datetime

def handler(event, context):
    """
    Lambda handler for matcher function
    Note: Main functionality moved to strands_agent_lambda
    """
    
    print("🎯 Matcher function called")
    print(f"Event: {json.dumps(event, default=str)}")
    
    # For now, return success to avoid breaking the deployment
    # In the future, this could be removed or redirect to strands_agent_lambda
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Matcher function called - functionality moved to strands_agent_lambda',
            'timestamp': datetime.now().isoformat(),
            'event': event
        })
    }