from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_iam as iam,
)
from constructs import Construct

class ServerStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, vpc: ec2.IVpc, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        instance_role = iam.Role(
            self, "InstanceSSM",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
        )
        instance_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore")
        )

        self.web_sg = ec2.SecurityGroup(
            self, "WebSG",
            vpc=vpc,
            allow_all_outbound=True
        )
        self.web_sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(80), "Allow HTTP traffic")

        for i in range(len(vpc.public_subnets)):
            ec2.Instance(self, f"WebInstance{i + 1}",
                instance_type=ec2.InstanceType("t2.micro"),
                machine_image=ec2.AmazonLinuxImage(),
                vpc=vpc,
                vpc_subnets=ec2.SubnetSelection(
                    subnets=[vpc.public_subnets[i]],
                ),
                role=instance_role,
                security_group=self.web_sg
            )
