import json
from datetime import datetime

def handler(event, context):
    """
    Enhanced Bedrock Agent tool for intelligent career path planning
    """
    
    try:
        print(f"Career planner event: {json.dumps(event)}")
        
        # Extract parameters from Bedrock Agent request
        current_role = None
        target_role = None
        experience_level = None
        preferred_cloud = None
        
        # Handle Bedrock Agent format
        if 'requestBody' in event:
            request_body = event['requestBody']
            if 'content' in request_body and 'application/json' in request_body['content']:
                properties = request_body['content']['application/json'].get('properties', [])
                for prop in properties:
                    name = prop.get('name')
                    value = prop.get('value')
                    
                    if name == 'current_role':
                        current_role = value
                    elif name == 'target_role':
                        target_role = value
                    elif name == 'experience_level':
                        experience_level = value
                    elif name == 'preferred_cloud':
                        preferred_cloud = value
        
        # Handle legacy format
        if not any([current_role, target_role, experience_level, preferred_cloud]):
            parameters = event.get('parameters', [])
            for param in parameters:
                name = param.get('name')
                value = param.get('value')
                
                if name == 'current_role':
                    current_role = value
                elif name == 'target_role':
                    target_role = value
                elif name == 'experience_level':
                    experience_level = value
                elif name == 'preferred_cloud':
                    preferred_cloud = value
        
        # Set defaults
        current_role = current_role or 'Developer'
        target_role = target_role or 'Cloud Architect'
        experience_level = experience_level or 'Intermediate'
        preferred_cloud = preferred_cloud or 'AWS'
        
        print(f"Planning path: {current_role} -> {target_role} ({experience_level}, {preferred_cloud})")
        
        # Generate intelligent career path
        career_path = generate_career_path(current_role, target_role, experience_level, preferred_cloud)
        
        # Format response for Bedrock Agent
        response_body = {
            'message': f'Generated career path from {current_role} to {target_role}',
            'career_path': career_path,
            'status': 'success',
            'generated_at': datetime.now().isoformat()
        }
        
        return {
            'messageVersion': '1.0',
            'response': {
                'actionGroup': event.get('actionGroup', 'career_planner'),
                'apiPath': event.get('apiPath', '/plan_path'),
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
        print(f"Error in career_planner handler: {str(e)}")
        return {
            'messageVersion': '1.0',
            'response': {
                'actionGroup': event.get('actionGroup', 'career_planner'),
                'apiPath': event.get('apiPath', '/plan_path'),
                'httpMethod': event.get('httpMethod', 'POST'),
                'httpStatusCode': 500,
                'responseBody': {
                    'application/json': {
                        'body': json.dumps({
                            'error': str(e),
                            'message': 'Career planning failed'
                        })
                    }
                }
            }
        }


def generate_career_path(current_role, target_role, experience_level, preferred_cloud):
    """Generate intelligent career path recommendations"""
    
    # Career progression templates
    career_paths = {
        ('Developer', 'Cloud Architect'): {
            'AWS': {
                'beginner': [
                    'AWS Cloud Practitioner',
                    'AWS Solutions Architect Associate',
                    'AWS Developer Associate',
                    'AWS Solutions Architect Professional'
                ],
                'intermediate': [
                    'AWS Solutions Architect Associate',
                    'AWS Developer Associate',
                    'AWS Solutions Architect Professional'
                ],
                'advanced': [
                    'AWS Solutions Architect Professional',
                    'AWS DevOps Engineer Professional'
                ]
            },
            'AZURE': {
                'beginner': [
                    'Azure Fundamentals (AZ-900)',
                    'Azure Administrator Associate (AZ-104)',
                    'Azure Solutions Architect Expert (AZ-305)'
                ],
                'intermediate': [
                    'Azure Administrator Associate (AZ-104)',
                    'Azure Solutions Architect Expert (AZ-305)'
                ],
                'advanced': [
                    'Azure Solutions Architect Expert (AZ-305)',
                    'Azure DevOps Engineer Expert (AZ-400)'
                ]
            },
            'GCP': {
                'beginner': [
                    'Google Cloud Digital Leader',
                    'Associate Cloud Engineer',
                    'Professional Cloud Architect'
                ],
                'intermediate': [
                    'Associate Cloud Engineer',
                    'Professional Cloud Architect'
                ],
                'advanced': [
                    'Professional Cloud Architect',
                    'Professional DevOps Engineer'
                ]
            }
        },
        ('Developer', 'DevOps Engineer'): {
            'AWS': {
                'beginner': [
                    'AWS Cloud Practitioner',
                    'AWS Developer Associate',
                    'AWS DevOps Engineer Professional'
                ],
                'intermediate': [
                    'AWS Developer Associate',
                    'AWS SysOps Administrator Associate',
                    'AWS DevOps Engineer Professional'
                ],
                'advanced': [
                    'AWS DevOps Engineer Professional',
                    'AWS Security Specialty'
                ]
            }
        },
        ('System Administrator', 'Cloud Engineer'): {
            'AWS': {
                'beginner': [
                    'AWS Cloud Practitioner',
                    'AWS SysOps Administrator Associate',
                    'AWS Solutions Architect Associate'
                ],
                'intermediate': [
                    'AWS SysOps Administrator Associate',
                    'AWS Solutions Architect Associate'
                ],
                'advanced': [
                    'AWS Solutions Architect Professional',
                    'AWS Advanced Networking Specialty'
                ]
            }
        }
    }
    
    # Get specific path or create generic one
    path_key = (current_role, target_role)
    if path_key in career_paths and preferred_cloud in career_paths[path_key]:
        cloud_paths = career_paths[path_key][preferred_cloud]
        certifications = cloud_paths.get(experience_level.lower(), cloud_paths.get('intermediate', []))
    else:
        # Generic path based on cloud provider
        certifications = get_generic_path(preferred_cloud, experience_level)
    
    # Calculate timeline
    timeline = calculate_timeline(certifications, experience_level)
    
    # Generate next steps
    next_steps = generate_next_steps(certifications, current_role, target_role)
    
    # Add learning recommendations
    learning_resources = get_learning_recommendations(preferred_cloud, certifications[0] if certifications else None)
    
    return {
        'current_role': current_role,
        'target_role': target_role,
        'experience_level': experience_level,
        'preferred_cloud': preferred_cloud,
        'recommended_certifications': certifications,
        'estimated_timeline': timeline,
        'next_steps': next_steps,
        'learning_resources': learning_resources,
        'priority_certification': certifications[0] if certifications else None
    }


def get_generic_path(cloud_provider, experience_level):
    """Generate generic certification path for any cloud provider"""
    
    generic_paths = {
        'AWS': {
            'beginner': ['AWS Cloud Practitioner', 'AWS Solutions Architect Associate'],
            'intermediate': ['AWS Solutions Architect Associate', 'AWS Developer Associate'],
            'advanced': ['AWS Solutions Architect Professional', 'AWS DevOps Engineer Professional']
        },
        'AZURE': {
            'beginner': ['Azure Fundamentals (AZ-900)', 'Azure Administrator Associate (AZ-104)'],
            'intermediate': ['Azure Administrator Associate (AZ-104)', 'Azure Solutions Architect Expert (AZ-305)'],
            'advanced': ['Azure Solutions Architect Expert (AZ-305)', 'Azure DevOps Engineer Expert (AZ-400)']
        },
        'GCP': {
            'beginner': ['Google Cloud Digital Leader', 'Associate Cloud Engineer'],
            'intermediate': ['Associate Cloud Engineer', 'Professional Cloud Architect'],
            'advanced': ['Professional Cloud Architect', 'Professional DevOps Engineer']
        },
        'SALESFORCE': {
            'beginner': ['Salesforce Administrator', 'Salesforce Platform App Builder'],
            'intermediate': ['Salesforce Platform Developer I', 'Salesforce Sales Cloud Consultant'],
            'advanced': ['Salesforce Platform Developer II', 'Salesforce Technical Architect']
        },
        'DATABRICKS': {
            'beginner': ['Databricks Certified Data Engineer Associate'],
            'intermediate': ['Databricks Certified Data Engineer Professional', 'Databricks Certified Machine Learning Associate'],
            'advanced': ['Databricks Certified Machine Learning Professional']
        }
    }
    
    return generic_paths.get(cloud_provider, {}).get(experience_level.lower(), [f'{cloud_provider} Fundamentals'])


def calculate_timeline(certifications, experience_level):
    """Calculate estimated timeline for certification path"""
    
    base_time_per_cert = {
        'beginner': 3,  # months
        'intermediate': 2,
        'advanced': 1.5
    }
    
    time_per_cert = base_time_per_cert.get(experience_level.lower(), 2)
    total_months = len(certifications) * time_per_cert
    
    if total_months <= 6:
        return f"{int(total_months)} months"
    elif total_months <= 12:
        return f"{int(total_months)} months (6-12 months)"
    else:
        years = total_months / 12
        return f"{years:.1f} years"


def generate_next_steps(certifications, current_role, target_role):
    """Generate actionable next steps"""
    
    steps = []
    
    if certifications:
        first_cert = certifications[0]
        steps.append(f"Start studying for {first_cert}")
        steps.append(f"Set up hands-on practice environment")
        steps.append(f"Schedule exam for {first_cert}")
        
        if len(certifications) > 1:
            steps.append(f"Plan timeline for {certifications[1]}")
    
    # Role-specific steps
    if 'architect' in target_role.lower():
        steps.append("Gain experience with system design and architecture patterns")
        steps.append("Practice creating technical documentation and diagrams")
    
    if 'devops' in target_role.lower():
        steps.append("Learn CI/CD tools and automation practices")
        steps.append("Gain experience with infrastructure as code")
    
    steps.append(f"Network with professionals in {target_role} roles")
    steps.append("Update LinkedIn profile and resume with new skills")
    
    return steps


def get_learning_recommendations(cloud_provider, priority_cert):
    """Get learning resource recommendations"""
    
    resources = {
        'AWS': [
            "AWS Training and Certification portal",
            "AWS Well-Architected Framework",
            "AWS Hands-on Labs",
            "A Cloud Guru courses"
        ],
        'AZURE': [
            "Microsoft Learn platform",
            "Azure Architecture Center",
            "Azure Hands-on Labs",
            "Pluralsight Azure courses"
        ],
        'GCP': [
            "Google Cloud Skills Boost",
            "Google Cloud Architecture Framework",
            "Qwiklabs hands-on labs",
            "Coursera Google Cloud courses"
        ],
        'SALESFORCE': [
            "Trailhead learning platform",
            "Salesforce Developer Documentation",
            "Trailhead Playground",
            "Salesforce Community Groups"
        ],
        'DATABRICKS': [
            "Databricks Academy",
            "Databricks Documentation",
            "Databricks Community Edition",
            "Apache Spark documentation"
        ]
    }
    
    return resources.get(cloud_provider, [f"{cloud_provider} official documentation"])