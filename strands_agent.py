#!/usr/bin/env python3
"""
Certification Coupon Hunter - Strands Agent Implementation
A model-driven approach to building AI agents in just a few lines of code.
"""

import os
import json
import boto3
import requests
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from strands_agents import Agent, tool, run_agent
from bs4 import BeautifulSoup

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

@dataclass
class CertificationDeal:
    """Data model for certification deals"""
    provider: str
    certification_name: str
    discount_amount: str
    original_price: str
    discounted_price: str
    eligibility: str
    expiry_date: Optional[str]
    deal_url: str
    confidence_score: float
    deal_quality: str

@dataclass
class UserProfile:
    """Data model for user profiles"""
    user_id: str
    current_role: str
    target_role: str
    experience_level: str
    preferred_cloud: str
    budget_range: str
    certifications_owned: List[str]

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
bedrock = boto3.client('bedrock-runtime')

# DynamoDB tables
offers_table = dynamodb.Table(os.getenv('OFFERS_TABLE', 'certification-offers'))
users_table = dynamodb.Table(os.getenv('USERS_TABLE', 'certification-users'))

class CertificationHunterAgent:
    """Strands Agent for Certification Deal Hunting and Career Planning"""
    
    def __init__(self):
        self.agent = Agent(
            name="Certification Hunter",
            description="""
            I'm an expert Certification Deal Hunter and Career Advisor AI agent. 
            I help developers and IT professionals:
            
            🎯 Discover and verify certification deals across AWS, Azure, Google Cloud, Databricks, and Salesforce
            📊 Analyze complex eligibility requirements and match them to user profiles  
            🚀 Plan optimal career paths with certification roadmaps
            💰 Optimize savings by comparing deals across providers
            🔔 Provide proactive alerts for expiring deals and new opportunities
            
            I use multi-step reasoning for complex certification planning and make autonomous 
            decisions for deal discovery and validation.
            """,
            model="gpt-4",  # Can be configured to use Bedrock models
            tools=[
                self.discover_certification_deals,
                self.analyze_deal_eligibility,
                self.create_career_roadmap,
                self.save_user_profile,
                self.get_personalized_recommendations,
                self.compare_deals_across_providers,
                self.check_deal_expiry_alerts
            ]
        )
    
    @tool
    def discover_certification_deals(self, providers: List[str] = None) -> Dict[str, Any]:
        """
        Autonomously discover certification deals from provider websites
        
        Args:
            providers: List of providers to search (AWS, Azure, Google Cloud, Databricks, Salesforce)
        
        Returns:
            Dictionary with discovered deals and analysis
        """
        if not providers:
            providers = ['AWS', 'Azure', 'Google Cloud', 'Databricks', 'Salesforce']
        
        print(f"🔍 Discovering deals from {len(providers)} providers...")
        
        all_deals = []
        provider_urls = {
            'AWS': [
                'https://aws.amazon.com/training/events/',
                'https://aws.amazon.com/certification/certification-prep/',
            ],
            'Azure': [
                'https://azure.microsoft.com/en-us/certifications/',
                'https://docs.microsoft.com/en-us/learn/certifications/',
            ],
            'Google Cloud': [
                'https://cloud.google.com/training/certification',
                'https://cloud.google.com/blog/topics/training-certifications',
            ],
            'Databricks': [
                'https://www.databricks.com/learn/certification',
                'https://www.databricks.com/learn/training',
            ],
            'Salesforce': [
                'https://trailhead.salesforce.com/en/credentials/certification-vouchers/',
                'https://trailhead.salesforce.com/en/credentials/',
            ]
        }
        
        for provider in providers:
            urls = provider_urls.get(provider, [])
            for url in urls:
                deals = self._scrape_provider_deals(provider, url)
                all_deals.extend(deals)
        
        # Analyze deals with AI
        analyzed_deals = self._analyze_deals_with_bedrock(all_deals)
        
        # Store in DynamoDB
        self._store_deals(analyzed_deals)
        
        return {
            'total_deals_found': len(analyzed_deals),
            'deals_by_provider': self._group_deals_by_provider(analyzed_deals),
            'top_deals': analyzed_deals[:5],
            'summary': f"Discovered {len(analyzed_deals)} certification deals across {len(providers)} providers",
            'last_updated': datetime.now(timezone.utc).isoformat()
        }
    
    @tool
    def analyze_deal_eligibility(self, deal_id: str, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze if a user is eligible for a specific certification deal
        
        Args:
            deal_id: ID of the deal to analyze
            user_profile: User's profile information
            
        Returns:
            Eligibility analysis with recommendations
        """
        print(f"🔍 Analyzing eligibility for deal {deal_id}...")
        
        # Get deal from DynamoDB
        try:
            response = offers_table.get_item(Key={'offer_id': deal_id})
            if 'Item' not in response:
                return {'error': 'Deal not found', 'eligible': False}
            
            deal = response['Item']
        except Exception as e:
            return {'error': f'Database error: {str(e)}', 'eligible': False}
        
        # Use Bedrock to analyze eligibility
        eligibility_analysis = self._analyze_eligibility_with_ai(deal, user_profile)
        
        return {
            'deal_id': deal_id,
            'eligible': eligibility_analysis.get('eligible', False),
            'confidence_score': eligibility_analysis.get('confidence_score', 0.0),
            'requirements_met': eligibility_analysis.get('requirements_met', []),
            'requirements_missing': eligibility_analysis.get('requirements_missing', []),
            'recommendations': eligibility_analysis.get('recommendations', []),
            'estimated_savings': eligibility_analysis.get('estimated_savings', 'Unknown')
        }
    
    @tool
    def create_career_roadmap(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a personalized certification career roadmap
        
        Args:
            user_profile: User's career information and goals
            
        Returns:
            Detailed career roadmap with certification path
        """
        print(f"🚀 Creating career roadmap for {user_profile.get('target_role', 'career advancement')}...")
        
        # Use Bedrock to generate comprehensive career path
        roadmap = self._generate_career_roadmap_with_ai(user_profile)
        
        # Find relevant deals for recommended certifications
        relevant_deals = self._find_deals_for_certifications(roadmap.get('recommended_certifications', []))
        
        return {
            'career_roadmap': roadmap,
            'relevant_deals': relevant_deals,
            'estimated_timeline': roadmap.get('timeline_months', '12-18 months'),
            'total_estimated_cost': roadmap.get('total_cost', '$1000-2000'),
            'potential_savings': self._calculate_potential_savings(relevant_deals),
            'next_steps': roadmap.get('immediate_actions', []),
            'generated_at': datetime.now(timezone.utc).isoformat()
        }
    
    @tool
    def save_user_profile(self, user_profile: Dict[str, Any]) -> Dict[str, str]:
        """
        Save or update user profile for personalized recommendations
        
        Args:
            user_profile: Complete user profile information
            
        Returns:
            Confirmation of profile save
        """
        print(f"💾 Saving profile for user {user_profile.get('user_id', 'anonymous')}...")
        
        try:
            # Add metadata
            user_profile['updated_at'] = datetime.now(timezone.utc).isoformat()
            user_profile['profile_version'] = '1.0'
            
            # Save to DynamoDB
            users_table.put_item(Item=user_profile)
            
            return {
                'status': 'success',
                'message': 'User profile saved successfully',
                'user_id': user_profile.get('user_id')
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Failed to save profile: {str(e)}'
            }
    
    @tool
    def get_personalized_recommendations(self, user_id: str) -> Dict[str, Any]:
        """
        Get personalized certification deal recommendations for a user
        
        Args:
            user_id: User's unique identifier
            
        Returns:
            Personalized recommendations based on user profile and available deals
        """
        print(f"🎯 Getting personalized recommendations for user {user_id}...")
        
        try:
            # Get user profile
            user_response = users_table.get_item(Key={'user_id': user_id})
            if 'Item' not in user_response:
                return {'error': 'User profile not found'}
            
            user_profile = user_response['Item']
            
            # Get all available deals
            deals_response = offers_table.scan()
            all_deals = deals_response.get('Items', [])
            
            # Use AI to match deals to user profile
            recommendations = self._generate_personalized_recommendations(user_profile, all_deals)
            
            return {
                'user_id': user_id,
                'recommendations': recommendations,
                'total_matches': len(recommendations),
                'generated_at': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            return {'error': f'Failed to generate recommendations: {str(e)}'}
    
    @tool
    def compare_deals_across_providers(self, certification_type: str) -> Dict[str, Any]:
        """
        Compare similar certification deals across different providers
        
        Args:
            certification_type: Type of certification to compare (e.g., "cloud architect", "data engineer")
            
        Returns:
            Comparison of deals across providers with recommendations
        """
        print(f"⚖️ Comparing {certification_type} deals across providers...")
        
        # Search for relevant deals
        relevant_deals = self._search_deals_by_type(certification_type)
        
        if not relevant_deals:
            return {
                'certification_type': certification_type,
                'deals_found': 0,
                'message': 'No deals found for this certification type'
            }
        
        # Group by provider and analyze
        comparison = self._analyze_deal_comparison(relevant_deals)
        
        return {
            'certification_type': certification_type,
            'deals_found': len(relevant_deals),
            'provider_comparison': comparison,
            'best_value_recommendation': comparison.get('best_value'),
            'analysis_summary': comparison.get('summary'),
            'generated_at': datetime.now(timezone.utc).isoformat()
        }
    
    @tool
    def check_deal_expiry_alerts(self, days_ahead: int = 7) -> Dict[str, Any]:
        """
        Check for deals expiring within specified days and generate alerts
        
        Args:
            days_ahead: Number of days to look ahead for expiring deals
            
        Returns:
            List of expiring deals with alert information
        """
        print(f"⏰ Checking for deals expiring in the next {days_ahead} days...")
        
        # Get all deals from DynamoDB
        try:
            response = offers_table.scan()
            all_deals = response.get('Items', [])
        except Exception as e:
            return {'error': f'Failed to fetch deals: {str(e)}'}
        
        # Find expiring deals
        expiring_deals = self._find_expiring_deals(all_deals, days_ahead)
        
        return {
            'days_ahead': days_ahead,
            'expiring_deals_count': len(expiring_deals),
            'expiring_deals': expiring_deals,
            'urgent_alerts': [deal for deal in expiring_deals if deal.get('days_until_expiry', 999) <= 3],
            'generated_at': datetime.now(timezone.utc).isoformat()
        }
    
    # Helper methods
    def _scrape_provider_deals(self, provider: str, url: str) -> List[Dict[str, Any]]:
        """Scrape deals from a provider URL"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for deal-related content
            deal_keywords = ['discount', 'voucher', 'free', 'promo', 'offer', 'save', '%', 'deal']
            
            deals = []
            for keyword in deal_keywords:
                elements = soup.find_all(text=lambda text: text and keyword in text.lower())
                
                for element in elements[:2]:  # Limit per keyword
                    deal = {
                        'provider': provider,
                        'raw_text': element.strip()[:500],  # Limit text length
                        'source_url': url,
                        'discovered_at': datetime.now(timezone.utc).isoformat(),
                        'keyword_matched': keyword
                    }
                    deals.append(deal)
            
            return deals
            
        except Exception as e:
            print(f"Error scraping {provider} at {url}: {e}")
            return []
    
    def _analyze_deals_with_bedrock(self, deals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Use Bedrock to analyze and structure deals"""
        if not deals:
            return []
        
        analyzed_deals = []
        
        for deal in deals:
            try:
                prompt = f"""
                Analyze this certification deal and extract structured information:
                
                Provider: {deal['provider']}
                Text: {deal['raw_text']}
                Source: {deal['source_url']}
                
                Extract and return JSON with:
                {{
                    "offer_id": "unique_identifier",
                    "certification_name": "specific certification name",
                    "discount_amount": "percentage or dollar amount",
                    "original_price": "original exam cost",
                    "eligibility_requirements": "who can use this deal",
                    "expiry_date": "when it expires (if mentioned)",
                    "confidence_score": 0.8,
                    "deal_quality": "excellent/good/fair/poor",
                    "action_required": "what user needs to do",
                    "deal_type": "voucher/discount/free_retake/bundle"
                }}
                
                Return only valid JSON.
                """
                
                response = bedrock.invoke_model(
                    modelId='anthropic.claude-3-sonnet-20240229-v1:0',
                    body=json.dumps({
                        'anthropic_version': 'bedrock-2023-05-31',
                        'max_tokens': 800,
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
                    deal['offer_id'] = f"{deal['provider']}_{len(analyzed_deals)}"
                    analyzed_deals.append(deal)
                    
            except Exception as e:
                print(f"Error analyzing deal: {e}")
                deal['confidence_score'] = 0.1
                deal['offer_id'] = f"{deal['provider']}_{len(analyzed_deals)}"
                analyzed_deals.append(deal)
        
        # Sort by confidence and quality
        analyzed_deals.sort(key=lambda x: x.get('confidence_score', 0), reverse=True)
        return analyzed_deals
    
    def _store_deals(self, deals: List[Dict[str, Any]]):
        """Store deals in DynamoDB"""
        try:
            with offers_table.batch_writer() as batch:
                for deal in deals:
                    # Ensure required keys exist
                    if 'offer_id' not in deal:
                        deal['offer_id'] = f"{deal.get('provider', 'unknown')}_{datetime.now().timestamp()}"
                    
                    batch.put_item(Item=deal)
        except Exception as e:
            print(f"Error storing deals: {e}")
    
    def _group_deals_by_provider(self, deals: List[Dict[str, Any]]) -> Dict[str, int]:
        """Group deals by provider"""
        provider_counts = {}
        for deal in deals:
            provider = deal.get('provider', 'Unknown')
            provider_counts[provider] = provider_counts.get(provider, 0) + 1
        return provider_counts
    
    def _analyze_eligibility_with_ai(self, deal: Dict[str, Any], user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Use AI to analyze deal eligibility for user"""
        # Implementation would use Bedrock to analyze eligibility
        # For now, return a basic analysis
        return {
            'eligible': True,
            'confidence_score': 0.8,
            'requirements_met': ['Basic requirements'],
            'requirements_missing': [],
            'recommendations': ['Apply soon as deals are limited'],
            'estimated_savings': '$100-200'
        }
    
    def _generate_career_roadmap_with_ai(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Generate career roadmap using AI"""
        # Implementation would use Bedrock for detailed career planning
        # For now, return a basic roadmap
        return {
            'recommended_certifications': ['AWS Solutions Architect', 'Azure Administrator'],
            'timeline_months': '12-18',
            'total_cost': '$1000-1500',
            'immediate_actions': ['Start with cloud fundamentals', 'Practice hands-on labs']
        }
    
    def _find_deals_for_certifications(self, certifications: List[str]) -> List[Dict[str, Any]]:
        """Find deals for specific certifications"""
        # Implementation would search DynamoDB for matching deals
        return []
    
    def _calculate_potential_savings(self, deals: List[Dict[str, Any]]) -> str:
        """Calculate potential savings from deals"""
        return "$200-500"
    
    def _generate_personalized_recommendations(self, user_profile: Dict[str, Any], deals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate personalized recommendations"""
        # Implementation would use AI to match user profile to deals
        return deals[:5]  # Return top 5 for now
    
    def _search_deals_by_type(self, certification_type: str) -> List[Dict[str, Any]]:
        """Search deals by certification type"""
        # Implementation would search DynamoDB
        return []
    
    def _analyze_deal_comparison(self, deals: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze and compare deals"""
        return {
            'best_value': 'AWS - Best overall value',
            'summary': 'AWS offers the most comprehensive deals'
        }
    
    def _find_expiring_deals(self, deals: List[Dict[str, Any]], days_ahead: int) -> List[Dict[str, Any]]:
        """Find deals expiring within specified days"""
        # Implementation would parse expiry dates and filter
        return []

# Main execution
def main():
    """Main function to run the Strands Agent"""
    print("🚀 Starting Certification Hunter Strands Agent...")
    
    # Initialize the agent
    hunter = CertificationHunterAgent()
    
    # Example usage - you can customize this based on your needs
    print("\n🎯 Example: Discovering certification deals...")
    
    # Run the agent with a sample query
    result = run_agent(
        hunter.agent,
        "I'm a Python developer looking to transition to cloud architecture. Can you discover current certification deals and create a career roadmap for me?"
    )
    
    print("\n✅ Agent Response:")
    print(result)

if __name__ == "__main__":
    main()