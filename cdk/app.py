#!/usr/bin/env python3
import aws_cdk as cdk
from stacks.certification_hunter_stack import CertificationHunterStack
from stacks.bedrock_agent_stack import BedrockAgentStack

app = cdk.App()

# Deploy basic infrastructure
base_stack = CertificationHunterStack(app, "CertificationHunterStack")

# Deploy enhanced Bedrock Agent
agent_stack = BedrockAgentStack(app, "CertificationHunterAgentStack")

app.synth()