import json

def handler(event, context):
    """
    Bedrock Agent tool for career path planning
    """
    
    try:
        print(f"Career planner event: {json.dumps(event)}")
        
        # Extract parameters from request body
        body = event.get('requestBody', {})
        if isinstance(body, str):
            body = json.loads(body)
        
        current_role = body.get('current_role', 'Developer')
        target_role = body.get('target_role', 'Cloud Architect')
        experience_level = body.get('experience_level', 'Intermediate')
        preferred_cloud = body.get('preferred_cloud', 'AWS')
        
        # Placeholder career path logic
        career_path = {
            'current_role': current_role,
            'target_role': target_role,
            'recommended_certifications': [
                f'{preferred_cloud} Cloud Practitioner',
                f'{preferred_cloud} Solutions Architect Associate',
                f'{preferred_cloud} Solutions Architect Professional'
            ],
            'estimated_timeline': '6-12 months',
            'next_steps': [
                'Start with fundamentals certification',
                'Gain hands-on experience',
                'Progress to associate level',
                'Advance to professional level'
            ]
        }
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f'Career path from {current_role} to {target_role}',
                'career_path': career_path,
                'status': 'success'
            })
        }
        
    except Exception as e:
        print(f"Error in career_planner handler: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'message': 'Career planning failed'
            })
        }