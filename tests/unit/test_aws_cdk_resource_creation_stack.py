import aws_cdk as core
import aws_cdk.assertions as assertions
from aws_cdk_resource_creation.aws_cdk_resource_creation_stack import AwsCdkResourceCreationStack


def test_sqs_queue_created():
    app = core.App()
    stack = AwsCdkResourceCreationStack(app, "aws-cdk-resource-creation")
    template = assertions.Template.from_stack(stack)

    template.has_resource_properties("AWS::SQS::Queue", {
        "VisibilityTimeout": 300
    })


def test_sns_topic_created():
    app = core.App()
    stack = AwsCdkResourceCreationStack(app, "aws-cdk-resource-creation")
    template = assertions.Template.from_stack(stack)

    template.resource_count_is("AWS::SNS::Topic", 1)


def test_ec2_instance_created():
    app = core.App()
    stack = AwsCdkResourceCreationStack(app, "aws-cdk-resource-creation")
    template = assertions.Template.from_stack(stack)

    template.resource_count_is("AWS::EC2::Instance", 1)
    template.has_resource_properties("AWS::EC2::Instance", {
        "InstanceType": "t3.micro",
        "BlockDeviceMappings": [{
            "DeviceName": "/dev/xvda",
            "Ebs": {"Encrypted": True, "VolumeSize": 8, "VolumeType": "gp3"},
        }],
    })


def test_ec2_instance_requires_imdsv2():
    app = core.App()
    stack = AwsCdkResourceCreationStack(app, "aws-cdk-resource-creation")
    template = assertions.Template.from_stack(stack)

    template.has_resource_properties("AWS::EC2::LaunchTemplate", {
        "LaunchTemplateData": {"MetadataOptions": {"HttpTokens": "required"}},
    })


def test_ec2_instance_has_no_inbound_access():
    app = core.App()
    stack = AwsCdkResourceCreationStack(app, "aws-cdk-resource-creation")
    template = assertions.Template.from_stack(stack)

    template.has_resource_properties("AWS::EC2::SecurityGroup", {
        "SecurityGroupIngress": assertions.Match.absent(),
    })
    template.resource_count_is("AWS::EC2::SecurityGroupIngress", 0)


def test_vpc_has_no_nat_gateway():
    app = core.App()
    stack = AwsCdkResourceCreationStack(app, "aws-cdk-resource-creation")
    template = assertions.Template.from_stack(stack)

    template.resource_count_is("AWS::EC2::VPC", 1)
    template.resource_count_is("AWS::EC2::NatGateway", 0)
