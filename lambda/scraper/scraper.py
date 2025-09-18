import json
import boto3
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone
from decimal import Decimal
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
            },

            {
                'name': 'Google Cloud Training',
                'url': 'https://cloud.google.com/training/certification',
                'provider': 'Google Cloud'
            },
            {
                'name': 'Databricks Academy',
                'url': 'https://www.databricks.com/learn/certification',
                'provider': 'Databricks'
            },
            {
                'name': 'Azure Fundamentals',
                'url': 'https://azure.microsoft.com/en-us/certifications/',
                'provider': 'Azure'
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

        elif source['provider'] == 'Google Cloud':
            offers = extract_gcp_offers(soup, source)
        elif source['provider'] == 'Databricks':
            offers = extract_databricks_offers(soup, source)
        elif source['provider'] == 'Azure':
            offers = extract_azure_offers(soup, source)
            
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
            'discovered_at': datetime.now(timezone.utc).isoformat()
        }
        offers.append(offer)
    
    return offers

def extract_salesforce_offers(soup, source):
    """Extract Salesforce-specific offers"""
    offers = []
    
    # Look for voucher and discount keywords
    voucher_elements = soup.find_all(text=lambda text: text and any(
        keyword in text.lower() for keyword in ['voucher', 'discount', 'free', 'promo', 'trailhead']
    ))
    
    for element in voucher_elements[:3]:
        offer = {
            'provider': source['provider'],
            'source_url': source['url'],
            'raw_text': element.strip(),
            'discovered_at': datetime.now(timezone.utc).isoformat()
        }
        offers.append(offer)
    
    return offers



def extract_gcp_offers(soup, source):
    """Extract Google Cloud certification offers"""
    offers = []
    
    # Look for GCP-specific keywords
    gcp_elements = soup.find_all(text=lambda text: text and any(
        keyword in text.lower() for keyword in [
            'discount', 'free', 'voucher', 'credit', 'promo', 'student',
            'associate', 'professional', 'cloud', 'google'
        ]
    ))
    
    for element in gcp_elements[:4]:
        offer = {
            'provider': source['provider'],
            'source_url': source['url'],
            'raw_text': element.strip(),
            'discovered_at': datetime.now(timezone.utc).isoformat()
        }
        offers.append(offer)
    
    return offers

def extract_databricks_offers(soup, source):
    """Extract Databricks certification offers"""
    offers = []
    
    # Look for Databricks-specific keywords
    databricks_elements = soup.find_all(text=lambda text: text and any(
        keyword in text.lower() for keyword in [
            'discount', 'free', 'voucher', 'promo', 'student', 'academy',
            'associate', 'professional', 'data engineer', 'data scientist',
            'machine learning', 'spark', 'lakehouse'
        ]
    ))
    
    for element in databricks_elements[:3]:
        offer = {
            'provider': source['provider'],
            'source_url': source['url'],
            'raw_text': element.strip(),
            'discovered_at': datetime.now(timezone.utc).isoformat()
        }
        offers.append(offer)
    
    return offers

def extract_azure_offers(soup, source):
    """Extract Azure certification offers"""
    offers = []
    
    # Look for Azure-specific keywords
    azure_elements = soup.find_all(text=lambda text: text and any(
        keyword in text.lower() for keyword in [
            'discount', 'free', 'voucher', 'promo', 'student', 'azure',
            'fundamentals', 'associate', 'expert', 'specialty',
            'administrator', 'developer', 'architect', 'security'
        ]
    ))
    
    for element in azure_elements[:4]:
        offer = {
            'provider': source['provider'],
            'source_url': source['url'],
            'raw_text': element.strip(),
            'discovered_at': datetime.now(timezone.utc).isoformat()
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
    1. Discount amount/percentage (e.g., "50% off", "Free", "$100 credit")
    2. Eligibility requirements (e.g., "Students", "First-time test takers", "Employees")
    3. Expiry date (if mentioned, format as YYYY-MM-DD)
    4. Certification type/level (e.g., "Fundamentals", "Associate", "Professional", "Expert")
    5. Specific certification name (e.g., "AWS Solutions Architect", "Azure Administrator", "GCP Professional Cloud Architect")
    6. Geographic restrictions (e.g., "Global", "US only", "EU residents")
    7. Confidence score (0-1, how confident you are in the extraction)
    
    Provider-specific context:
    - AWS: Look for Solutions Architect, Developer, SysOps, Security, Data Analytics, Machine Learning
    - Microsoft/Azure: Look for Fundamentals (AZ-900), Administrator (AZ-104), Developer (AZ-204), Architect (AZ-305)
    - Google Cloud: Look for Associate Cloud Engineer, Professional Cloud Architect, Professional Data Engineer
    - Salesforce: Look for Administrator, Platform Developer, Sales Cloud, Service Cloud
    - Databricks: Look for Data Engineer Associate/Professional, Data Scientist Associate/Professional
    
    Return as JSON with these fields: discount, eligibility, expiry, cert_type, cert_name, geo_restrictions, confidence
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
            
            # Convert float values to Decimal for DynamoDB
            if 'confidence' in structured_data and isinstance(structured_data['confidence'], (int, float)):
                structured_data['confidence'] = Decimal(str(structured_data['confidence']))
            
            # Create final offer object
            processed_offer = {
                'offer_id': generate_offer_id(offer),
                'provider': offer['provider'],
                'source_url': offer['source_url'],
                'raw_text': offer['raw_text'],
                'discovered_at': offer['discovered_at'],
                'processed_at': datetime.now(timezone.utc).isoformat(),
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