from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_rds as rds,
    aws_iam as iam,
)
from constructs import Construct

class NetworkStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.vpc = ec2.Vpc(
            self, "cdk_lab_vpc",
            ip_addresses=ec2.IpAddresses.cidr("10.0.0.0/16"),
            max_azs=2, 
            subnet_configuration=[
                ec2.SubnetConfiguration(name="PublicSubnet01", subnet_type=ec2.SubnetType.PUBLIC),
                ec2.SubnetConfiguration(name="PrivateSubnet01", subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT),
                ec2.SubnetConfiguration(name="PublicSubnet02", subnet_type=ec2.SubnetType.PUBLIC),
                ec2.SubnetConfiguration(name="PrivateSubnet02", subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT)
            ]
        )

class ServerStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, vpc, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        instance_role = iam.Role(
            self, "InstanceSSM",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
        )
        instance_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore")
        )

        web_sg = ec2.SecurityGroup(
            self, "WebSG",
            vpc=vpc,
            allow_all_outbound=True
        )
        web_sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(80), "Allow HTTP traffic")

        ec2.Instance(self, "WebInstance01",
            instance_type=ec2.InstanceType("t2.micro"),
            machine_image=ec2.AmazonLinuxImage(),
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC, availability_zone=vpc.availability_zones[0]),
            role=instance_role,
            security_group=web_sg
        )

        ec2.Instance(self, "WebInstance02",
            instance_type=ec2.InstanceType("t2.micro"),
            machine_image=ec2.AmazonLinuxImage(),
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC, availability_zone=vpc.availability_zones[1]),
            role=instance_role,
            security_group=web_sg
        )

class RDSStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, vpc, web_sg, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        rds_sg = ec2.SecurityGroup(
            self, "RDSSG",
            vpc=vpc,
            allow_all_outbound=True
        )
        rds_sg.add_ingress_rule(web_sg, ec2.Port.tcp(3306), "Allow MySQL traffic from web server")

        rds.DatabaseInstance(self, "RDSInstance",
            engine=rds.DatabaseInstanceEngine.mysql(version=rds.MysqlEngineVersion.VER_8_0_21),
            instance_type=ec2.InstanceType.of(ec2.InstanceClass.BURSTABLE2, ec2.InstanceSize.MICRO),
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT),
            security_groups=[rds_sg]
        )
