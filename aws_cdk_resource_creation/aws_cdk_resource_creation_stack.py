from constructs import Construct
from aws_cdk import (
    CfnOutput,
    Duration,
    Stack,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_sqs as sqs,
    aws_sns as sns,
    aws_sns_subscriptions as subs,
)


class AwsCdkResourceCreationStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        queue = sqs.Queue(
            self, "AwsCdkResourceCreationQueue",
            visibility_timeout=Duration.seconds(300),
        )

        topic = sns.Topic(
            self, "AwsCdkResourceCreationTopic"
        )

        topic.add_subscription(subs.SqsSubscription(queue))

        # Public subnets only, which avoids NAT gateway charges.
        vpc = ec2.Vpc(
            self, "AwsCdkResourceCreationVpc",
            max_azs=2,
            nat_gateways=0,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="Public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24,
                ),
            ],
        )

        # No inbound rules: connect through SSM Session Manager instead of SSH.
        security_group = ec2.SecurityGroup(
            self, "AwsCdkResourceCreationInstanceSecurityGroup",
            vpc=vpc,
            description="EC2 instance with outbound access only",
            allow_all_outbound=True,
        )

        instance = ec2.Instance(
            self, "AwsCdkResourceCreationInstance",
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.T3,
                ec2.InstanceSize.MICRO,
            ),
            machine_image=ec2.MachineImage.latest_amazon_linux2023(),
            security_group=security_group,
            ssm_session_permissions=True,
            require_imdsv2=True,
            block_devices=[
                ec2.BlockDevice(
                    device_name="/dev/xvda",
                    volume=ec2.BlockDeviceVolume.ebs(
                        8,
                        encrypted=True,
                        volume_type=ec2.EbsDeviceVolumeType.GP3,
                    ),
                ),
            ],
        )

        CfnOutput(self, "InstanceId", value=instance.instance_id)
        CfnOutput(
            self, "ConnectCommand",
            value=f"aws ssm start-session --target {instance.instance_id} --region {self.region}",
        )
