from aws_cdk import Stack
from aws_cdk import aws_route53 as route53
from aws_cdk import aws_route53_targets as route53_targets
from aws_cdk import aws_apigateway as apigw
from constructs import Construct

from aws_cdk import (
    aws_certificatemanager as acm
)
import aws_cdk.custom_resources as cr


class DomainStack(Stack):

    def __init__(self, scope: Construct, id: str, hzone:str, cdomains:list, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        hosted_zone_name=hzone
        custom_domain_names=cdomains
        
        cert_arn_params={} # Dict to hold cert arns fetched by Custom Resource.
        
        for domain in custom_domain_names:
            cert_arn_param = cr.AwsCustomResource(self, f"{domain}-CResourceFetchCertArn",
                on_update=cr.AwsSdkCall(service="SSM", action="getParameter",
                    parameters={
                        "Name": f"/cdk/feature/{domain}/certarn",
                    },
                    region="us-east-1",
                    physical_resource_id=cr.PhysicalResourceId.of(f"{domain}-cert-arn")),
                
                on_create=cr.AwsSdkCall(service="SSM", action="getParameter",
                    parameters={
                        "Name": f"/cdk/feature/{domain}/certarn",
                    },
                    region="us-east-1",
                    physical_resource_id=cr.PhysicalResourceId.of(f"{domain}-cert-arn")),
                policy=cr.AwsCustomResourcePolicy.from_sdk_calls(resources=cr.AwsCustomResourcePolicy.ANY_RESOURCE)
            )
            cert_arn_params[domain]=cert_arn_param
        
        # Get Existing Hosted Zone. 
        hosted_zone = route53.HostedZone.from_lookup(
            self, "hostedzone", domain_name=hosted_zone_name
        )
        
        for domain in custom_domain_names:
            cert_arn = cert_arn_params[domain].get_response_field("Parameter.Value")
            certificate = acm.Certificate.from_certificate_arn(
                self, f"{domain}-certificate", certificate_arn=cert_arn
            )       
            domain = apigw.DomainName(
                self,
                f"{domain}-domain",
                domain_name=f"{domain}.{hosted_zone_name}",
                certificate=certificate,
                endpoint_type=apigw.EndpointType.EDGE,
                security_policy=apigw.SecurityPolicy.TLS_1_2,
            )

            # Create Alias record in route53 for the custom domain.
            route53.ARecord(
                self,
                f"{domain}-domain-alias",
                record_name=f"{domain}.{hosted_zone_name}",
                zone=hosted_zone,
                target=route53.RecordTarget.from_alias(
                    route53_targets.ApiGatewayDomain(domain)
                ),
            )