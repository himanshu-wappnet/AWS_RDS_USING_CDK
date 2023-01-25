#!/usr/bin/env python3
##
# This code helps to do the below functionality
#   - Create the VPC
#   - Create the Subnet
#   - Create the IG
#   - Create the Route Table
#   - Attach the ID
#   - Create the Security Group

from aws_cdk import CfnOutput, Stack
from constructs import Construct
from aws_cdk import (
    aws_ec2 as ec2,
    aws_rds as rds,
)
class vpcStack(Stack):

    def __init__(self, scope: Construct, id: str, props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create VPC
        vpc = ec2.CfnVPC(
            self,
            "vpcStack",
            cidr_block="10.0.0.0/16",
            enable_dns_hostnames = True,
            enable_dns_support = True,
        )
        vpc.tags.set_tag(key="Name",value=props['vpc_name'])


        # Create Route Table
        route_table_public = ec2.CfnRouteTable(
            self,
            "rtb-public",
            vpc_id=vpc.ref
        )
        route_table_public.tags.set_tag(key="Name",value="RDS Public Routing Table")

        # Create first public subnet
        public_subnet_1 = ec2.CfnSubnet(
            self,
            "public_subnet_1",
            cidr_block="10.0.0.0/24",
            vpc_id=vpc.ref,
            map_public_ip_on_launch=True,
            availability_zone="ap-south-1a"
        )

        # Create Second public subnet
        public_subnet_2 = ec2.CfnSubnet(
            self,
            "public_subnet_2",
            cidr_block="10.0.1.0/24",
            vpc_id=vpc.ref,
            map_public_ip_on_launch=True,
            availability_zone="ap-south-1b"
        )
        # Create internet gateway
        inet_gateway = ec2.CfnInternetGateway(
            self,
            "rds-igw",
        )
        inet_gateway.tags.set_tag(key="Name",value="rds-igw")
        
        # Attach internet gateway to vpc
        ec2.CfnVPCGatewayAttachment(
            self,
            "igw-attachment",
            vpc_id=vpc.ref,
            internet_gateway_id=inet_gateway.ref
        )

        # Create a new public route to use the internet gateway
        ec2.CfnRoute(
            self,
            "public-route",
            route_table_id=route_table_public.ref,
            gateway_id=inet_gateway.ref,
            destination_cidr_block="0.0.0.0/0",
        
        )

        # Create RDS subnet group
        rds.CfnDBSubnetGroup(
            self,
            "rds_db_subnet_group",
            db_subnet_group_description="RDS DB Subnet Group",
            db_subnet_group_name="sgp-rds-db",
            subnet_ids=[public_subnet_1.ref, public_subnet_2.ref],
        )

        ec2.CfnSubnetRouteTableAssociation(
            self,
            "rtb-assoc-public-1",
            route_table_id=route_table_public.ref,
            subnet_id=public_subnet_1.ref
        )

        ec2.CfnSubnetRouteTableAssociation(
            self,
            "rtb-assoc-public-2",
            route_table_id=route_table_public.ref,
            subnet_id=public_subnet_2.ref
        )

        # Create security group for the RDS instance
        db_sec_group = ec2.CfnSecurityGroup(
            self,
            "dbserver-sec-group",
            group_description="DB Instance Security Group",
            vpc_id=vpc.ref
        )

        db_sec_group.tags.set_tag(key="Name",value="sg-rds-db")

        # Allow port 3306 to public in order to access MySQL from lamda
        # Not recommended for production
        db_ingress = ec2.CfnSecurityGroupIngress(
            self,
            "sec-group-db-ingress",
            ip_protocol="tcp",
            from_port=3306,
            to_port=3306,
            group_id=db_sec_group.ref,
            cidr_ip="0.0.0.0/0",
        )
        self.output_props = props.copy()
        self.output_props['vpc_id'] = vpc.ref
        self.output_props['db_sg_id'] = db_sec_group.ref


        CfnOutput(self, "Output",
                       value=vpc.ref)

    @property
    def outputs(self):
        return self.output_props
