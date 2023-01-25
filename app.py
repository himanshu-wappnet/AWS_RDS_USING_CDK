#!/usr/bin/env python3
##
#
# The AWS CDK stack APP does the below function
#   - Create the VPC with two public subnet
#   - Create the Lamda function(Python)
#   - Create the RDS(Mysql)
#   - Grant the permission from s3 to lamda
#

import aws_cdk as cdk
from s3_lamda_rds.s3_lamda_rds_stack import S3LamdaRDSStack
from s3_lamda_rds.vpc_stack import vpcStack


props = {
            'vpc_name':'vpc-rds',
            'db_name': 'newdatabase',
            'db_master_username': 'admin',
            'db_instance_identifier':'dbinstance',
            'db_instance_engine':'MYSQL'
        }

app = cdk.App()
vpcStack = vpcStack(app, "vpcStack", 
                    props, 
                    env=cdk.Environment(account='810833458562', 
                                        region='ap-south-1'),
                    )
S3LamdaRDSStack(app, "S3LamdaRDSStack",
                vpcStack.output_props,
                env=cdk.Environment(account='810833458562', 
                                    region='ap-south-1'),
                )

app.synth()
