#!/usr/bin/env python3
"""
Main CDK app for Certification Hunter with Bedrock Agent
"""

import aws_cdk as cdk
from stacks.simple_bedrock_stack import SimpleBedrockStack
from stacks.certification_hunter_stack import CertificationHunterStack

app = cdk.App()

# Deploy the simplified Bedrock stack (Lambda functions only)
bedrock_stack = SimpleBedrockStack(app, "SimpleBedrockStack")

# Deploy the certification hunter stack as fallback
fallback_stack = CertificationHunterStack(app, "CertificationHunterStack")

app.synth()