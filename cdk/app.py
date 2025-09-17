#!/usr/bin/env python3
import aws_cdk as cdk
from stacks.certification_hunter_stack import CertificationHunterStack

app = cdk.App()
CertificationHunterStack(app, "CertificationHunterStack")
app.synth()