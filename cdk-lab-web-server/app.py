#!/usr/bin/env python3
import aws_cdk as cdk

from network_stack import NetworkStack
from server_stack import ServerStack
from rds_stack import RDSStack

app = cdk.App()

# Specify the AWS Account and Region
env = cdk.Environment(account="911167900137", region="us-east-1")

# Create the network stack
network_stack = NetworkStack(app, "NetworkStack", env=env)

# Create the server stack using the VPC from the network stack
server_stack = ServerStack(app, "ServerStack", vpc=network_stack.vpc, env=env)

# Create the RDS stack, passing the VPC and security group from the server stack
rds_stack = RDSStack(app, "RDSStack", vpc=network_stack.vpc, web_sg=server_stack.web_sg, env=env)

# Synthesize the app
app.synth()
