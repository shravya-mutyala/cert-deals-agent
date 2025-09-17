import json
import boto3
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import hashlib
import os

dynamodb = boto3.resource('dynamodb')
bedrock = boto3.client('bedrock-runtime')
offers_table = dynamodb.Table(os.environ['OFFERS_TABLE'])

def handler(event, context):
    """Main scraper function - discovers and processes certification offers"""
    
    try:
        # Define target sources
        sources = [
            {
                'name': 'AWS Training',
                'url': 'https://aws.amazon.com/training/events/',
                'provider': 'AWS'
            },
            {
                'name': 'Salesforce Trailhead',
                'url': 'https://trailhead.salesforce.com/en/credentials/certification-vouchers/',
                'provider': 'Salesforce'
            }
        ]
        
        discovered_offers = []
        
        for source in sources:
            print(f"Scraping {source['name']}...")
            offers = scrape_source(source)
            discovered_offers.extend(offers)
        
        # Process offers with Bedrock
        processed_offers = []
        for offer in discovered_offers:
            processed = process_offer_with_ai(offer)
            if processed:
                processed_offers.append(processed)
        
        # Store in DynamoDB
        for offer in processed_offers:
            store_offer(offer)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f'Processed {len(processed_offers)} offers',
                'offers': len(processed_offers)
            })
        }
        
    except Exception as e:
        print(f"Error in scraper: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def scrape_source(source):
    """Scrape a specific source for offers"""
    offers = []
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(source['url'], headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Basic offer detection (customize per provider)
        if source['provider'] == 'AWS':
            offers = extract_aws_offers(soup, source)
        elif source['provider'] == 'Salesforce':
            offers = extract_salesforce_offers(soup, source)
            
    except Exception as e:
        print(f"Error scraping {source['name']}: {str(e)}")
    
    return offers

def extract_aws_offers(soup, source):
    """Extract AWS-specific offers"""
    offers = []
    
    # Look for discount/voucher keywords
    discount_elements = soup.find_all(text=lambda text: text and any(
        keyword in text.lower() for keyword in ['discount', 'voucher', 'free', 'promo']
    ))
    
    for element in discount_elements[:5]:  # Limit for demo
        offer = {
            'provider': source['provider'],
            'source_url': source['url'],
            'raw_text': element.strip(),
            'discovered_at': datetime.utcnow().isoformat()
        }
        offers.append(offer)
    
    return offers

def extract_salesforce_offers(soup, source):
    """Extract Salesforce-specific offers"""
    offers = []
    
    # Similar pattern for Salesforce
    voucher_elements = soup.find_all(text=lambda text: text and 'voucher' in text.lower())
    
    for element in voucher_elements[:3]:
        offer = {
            'provider': source['provider'],
            'source_url': source['url'],
            'raw_text': element.strip(),
            'discovered_at': datetime.utcnow().isoformat()
        }
        offers.append(offer)
    
    return offers

def process_offer_with_ai(offer):
    """Use Bedrock to parse and structure the offer"""
    
    prompt = f"""
    Analyze this certification offer text and extract structured information:
    
    Text: {offer['raw_text']}
    Provider: {offer['provider']}
    
    Extract:
    1. Discount amount/percentage
    2. Eligibility requirements
    3. Expiry date (if mentioned)
    4. Certification type
    5. Geographic restrictions
    6. Confidence score (0-1)
    
    Return as JSON with these fields: discount, eligibility, expiry, cert_type, geo_restrictions, confidence
    """
    
    try:
        response = bedrock.invoke_model(
            modelId='anthropic.claude-3-sonnet-20240229-v1:0',
            body=json.dumps({
                'anthropic_version': 'bedrock-2023-05-31',
                'max_tokens': 1000,
                'messages': [{'role': 'user', 'content': prompt}]
            })
        )
        
        result = json.loads(response['body'].read())
        ai_analysis = result['content'][0]['text']
        
        # Parse JSON from AI response
        try:
            structured_data = json.loads(ai_analysis)
            
            # Create final offer object
            processed_offer = {
                'offer_id': generate_offer_id(offer),
                'provider': offer['provider'],
                'source_url': offer['source_url'],
                'raw_text': offer['raw_text'],
                'discovered_at': offer['discovered_at'],
                'processed_at': datetime.utcnow().isoformat(),
                **structured_data
            }
            
            return processed_offer
            
        except json.JSONDecodeError:
            print(f"Failed to parse AI response as JSON: {ai_analysis}")
            return None
            
    except Exception as e:
        print(f"Error processing offer with AI: {str(e)}")
        return None

def generate_offer_id(offer):
    """Generate unique offer ID"""
    content = f"{offer['provider']}{offer['raw_text']}{offer['source_url']}"
    return hashlib.md5(content.encode()).hexdigest()

def store_offer(offer):
    """Store offer in DynamoDB"""
    try:
        offers_table.put_item(Item=offer)
        print(f"Stored offer: {offer['offer_id']}")
    except Exception as e:
        print(f"Error storing offer: {str(e)}")