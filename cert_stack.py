import aws_cdk as cdk
from aws_cdk import Stack
from aws_cdk import aws_certificatemanager as acm
from aws_cdk import aws_route53 as route53
from constructs import Construct
from aws_cdk import aws_ssm as ssm

app = cdk.App()


class CertStack(Stack):
    def __init__(self, scope: Construct, id: str, hzone:str, cdomains:list, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        hosted_zone_name=hzone
        custom_domain_names=cdomains
        
        # Get details of the existing Hosted Zone.
        hosted_zone = route53.HostedZone.from_lookup(
            self, "hostedzone", domain_name=hosted_zone_name
        )

        for domain in custom_domain_names:
            # Create an ACM certificate for the custom domain.
            certificate = acm.Certificate(
                self,
                f"{domain}-certificate",
                domain_name=f"{domain}.{hosted_zone_name}",
                validation=acm.CertificateValidation.from_dns(hosted_zone),
            )    
            ssm.StringParameter(self, f"{domain}-certificate-arn", parameter_name=f"/cdk/feature/{domain}/certarn", string_value=certificate.certificate_arn)
