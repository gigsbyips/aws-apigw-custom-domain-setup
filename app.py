# #!/usr/bin/env python3
import aws_cdk as cdk

from cert_stack import CertStack
from domain_stack import DomainStack

app = cdk.App()

hosted_zone_name = "<<REPLACE_WITH_YOUR_DOMAIN_NAME>>"
custom_domains=["first","second"] # Replace with appropriate custom domain names.

cert_env = cdk.Environment(account="<<REPLACE_WITH_YOUR_ACC_NO>>", region="us-east-1")
app_env = cdk.Environment(account="<<REPLACE_WITH_YOUR_ACC_NO>>", region="us-east-2")

CertStack(app, "CustomCertStack", hzone=hosted_zone_name, cdomains=custom_domains, env=cert_env)
DomainStack(app, "CustomDomainStack", hzone=hosted_zone_name, cdomains=custom_domains, env=app_env)

app.synth()
