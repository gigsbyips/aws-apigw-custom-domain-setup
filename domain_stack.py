import aws_cdk as cdk
from aws_cdk import Stack
from aws_cdk import aws_route53 as route53
from aws_cdk import aws_route53_targets as route53_targets
from aws_cdk import aws_apigateway as apigw
from constructs import Construct
from aws_cdk import aws_lambda as lmbd
from cert_stack import CertStack


class DomainStack(Stack):

    def __init__(self, scope: Construct, id: str, cert: CertStack,  hzone: str, cdomains: list, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        hosted_zone_name = hzone
        custom_domain_names = cdomains

        # Get details of the existing Hosted Zone.
        hosted_zone = route53.HostedZone.from_lookup(
            self, "hostedzone", domain_name=hosted_zone_name
        )

        # Refer cert from the input cross region param.
        first_certificate = cert.first_certificate
        second_certificate = cert.second_certificate

        ######################################################
        # First set of domain and A records.
        ######################################################
        first_domain = apigw.DomainName(
            self,
            "first-custom-domain",
            domain_name=custom_domain_names[0],
            certificate=first_certificate,
            endpoint_type=apigw.EndpointType.EDGE,
            security_policy=apigw.SecurityPolicy.TLS_1_2,
        )

        # Create Alias record in route53 for the custom domain.
        route53.ARecord(
            self,
            "first-custom-domain-alias",
            record_name=custom_domain_names[0],
            zone=hosted_zone,
            target=route53.RecordTarget.from_alias(
                route53_targets.ApiGatewayDomain(first_domain)
            ),
        )

        ######################################################
        # Second set of domain and A records.
        ######################################################
        second_domain = apigw.DomainName(
            self,
            "second-custom-domain",
            domain_name=custom_domain_names[1],
            certificate=second_certificate,
            endpoint_type=apigw.EndpointType.EDGE,
            security_policy=apigw.SecurityPolicy.TLS_1_2,
        )

        # Create Alias record in route53 for the custom domain.
        route53.ARecord(
            self,
            "second-custom-domain-alias",
            record_name=custom_domain_names[1],
            zone=hosted_zone,
            target=route53.RecordTarget.from_alias(
                route53_targets.ApiGatewayDomain(second_domain)
            ),
        )
