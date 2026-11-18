#!/usr/bin/env python3

import aws_cdk as cdk

from aws_cdk_resource_creation.aws_cdk_resource_creation_stack import AwsCdkResourceCreationStack


app = cdk.App()
AwsCdkResourceCreationStack(app, "AwsCdkResourceCreationStack")

app.synth()
