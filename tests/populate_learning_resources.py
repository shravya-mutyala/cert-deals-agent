#!/usr/bin/env python3
"""
Script to populate the learning-resources DynamoDB table with hardcoded links
from the frontend agent-chat.html file
"""

import boto3
import json
from datetime import datetime

# Initialize DynamoDB with your profile
session = boto3.Session(profile_name='msr-aws')
dynamodb = session.resource('dynamodb', region_name='us-east-1')
table_name = 'learning-resources'

def populate_learning_resources():
    """Populate the learning resources table with hardcoded data"""
    
    try:
        table = dynamodb.Table(table_name)
        
        # Learning resources data extracted from agent-chat.html
        resources_data = [
            # AWS Resources
            {
                'provider': 'AWS',
                'resource_id': 'aws-skill-builder',
                'name': 'AWS Skill Builder',
                'url': 'https://skillbuilder.aws/',
                'description': 'on-demand courses & learning plans',
                'category': 'Training Platform'
            },
            {
                'provider': 'AWS',
                'resource_id': 'aws-builder-labs',
                'name': 'AWS Builder Labs',
                'url': 'https://aws.amazon.com/builder/',
                'description': 'guided hands-on labs',
                'category': 'Hands-on Labs'
            },
            {
                'provider': 'AWS',
                'resource_id': 'aws-educate',
                'name': 'AWS Educate',
                'url': 'https://aws.amazon.com/education/awseducate/',
                'description': 'free beginner content for students/learners',
                'category': 'Education'
            },
            {
                'provider': 'AWS',
                'resource_id': 'aws-workshops',
                'name': 'AWS Workshops',
                'url': 'https://workshops.aws/',
                'description': 'curated, hands-on workshops',
                'category': 'Workshops'
            },
            {
                'provider': 'AWS',
                'resource_id': 'aws-documentation',
                'name': 'AWS Documentation',
                'url': 'https://docs.aws.amazon.com/',
                'description': 'service docs, tutorials, best practices',
                'category': 'Documentation'
            },
            {
                'provider': 'AWS',
                'resource_id': 'aws-certification',
                'name': 'AWS Certification',
                'url': 'https://aws.amazon.com/certification/',
                'description': 'paths, exam guides, prep',
                'category': 'Certification'
            },
            
            # Azure Resources
            {
                'provider': 'AZURE',
                'resource_id': 'microsoft-learn',
                'name': 'Microsoft Learn',
                'url': 'https://learn.microsoft.com/training/',
                'description': 'free interactive modules & learning paths',
                'category': 'Training Platform'
            },
            {
                'provider': 'AZURE',
                'resource_id': 'azure-documentation',
                'name': 'Azure Documentation',
                'url': 'https://learn.microsoft.com/azure/',
                'description': 'service docs, samples, quickstarts',
                'category': 'Documentation'
            },
            {
                'provider': 'AZURE',
                'resource_id': 'what-the-hack',
                'name': 'What The Hack',
                'url': 'https://microsoft.github.io/WhatTheHack/',
                'description': 'open-source workshop-style scenarios',
                'category': 'Workshops'
            },
            {
                'provider': 'AZURE',
                'resource_id': 'azure-learning-paths',
                'name': 'Azure Learning Paths',
                'url': 'https://learn.microsoft.com/training/azure/',
                'description': 'curated Azure tracks',
                'category': 'Learning Paths'
            },
            
            # Google Cloud Resources
            {
                'provider': 'GCP',
                'resource_id': 'cloud-skills-boost',
                'name': 'Cloud Skills Boost',
                'url': 'https://www.cloudskillsboost.google/',
                'description': 'hands-on labs, quests, and courses',
                'category': 'Training Platform'
            },
            {
                'provider': 'GCP',
                'resource_id': 'gcp-training',
                'name': 'Google Cloud Training',
                'url': 'https://cloud.google.com/training',
                'description': 'learning paths & instructor-led training',
                'category': 'Training'
            },
            {
                'provider': 'GCP',
                'resource_id': 'gcp-docs',
                'name': 'Google Cloud Docs',
                'url': 'https://cloud.google.com/docs',
                'description': 'product docs & quickstarts',
                'category': 'Documentation'
            },
            {
                'provider': 'GCP',
                'resource_id': 'gcp-certification',
                'name': 'Google Cloud Certification',
                'url': 'https://cloud.google.com/certification',
                'description': 'paths, exam guides, prep',
                'category': 'Certification'
            },
            
            # Salesforce Resources
            {
                'provider': 'SALESFORCE',
                'resource_id': 'trailhead',
                'name': 'Trailhead',
                'url': 'https://trailhead.salesforce.com/',
                'description': 'free, gamified learning modules & trails',
                'category': 'Training Platform'
            },
            {
                'provider': 'SALESFORCE',
                'resource_id': 'salesforce-credentials',
                'name': 'Salesforce Credentials',
                'url': 'https://trailheadacademy.salesforce.com/certification-overview',
                'description': 'certifications & exam guides',
                'category': 'Certification'
            },
            {
                'provider': 'SALESFORCE',
                'resource_id': 'salesforce-help',
                'name': 'Salesforce Help & Docs',
                'url': 'https://help.salesforce.com/s/',
                'description': 'official product documentation',
                'category': 'Documentation'
            },
            {
                'provider': 'SALESFORCE',
                'resource_id': 'superbadges',
                'name': 'Superbadges',
                'url': 'https://trailhead.salesforce.com/superbadges',
                'description': 'hands-on, scenario-based challenges',
                'category': 'Hands-on Labs'
            },
            
            # Databricks Resources
            {
                'provider': 'DATABRICKS',
                'resource_id': 'databricks-academy',
                'name': 'Databricks Academy Labs',
                'url': 'https://www.databricks.com/databricks-academy-labs',
                'description': 'learning paths, courses, and exams',
                'category': 'Training Platform'
            },
            {
                'provider': 'DATABRICKS',
                'resource_id': 'databricks-docs',
                'name': 'Databricks Documentation',
                'url': 'https://docs.databricks.com/',
                'description': 'product docs & quickstarts',
                'category': 'Documentation'
            },
            {
                'provider': 'DATABRICKS',
                'resource_id': 'databricks-learn',
                'name': 'Learn on Databricks',
                'url': 'https://www.databricks.com/learn',
                'description': 'self-paced content & webinars',
                'category': 'Learning'
            },
            {
                'provider': 'DATABRICKS',
                'resource_id': 'databricks-workshops',
                'name': 'Workshops',
                'url': 'https://www.databricks.com/resources?type=workshop',
                'description': 'upcoming workshops & hands-on sessions',
                'category': 'Workshops'
            }
        ]
        
        # Add timestamp to all records
        timestamp = datetime.utcnow().isoformat()
        for resource in resources_data:
            resource['created_at'] = timestamp
            resource['updated_at'] = timestamp
        
        # Batch write to DynamoDB
        with table.batch_writer() as batch:
            for resource in resources_data:
                batch.put_item(Item=resource)
                print(f"Added: {resource['provider']} - {resource['name']}")
        
        print(f"\nSuccessfully populated {len(resources_data)} learning resources!")
        
        # Verify the data
        response = table.scan()
        print(f"Total items in table: {response['Count']}")
        
        return True
        
    except Exception as e:
        print(f"Error populating learning resources: {str(e)}")
        return False

if __name__ == "__main__":
    print("Populating learning resources table...")
    success = populate_learning_resources()
    if success:
        print("Learning resources populated successfully!")
    else:
        print("Failed to populate learning resources!")