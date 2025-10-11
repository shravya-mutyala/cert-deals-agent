import json
import boto3
import requests
from datetime import datetime, timedelta
import re
from urllib.parse import urljoin, urlparse
import time
import os

def handler(event, context):
    """
    Enhanced Bedrock Agent tool for intelligent certification deal discovery
    Finds official deals, challenges, and promotions from certification providers
    """
    
    try:
        print(f"Certification deal discovery event: {json.dumps(event)}")
        
        # Extract parameters from Bedrock Agent request
        providers = []
        
        # Handle Bedrock Agent format
        if 'requestBody' in event:
            request_body = event['requestBody']
            if 'content' in request_body and 'application/json' in request_body['content']:
                properties = request_body['content']['application/json'].get('properties', [])
                for prop in properties:
                    if prop.get('name') == 'providers':
                        value = prop.get('value', '[]')
                        if isinstance(value, str):
                            # Parse string representation of array
                            import ast
                            try:
                                providers = ast.literal_eval(value)
                            except:
                                providers = [value] if value else []
                        else:
                            providers = value if isinstance(value, list) else [value]
                        break
        
        # Handle legacy format
        if not providers:
            parameters = event.get('parameters', [])
            for param in parameters:
                if param.get('name') == 'providers':
                    providers = param.get('value', [])
                    if isinstance(providers, str):
                        providers = [providers]
                    break
        
        # Default providers if none specified
        if not providers:
            providers = ['AWS', 'AZURE', 'GCP', 'SALESFORCE', 'DATABRICKS']
        
        print(f"Discovering deals for providers: {providers}")
        
        # Discover deals for each provider
        all_deals = []
        for provider in providers:
            provider_deals = discover_provider_deals(provider.upper())
            all_deals.extend(provider_deals)
        
        # Sort by confidence score
        all_deals.sort(key=lambda x: x.get('confidence_score', 0), reverse=True)
        
        # Format response for Bedrock Agent
        response_body = {
            'message': f'Discovered {len(all_deals)} certification deals and challenges',
            'deals': all_deals[:10],  # Return top 10 deals
            'providers_searched': providers,
            'total_found': len(all_deals)
        }
        
        return {
            'messageVersion': '1.0',
            'response': {
                'actionGroup': event.get('actionGroup', 'web_discovery'),
                'apiPath': event.get('apiPath', '/discover_deals'),
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
        print(f"Error in web_discovery handler: {str(e)}")
        return {
            'messageVersion': '1.0',
            'response': {
                'actionGroup': event.get('actionGroup', 'web_discovery'),
                'apiPath': event.get('apiPath', '/discover_deals'),
                'httpMethod': event.get('httpMethod', 'POST'),
                'httpStatusCode': 500,
                'responseBody': {
                    'application/json': {
                        'body': json.dumps({
                            'error': str(e),
                            'message': 'Web discovery failed'
                        })
                    }
                }
            }
        }


def discover_provider_deals(provider):
    """Discover deals for a specific provider using Google Custom Search"""
    deals = []
    
    try:
        # Get search API credentials
        api_key = os.environ.get('GOOGLE_SEARCH_API_KEY')
        search_engine_id = os.environ.get('GOOGLE_SEARCH_ENGINE_ID')
        
        if not api_key or not search_engine_id:
            print(f"WARNING: Google Search API credentials not configured")
            return []
        
        # Provider-specific search queries for deals and challenges
        search_queries = get_provider_search_queries(provider)
        
        for query in search_queries:
            try:
                print(f"Searching for: {query}")
                
                # Make Google Custom Search API request
                url = "https://www.googleapis.com/customsearch/v1"
                params = {
                    'key': api_key,
                    'cx': search_engine_id,
                    'q': query,
                    'num': 5,  # Limit results per query
                    'dateRestrict': 'y1'  # Last year only
                }
                
                response = requests.get(url, params=params, timeout=10)
                
                if response.status_code == 200:
                    search_results = response.json()
                    query_deals = format_search_results(search_results, provider, query)
                    deals.extend(query_deals)
                else:
                    print(f"Search API error: {response.status_code}")
                
                # Rate limiting
                time.sleep(0.5)
                
            except Exception as e:
                print(f"Error searching for query '{query}': {e}")
                continue
    
    except Exception as e:
        print(f"Error discovering deals for {provider}: {e}")
    
    return deals


def get_provider_search_queries(provider):
    """Get provider-specific search queries for deals and challenges"""
    
    current_year = datetime.now().year
    next_year = current_year + 1
    
    queries = {
        'AWS': [
            f"AWS certification challenge {current_year} discount voucher",
            f"AWS AI Practitioner certification deal {current_year}",
            f"AWS certification promotion {current_year} free voucher",
            f"AWS re:Invent certification challenge {current_year}",
            f"AWS certification discount code {current_year}",
            f"site:aws.amazon.com certification challenge {current_year}",
            f"site:pages.awscloud.com certification challenge {current_year}"
        ],
        'AZURE': [
            f"Microsoft Azure certification challenge {current_year} voucher",
            f"Azure certification discount {current_year} free exam",
            f"Microsoft Ignite certification challenge {current_year}",
            f"Azure certification promotion {current_year}",
            f"site:learn.microsoft.com certification challenge {current_year}",
            f"Microsoft certification discount code {current_year}"
        ],
        'GCP': [
            f"Google Cloud certification challenge {current_year} voucher",
            f"GCP certification discount {current_year} free exam",
            f"Google Cloud Next certification challenge {current_year}",
            f"site:cloud.google.com certification challenge {current_year}",
            f"Google Cloud certification promotion {current_year}"
        ],
        'SALESFORCE': [
            f"Salesforce certification challenge {current_year} voucher",
            f"Trailhead certification discount {current_year}",
            f"Salesforce certification promotion {current_year}",
            f"site:trailhead.salesforce.com certification challenge {current_year}",
            f"Dreamforce certification challenge {current_year}"
        ],
        'DATABRICKS': [
            f"Databricks certification challenge {current_year} voucher",
            f"Databricks certification discount {current_year}",
            f"site:databricks.com certification challenge {current_year}",
            f"Databricks certification promotion {current_year}"
        ]
    }
    
    return queries.get(provider, [f"{provider} certification challenge {current_year}"])


def format_search_results(search_results, provider, query):
    """Format Google search results into deal objects"""
    deals = []
    
    items = search_results.get('items', [])
    
    for item in items:
        try:
            title = item.get('title', '')
            snippet = item.get('snippet', '')
            link = item.get('link', '')
            
            # Skip if no deal indicators
            if not has_deal_indicators(title, snippet):
                continue
            
            # Extract deal information
            deal = {
                'offer_id': f"bedrock_{provider.lower()}_{hash(link) % 10000}",
                'provider': provider,
                'certification_name': extract_certification_name(title, snippet, provider),
                'title': title,
                'description': snippet,
                'source_url': link,
                'source_name': extract_source_name(link),
                'discount_type': extract_discount_type(title, snippet),
                'eligibility': extract_eligibility(title, snippet),
                'confidence_score': calculate_confidence_score(title, snippet, link, provider),
                'discovered_at': datetime.now().isoformat(),
                'search_query': query,
                'deal_type': classify_deal_type(title, snippet)
            }
            
            deals.append(deal)
            
        except Exception as e:
            print(f"Error formatting search result: {e}")
            continue
    
    return deals


def has_deal_indicators(title, snippet):
    """Check if the result contains deal indicators"""
    text = f"{title} {snippet}".lower()
    
    deal_keywords = [
        'challenge', 'discount', 'voucher', 'free', 'promotion', 'offer',
        'deal', 'coupon', 'save', 'promo', 'special', 'limited time',
        'certification challenge', 'exam voucher', 'free exam'
    ]
    
    return any(keyword in text for keyword in deal_keywords)


def extract_certification_name(title, snippet, provider):
    """Extract certification name from title and snippet"""
    text = f"{title} {snippet}"
    
    # Provider-specific patterns
    patterns = {
        'AWS': [
            r'AWS\s+(?:Certified\s+)?([A-Za-z\s]+(?:Associate|Professional|Specialty|Practitioner))',
            r'(AI Practitioner)',
            r'(Solutions Architect)',
            r'(Developer Associate)',
            r'(SysOps Administrator)'
        ],
        'AZURE': [
            r'Azure\s+([A-Za-z\s]+(?:Associate|Expert|Fundamentals))',
            r'(AZ-\d+)',
            r'Microsoft\s+([A-Za-z\s]+(?:Associate|Expert))'
        ],
        'GCP': [
            r'Google Cloud\s+([A-Za-z\s]+(?:Associate|Professional))',
            r'(Cloud Engineer)',
            r'(Cloud Architect)'
        ],
        'SALESFORCE': [
            r'Salesforce\s+([A-Za-z\s]+(?:Administrator|Developer|Consultant))',
            r'(Platform Developer)',
            r'(System Administrator)'
        ],
        'DATABRICKS': [
            r'Databricks\s+([A-Za-z\s]+(?:Associate|Professional))',
            r'(Data Engineer)',
            r'(Machine Learning)'
        ]
    }
    
    provider_patterns = patterns.get(provider, [])
    
    for pattern in provider_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    return f"{provider} Certification"


def extract_discount_type(title, snippet):
    """Extract discount type from text"""
    text = f"{title} {snippet}".lower()
    
    if 'free' in text or 'complimentary' in text:
        return 'Free'
    elif 'voucher' in text:
        return 'Voucher'
    elif '%' in text:
        # Try to extract percentage
        match = re.search(r'(\d+)%', text)
        if match:
            return f"{match.group(1)}% Off"
    elif 'discount' in text:
        return 'Discount'
    elif 'challenge' in text:
        return 'Challenge Reward'
    
    return 'Special Offer'


def extract_eligibility(title, snippet):
    """Extract eligibility requirements"""
    text = f"{title} {snippet}".lower()
    
    if 'student' in text:
        return 'Students'
    elif 'employee' in text:
        return 'Employees'
    elif 'partner' in text:
        return 'Partners'
    elif 'challenge' in text:
        return 'Challenge Participants'
    
    return 'General Public'


def extract_source_name(url):
    """Extract friendly source name from URL"""
    try:
        domain = urlparse(url).netloc.lower()
        
        if 'aws.amazon.com' in domain or 'awscloud.com' in domain:
            return 'AWS Official'
        elif 'microsoft.com' in domain or 'azure.com' in domain:
            return 'Microsoft Official'
        elif 'cloud.google.com' in domain:
            return 'Google Cloud Official'
        elif 'databricks.com' in domain:
            return 'Databricks Official'
        elif 'salesforce.com' in domain or 'trailhead' in domain:
            return 'Salesforce Official'
        else:
            return domain.replace('www.', '').title()
    except:
        return 'External Source'


def calculate_confidence_score(title, snippet, link, provider):
    """Calculate confidence score for the deal"""
    score = 0.0
    text = f"{title} {snippet}".lower()
    
    # Base score for having title and snippet
    if title and snippet:
        score += 0.3
    
    # Official domain bonus
    domain = urlparse(link).netloc.lower()
    official_domains = {
        'AWS': ['aws.amazon.com', 'awscloud.com'],
        'AZURE': ['microsoft.com', 'azure.com'],
        'GCP': ['cloud.google.com'],
        'SALESFORCE': ['salesforce.com', 'trailhead.salesforce.com'],
        'DATABRICKS': ['databricks.com']
    }
    
    if any(official in domain for official in official_domains.get(provider, [])):
        score += 0.3
    
    # Deal keyword bonus
    deal_keywords = ['challenge', 'voucher', 'free', 'discount', 'promotion']
    for keyword in deal_keywords:
        if keyword in text:
            score += 0.1
    
    # Current year bonus
    current_year = str(datetime.now().year)
    if current_year in text:
        score += 0.2
    
    return min(score, 1.0)


def classify_deal_type(title, snippet):
    """Classify the type of deal"""
    text = f"{title} {snippet}".lower()
    
    if 'challenge' in text:
        return 'Certification Challenge'
    elif 'voucher' in text:
        return 'Exam Voucher'
    elif 'free' in text:
        return 'Free Offer'
    elif 'discount' in text:
        return 'Discount Deal'
    elif 'promotion' in text:
        return 'Promotional Offer'
    
    return 'General Deal'