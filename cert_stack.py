import aws_cdk as cdk
from aws_cdk import Stack
from aws_cdk import aws_certificatemanager as acm
from aws_cdk import aws_route53 as route53
from constructs import Construct

app = cdk.App()


class CertStack(Stack):

    def __init__(self, scope: Construct, id: str, hzone: str, cdomains: list, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        hosted_zone_name = hzone
        custom_domain_names = cdomains

        # Get details of the existing Hosted Zone.
        hosted_zone = route53.HostedZone.from_lookup(
            self, "hostedzone", domain_name=hosted_zone_name
        )

        # Create an ACM certificate for the custom domain.
        self.first_certificate = acm.Certificate(
            self,
            "first-subdomain-certificate",
            domain_name=custom_domain_names[0],
            validation=acm.CertificateValidation.from_dns(hosted_zone),
        )

        # Create an ACM certificate for the custom domain.
        self.second_certificate = acm.Certificate(
            self,
            "second-subdomain-certificate",
            domain_name=custom_domain_names[1],
            validation=acm.CertificateValidation.from_dns(hosted_zone),
        )
