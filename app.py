#!/usr/bin/env python3
import os

import aws_cdk as cdk
from aws_cdk import Tags

from opensearch_cognito.opensearch_cognito_stack import OpensearchCognitoStack


app = cdk.App()

def tag_my_stack(stack):
    tags = Tags.of(stack)
    tags.add("project", "opensearch-cognito")

account_id = os.getenv('CDK_DEFAULT_ACCOUNT')
region = os.getenv('CDK_DEFAULT_REGION')
env=cdk.Environment(account=account_id, region=region)
env_name = app.node.try_get_context("environment_name")
opensearch_stack = OpensearchCognitoStack(app, f"oss-{env_name}-OpensearchCognitoStack", env=env
    # If you don't specify 'env', this stack will be environment-agnostic.
    # Account/Region-dependent features and context lookups will not work,
    # but a single synthesized template can be deployed anywhere.
)

tag_my_stack(opensearch_stack)
app.synth()
