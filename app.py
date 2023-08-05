# #!/usr/bin/env python3
import os
import aws_cdk as cdk
from aws_cdk import Stack
from aws_cdk import aws_certificatemanager as acm
from aws_cdk import aws_route53 as route53
from aws_cdk import aws_route53_targets as route53_targets
from aws_cdk import aws_apigateway as apigw
from constructs import Construct
from aws_cdk import aws_lambda as lmbd

app = cdk.App()


class TestApiStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Read Context Variables.
        hosted_zone_name = self.node.try_get_context("hosted_zone_name")
        cert_san = self.node.try_get_context("cert_san") # this is a list.
        custom_domain_name = self.node.try_get_context("custom_domain_name")

        # Get details of the existing Hosted Zone.
        hosted_zone = route53.HostedZone.from_lookup(
            self, "hostedzone", domain_name=hosted_zone_name
        )

        # Create an ACM certificate for the custom domain.
        certificate = acm.Certificate(
            self,
            "subdomain-certificate",
            domain_name=custom_domain_name,
            subject_alternative_names=cert_san,
            validation=acm.CertificateValidation.from_dns(hosted_zone),
        )

        # create custom domain.
        domain = apigw.DomainName(
            self,
            "custom-domain",
            domain_name=custom_domain_name,
            certificate=certificate,
            endpoint_type=apigw.EndpointType.EDGE,  # default is REGIONAL
            security_policy=apigw.SecurityPolicy.TLS_1_2,
        )

        # Cretea Alias record in route53 for the custom domain.
        route53.ARecord(
            self,
            "apgw-custom-domain-alias",
            record_name=custom_domain_name.split(f".{hosted_zone_name}")[0],
            zone=hosted_zone,  # this is hosted zone.
            target=route53.RecordTarget.from_alias(
                route53_targets.ApiGatewayDomain(domain)
            ),
        )

        mock_lambda = lmbd.Function(
            self,
            "mock-response-lambda",
            runtime=lmbd.Runtime.PYTHON_3_9,
            code=lmbd.Code.from_asset("lambdas"),
            handler="mock_function.lambda_handler",
        )

        # Dummy API for testing.
        api = apigw.RestApi(
            self, "mock-api", rest_api_name="mock-api",
            description="Dummy API for testing.",
            deploy_options=apigw.StageOptions(stage_name= "dev")
        )
        integration = apigw.LambdaIntegration(handler=mock_lambda)
        api.root.add_method("GET", integration)
        ## Map API with Custom Domain.
        domain.add_base_path_mapping(api, base_path="mockapi", attach_to_stage=False)

        # Another Dummy API for testing.
        api01 = apigw.RestApi(
            self, "mock-api01", rest_api_name="mock-api01",
            description="Dummy API for testing.",
            deploy_options=apigw.StageOptions(stage_name="dev")
        )
        integration01 = apigw.LambdaIntegration(handler=mock_lambda)
        api01.root.add_method("GET", integration01) 
            
        ## Map API with Custom Domain.
        domain.add_base_path_mapping(
            api01, base_path="mockapi_01", attach_to_stage=False
        )


app = cdk.App()
env = cdk.Environment(
    account=os.environ["CDK_DEFAULT_ACCOUNT"], region=os.environ["CDK_DEFAULT_REGION"]
)
TestApiStack(app, "DevTestApiStack", env=env)
app.synth()
