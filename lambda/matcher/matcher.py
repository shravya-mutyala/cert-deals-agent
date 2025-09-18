import json
import boto3
import os
from datetime import datetime, timezone
from decimal import Decimal
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
bedrock = boto3.client('bedrock-runtime')
offers_table = dynamodb.Table(os.environ['OFFERS_TABLE'])
users_table = dynamodb.Table(os.environ['USERS_TABLE'])

def handler(event, context):
    """Handle API requests for offer matching and user management"""
    
    try:
        http_method = event['httpMethod']
        path = event['path']
        
        if path == '/offers' and http_method == 'GET':
            return get_matched_offers(event)
        elif path == '/users' and http_method == 'POST':
            return create_or_update_user(event)
        else:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Endpoint not found'})
            }
            
    except Exception as e:
        print(f"Error in matcher: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def get_matched_offers(event):
    """Get offers matched to user profile"""
    
    # Get user_id from query parameters
    user_id = event.get('queryStringParameters', {}).get('user_id')
    if not user_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'user_id required'})
        }
    
    try:
        # Get user profile
        user_response = users_table.get_item(Key={'user_id': user_id})
        if 'Item' not in user_response:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'User not found'})
            }
        
        user_profile = user_response['Item']
        
        # Get all active offers
        offers_response = offers_table.scan()
        offers = offers_response['Items']
        
        # Match offers to user
        matched_offers = []
        for offer in offers:
            match_result = match_offer_to_user(offer, user_profile)
            if match_result['is_match']:
                matched_offers.append({
                    **offer,
                    'match_score': match_result['score'],
                    'match_reasons': match_result['reasons']
                })
        
        # Sort by match score
        matched_offers.sort(key=lambda x: x['match_score'], reverse=True)
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'user_id': user_id,
                'matched_offers': matched_offers[:10],  # Top 10
                'total_matches': len(matched_offers)
            })
        }
        
    except Exception as e:
        print(f"Error getting matched offers: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def create_or_update_user(event):
    """Create or update user profile"""
    
    try:
        body = json.loads(event['body'])
        user_id = body.get('user_id')
        
        if not user_id:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'user_id required'})
            }
        
        # Create user profile
        user_profile = {
            'user_id': user_id,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat(),
            'location': body.get('location', ''),
            'student_status': body.get('student_status', False),
            'current_certifications': body.get('current_certifications', []),
            'target_certifications': body.get('target_certifications', []),
            'preferred_providers': body.get('preferred_providers', []),
            'notification_preferences': body.get('notification_preferences', {
                'email': True,
                'days_before_expiry': 7
            })
        }
        
        # Store in DynamoDB
        users_table.put_item(Item=user_profile)
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'message': 'User profile saved',
                'user_id': user_id
            })
        }
        
    except Exception as e:
        print(f"Error creating user: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def match_offer_to_user(offer, user_profile):
    """Use AI to match offer to user profile"""
    
    prompt = f"""
    Determine if this certification offer matches the user profile:
    
    OFFER:
    Provider: {offer.get('provider')}
    Discount: {offer.get('discount')}
    Eligibility: {offer.get('eligibility')}
    Certification Type: {offer.get('cert_type')}
    Geographic Restrictions: {offer.get('geo_restrictions')}
    
    USER PROFILE:
    Location: {user_profile.get('location')}
    Student Status: {user_profile.get('student_status')}
    Current Certifications: {user_profile.get('current_certifications')}
    Target Certifications: {user_profile.get('target_certifications')}
    Preferred Providers: {user_profile.get('preferred_providers')}
    
    Analyze:
    1. Does the user meet eligibility requirements?
    2. Is the certification relevant to their targets?
    3. Are there geographic restrictions?
    4. What's the match confidence (0-1)?
    5. Why does this match or not match?
    
    Return JSON: {{"is_match": boolean, "score": float, "reasons": [list of strings]}}
    """
    
    try:
        response = bedrock.invoke_model(
            modelId='anthropic.claude-3-sonnet-20240229-v1:0',
            body=json.dumps({
                'anthropic_version': 'bedrock-2023-05-31',
                'max_tokens': 500,
                'messages': [{'role': 'user', 'content': prompt}]
            })
        )
        
        result = json.loads(response['body'].read())
        ai_response = result['content'][0]['text']
        
        # Parse JSON response
        try:
            match_result = json.loads(ai_response)
            return match_result
        except json.JSONDecodeError:
            # Fallback to basic matching
            return basic_match(offer, user_profile)
            
    except Exception as e:
        print(f"Error in AI matching: {str(e)}")
        return basic_match(offer, user_profile)

def basic_match(offer, user_profile):
    """Fallback basic matching logic"""
    score = 0.5
    reasons = []
    
    # Check provider preference
    if offer.get('provider') in user_profile.get('preferred_providers', []):
        score += 0.3
        reasons.append(f"Preferred provider: {offer.get('provider')}")
    
    # Check certification relevance
    target_certs = user_profile.get('target_certifications', [])
    if any(cert.lower() in offer.get('cert_type', '').lower() for cert in target_certs):
        score += 0.4
        reasons.append("Matches target certification")
    
    return {
        'is_match': score > 0.6,
        'score': min(score, 1.0),
        'reasons': reasons
    }