#!/usr/bin/env python3
"""
Main CDK app for Certification Hunter
"""

import aws_cdk as cdk
from stacks.certification_hunter_stack import CertificationHunterStack

app = cdk.App()

# Deploy the main certification hunter stack first
CertificationHunterStack(app, "CertificationHunterStack")

app.synth()