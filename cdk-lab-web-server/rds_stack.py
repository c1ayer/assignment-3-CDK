from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_rds as rds,
)
from constructs import Construct

class RDSStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, vpc: ec2.IVpc, web_sg: ec2.ISecurityGroup, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        rds_sg = ec2.SecurityGroup(
            self, "RDSSG",
            vpc=vpc,
            allow_all_outbound=True
        )
        rds_sg.add_ingress_rule(web_sg, ec2.Port.tcp(3306), "Allow MySQL traffic from web servers")

        rds.DatabaseInstance(self, "RDSInstance",
            engine=rds.DatabaseInstanceEngine.mysql(version=rds.MysqlEngineVersion.VER_8_0_32), 
            instance_type=ec2.InstanceType.of(ec2.InstanceClass.BURSTABLE3, ec2.InstanceSize.MICRO), 
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
            security_groups=[rds_sg]
        )
