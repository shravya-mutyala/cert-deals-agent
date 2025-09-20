#!/usr/bin/env python3
"""
Simple CDK app for Certification Hunter
Only deploys the main stack without additional complexity
"""

import aws_cdk as cdk
from stacks.certification_hunter_stack import CertificationHunterStack

app = cdk.App()

# Deploy the main certification hunter stack
CertificationHunterStack(app, "CertificationHunterStack")

app.synth()