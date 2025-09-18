import json
import boto3
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone

def handler(event, context):
    """
    Bedrock Agent tool for autonomous web discovery
    """
    
    try:
        # Parse agent input
        agent_input = event.get('inputText', '')
        parameters = event.get('parameters', [])
        
        # Extract providers from parameters
        providers = []
        for param in parameters:
            if param.get('name') == 'providers':
                providers = param.get('value', [])
        
        if not providers:
            providers = ['AWS', 'Azure', 'Google Cloud', 'Databricks', 'Salesforce']
        
        # Discover deals from each provider
        discovered_deals = []
        
        for provider in providers:
            deals = discover_provider_deals(provider)
            discovered_deals.extend(deals)
        
        # Analyze and rank deals using AI
        analyzed_deals = analyze_deals_with_ai(discovered_deals)
        
        # Return response in Bedrock Agent format
        return {
            'messageVersion': '1.0',
            'response': {
                'actionGroup': event['actionGroup'],
                'function': event['function'],
                'functionResponse': {
                    'responseBody': {
                        'TEXT': {
                            'body': json.dumps({
                                'deals_found': len(analyzed_deals),
                                'deals': analyzed_deals[:10],  # Top 10
                                'summary': f"Discovered {len(analyzed_deals)} certification deals across {len(providers)} providers",
                                'recommendations': generate_recommendations(analyzed_deals)
                            })
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
                                'deals_found': 0
                            })
                        }
                    }
                }
            }
        }

def discover_provider_deals(provider):
    """Discover deals from a specific provider"""
    
    provider_urls = {
        'AWS': 'https://aws.amazon.com/training/events/',
        'Azure': 'https://azure.microsoft.com/en-us/certifications/',
        'Google Cloud': 'https://cloud.google.com/training/certification',
        'Databricks': 'https://www.databricks.com/learn/certification',
        'Salesforce': 'https://trailhead.salesforce.com/en/credentials/certification-vouchers/'
    }
    
    url = provider_urls.get(provider)
    if not url:
        return []
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for deal-related content
        deal_keywords = ['discount', 'voucher', 'free', 'promo', 'offer', 'save', '%']
        
        deals = []
        for keyword in deal_keywords:
            elements = soup.find_all(text=lambda text: text and keyword in text.lower())
            
            for element in elements[:3]:  # Limit per keyword
                deal = {
                    'provider': provider,
                    'raw_text': element.strip(),
                    'source_url': url,
                    'discovered_at': datetime.now(timezone.utc).isoformat(),
                    'keyword_matched': keyword
                }
                deals.append(deal)
        
        return deals
        
    except Exception as e:
        print(f"Error discovering deals for {provider}: {e}")
        return []

def analyze_deals_with_ai(deals):
    """Use Bedrock to analyze and structure deals"""
    
    if not deals:
        return []
    
    bedrock = boto3.client('bedrock-runtime')
    analyzed_deals = []
    
    for deal in deals:
        try:
            prompt = f"""
            Analyze this certification deal and extract key information:
            
            Provider: {deal['provider']}
            Text: {deal['raw_text']}
            
            Extract and return JSON with:
            1. discount_amount: The discount percentage or amount
            2. certification_type: What certification this applies to
            3. eligibility: Who can use this deal
            4. expiry_info: When it expires (if mentioned)
            5. confidence_score: How confident you are (0-1)
            6. deal_quality: Rate the deal quality (poor/good/excellent)
            7. action_required: What user needs to do to get this deal
            
            Return only valid JSON.
            """
            
            response = bedrock.invoke_model(
                modelId='anthropic.claude-3-sonnet-20240229-v1:0',
                body=json.dumps({
                    'anthropic_version': 'bedrock-2023-05-31',
                    'max_tokens': 500,
                    'messages': [{'role': 'user', 'content': prompt}]
                })
            )
            
            result = json.loads(response['body'].read())
            ai_analysis = result['content'][0]['text']
            
            try:
                structured_deal = json.loads(ai_analysis)
                structured_deal.update(deal)  # Add original data
                analyzed_deals.append(structured_deal)
            except json.JSONDecodeError:
                # Fallback if AI doesn't return valid JSON
                deal['confidence_score'] = 0.3
                deal['deal_quality'] = 'unknown'
                analyzed_deals.append(deal)
                
        except Exception as e:
            print(f"Error analyzing deal: {e}")
            deal['confidence_score'] = 0.1
            analyzed_deals.append(deal)
    
    # Sort by confidence and quality
    analyzed_deals.sort(key=lambda x: x.get('confidence_score', 0), reverse=True)
    return analyzed_deals

def generate_recommendations(deals):
    """Generate AI recommendations based on discovered deals"""
    
    if not deals:
        return "No deals found at this time. Check back later for new opportunities."
    
    high_quality_deals = [d for d in deals if d.get('deal_quality') == 'excellent']
    expiring_soon = [d for d in deals if 'expir' in d.get('raw_text', '').lower()]
    
    recommendations = []
    
    if high_quality_deals:
        recommendations.append(f"Found {len(high_quality_deals)} excellent deals - act quickly!")
    
    if expiring_soon:
        recommendations.append(f"{len(expiring_soon)} deals may be expiring soon - check expiry dates")
    
    provider_counts = {}
    for deal in deals:
        provider = deal.get('provider', 'Unknown')
        provider_counts[provider] = provider_counts.get(provider, 0) + 1
    
    best_provider = max(provider_counts, key=provider_counts.get)
    recommendations.append(f"{best_provider} has the most active deals ({provider_counts[best_provider]})")
    
    return "; ".join(recommendations)