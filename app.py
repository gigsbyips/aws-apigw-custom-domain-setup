# #!/usr/bin/env python3
import aws_cdk as cdk

from cert_stack import CertStack
from domain_stack import DomainStack

app = cdk.App()

# This is for a scenario where you have EDGE Optimised API, so certificate must be in us-east-1 region.
# API can be in any region. This uses OOTB cross_region_reference support.
# AWS creates custom resources behind the scene that stores values in SSM to be accessible in other region.

hosted_zone_name = "example.com"  # Change this to an original domain you own.

# Change this to actual subdomains you want.
custom_domain_names = ["firstsubdomain.example.com",
                       "secondsubdomain.example.com"]

cert_env = cdk.Environment(account="<<AWS_ACCOUNT>>", region="us-east-1")
app_env = cdk.Environment(account="<<AWS_ACCOUNT>>", region="us-east-2")

cert = CertStack(app, "CertStack", hzone=hosted_zone_name,
                 cdomains=custom_domain_names, env=cert_env,  cross_region_references=True)

DomainStack(app, "DomainStack", env=app_env,
            cert=cert,  hzone=hosted_zone_name, cdomains=custom_domain_names, cross_region_references=True)

app.synth()
