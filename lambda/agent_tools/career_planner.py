import json
import boto3
from datetime import datetime

def handler(event, context):
    """
    Bedrock Agent tool for AI-powered career planning
    """
    
    try:
        # Parse request body from agent
        request_body = event.get('requestBody', {})
        content = request_body.get('content', {})
        application_json = content.get('application/json', {})
        
        # Extract career planning parameters
        current_role = application_json.get('current_role', 'Developer')
        target_role = application_json.get('target_role', 'Cloud Architect')
        experience_level = application_json.get('experience_level', 'Intermediate')
        preferred_cloud = application_json.get('preferred_cloud', 'AWS')
        
        # Generate career path using AI
        career_path = generate_career_path(current_role, target_role, experience_level, preferred_cloud)
        
        return {
            'messageVersion': '1.0',
            'response': {
                'actionGroup': event['actionGroup'],
                'function': event['function'],
                'functionResponse': {
                    'responseBody': {
                        'TEXT': {
                            'body': json.dumps(career_path)
                        }
                    }
                }
            }
        }
        
    except Exception as e:
        return {
            'messageVersion': '1.0',
            'response': {
                'actionGroup': event['actionGroup'],
                'function': event['function'],
                'functionResponse': {
                    'responseBody': {
                        'TEXT': {
                            'body': json.dumps({
                                'error': str(e),
                                'career_path': []
                            })
                        }
                    }
                }
            }
        }

def generate_career_path(current_role, target_role, experience_level, preferred_cloud):
    """Generate AI-powered career path recommendations"""
    
    bedrock = boto3.client('bedrock-runtime')
    
    prompt = f"""
    You are an expert career advisor for IT professionals. Create a detailed certification roadmap.
    
    Current Role: {current_role}
    Target Role: {target_role}
    Experience Level: {experience_level}
    Preferred Cloud: {preferred_cloud}
    
    Create a step-by-step certification path that includes:
    1. Foundation certifications (if needed)
    2. Intermediate certifications
    3. Advanced/Professional certifications
    4. Specialty certifications
    5. Timeline estimates
    6. Prerequisites for each cert
    7. Career impact of each certification
    8. Estimated costs and potential savings opportunities
    
    Consider multiple cloud providers if beneficial for the career path.
    
    Return as JSON with this structure:
    {{
        "career_summary": "Brief overview of the recommended path",
        "timeline_months": "Total estimated timeline",
        "certifications": [
            {{
                "name": "Certification name",
                "provider": "AWS/Azure/GCP/etc",
                "level": "Foundation/Associate/Professional/Expert",
                "priority": "High/Medium/Low",
                "timeline_months": "Time to complete",
                "prerequisites": ["List of prerequisites"],
                "career_impact": "How this helps career progression",
                "estimated_cost": "Exam cost estimate",
                "why_important": "Explanation of value"
            }}
        ],
        "learning_path": [
            {{
                "phase": "Phase name",
                "duration_months": "Duration",
                "focus_areas": ["Key skills to develop"],
                "certifications_in_phase": ["Certs to pursue"]
            }}
        ],
        "cost_optimization": {{
            "total_estimated_cost": "Total cost estimate",
            "savings_opportunities": ["Ways to save money"],
            "roi_timeline": "When investment pays off"
        }}
    }}
    """
    
    try:
        response = bedrock.invoke_model(
            modelId='anthropic.claude-3-sonnet-20240229-v1:0',
            body=json.dumps({
                'anthropic_version': 'bedrock-2023-05-31',
                'max_tokens': 2000,
                'messages': [{'role': 'user', 'content': prompt}]
            })
        )
        
        result = json.loads(response['body'].read())
        ai_response = result['content'][0]['text']
        
        try:
            career_path = json.loads(ai_response)
            
            # Add metadata
            career_path['generated_at'] = datetime.utcnow().isoformat()
            career_path['input_parameters'] = {
                'current_role': current_role,
                'target_role': target_role,
                'experience_level': experience_level,
                'preferred_cloud': preferred_cloud
            }
            
            return career_path
            
        except json.JSONDecodeError:
            # Fallback if AI doesn't return valid JSON
            return create_fallback_career_path(current_role, target_role, preferred_cloud)
            
    except Exception as e:
        print(f"Error generating career path: {e}")
        return create_fallback_career_path(current_role, target_role, preferred_cloud)

def create_fallback_career_path(current_role, target_role, preferred_cloud):
    """Create a basic career path if AI fails"""
    
    # Basic certification paths by cloud provider
    cert_paths = {
        'AWS': [
            {'name': 'AWS Cloud Practitioner', 'level': 'Foundation', 'cost': '$100'},
            {'name': 'AWS Solutions Architect Associate', 'level': 'Associate', 'cost': '$150'},
            {'name': 'AWS Solutions Architect Professional', 'level': 'Professional', 'cost': '$300'}
        ],
        'Azure': [
            {'name': 'Azure Fundamentals (AZ-900)', 'level': 'Foundation', 'cost': '$99'},
            {'name': 'Azure Administrator (AZ-104)', 'level': 'Associate', 'cost': '$165'},
            {'name': 'Azure Solutions Architect (AZ-305)', 'level': 'Professional', 'cost': '$165'}
        ],
        'Google Cloud': [
            {'name': 'Cloud Digital Leader', 'level': 'Foundation', 'cost': '$99'},
            {'name': 'Associate Cloud Engineer', 'level': 'Associate', 'cost': '$125'},
            {'name': 'Professional Cloud Architect', 'level': 'Professional', 'cost': '$200'}
        ]
    }
    
    certs = cert_paths.get(preferred_cloud, cert_paths['AWS'])
    
    return {
        'career_summary': f"Recommended path from {current_role} to {target_role} using {preferred_cloud}",
        'timeline_months': '12-18',
        'certifications': certs,
        'learning_path': [
            {
                'phase': 'Foundation',
                'duration_months': '3-4',
                'focus_areas': ['Cloud basics', 'Core services'],
                'certifications_in_phase': [certs[0]['name']]
            },
            {
                'phase': 'Specialization', 
                'duration_months': '6-8',
                'focus_areas': ['Architecture', 'Best practices'],
                'certifications_in_phase': [certs[1]['name']]
            },
            {
                'phase': 'Mastery',
                'duration_months': '6-12',
                'focus_areas': ['Advanced architecture', 'Leadership'],
                'certifications_in_phase': [certs[2]['name']]
            }
        ],
        'cost_optimization': {
            'total_estimated_cost': '$400-600',
            'savings_opportunities': ['Student discounts', 'Employer sponsorship', 'Voucher programs'],
            'roi_timeline': '6-12 months after completion'
        },
        'generated_at': datetime.utcnow().isoformat(),
        'fallback_used': True
    }