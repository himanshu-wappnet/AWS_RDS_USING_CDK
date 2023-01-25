#!/usr/bin/env python3
##
# This code helps to do the below functionality
#   - Create the Lamda function(Python)
#   - Create the RDS(Mysql)
#   - Grant the permission from s3 to lamda
#

from aws_cdk import (
    aws_lambda as _lambda,
    aws_s3 as _s3,
    aws_ec2 as ec2,
    aws_s3_notifications,
    aws_rds as rds,
    aws_secretsmanager as sm,
    RemovalPolicy, Duration, Stack

)
import json
from aws_cdk.aws_iam import User
from constructs import Construct


class S3LamdaRDSStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, props , **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Adding the pymsql package used for pushing the data to RDS
        pymysql_layer = _lambda.LayerVersion(
            self, "pymysql",
            code=_lambda.AssetCode('layers/pymysql.zip'))

        # Create Lamda function with python 3.7
        # Load the python file from ./lamda folder
        lamd_function = _lambda.Function(self, "lambda_function",
                                    runtime=_lambda.Runtime.PYTHON_3_7,
                                    handler="push_to_sql.main",
                                    layers=[ pymysql_layer ],
                                    code=_lambda.Code.from_asset("./lambda"))
        
        # Create s3 bucket 
        s3_bucket = _s3.Bucket(
            self, "Bucket",
            bucket_name=f"lamda-mysql",
            versioned=False,
            removal_policy=RemovalPolicy.DESTROY 
        )
        # Create s3 notification for lambda function
        notification = aws_s3_notifications.LambdaDestination(lamd_function)

        # assign notification for the s3 event type (ex: OBJECT_CREATED)
        s3_bucket.add_event_notification(_s3.EventType.OBJECT_CREATED, notification)
        # Grant permission to lamda function 
        s3_bucket.grant_read_write(lamd_function)

        # Create Secrets in secrets manager to store the mysql Master password
        db_master_username = {
            "db-master-username": props['db_master_username']
        }
        secret = sm.Secret(self,
                            "db-user-password-secret",
                            description="db master user password",
                            secret_name="db-master-user-password",
                            generate_secret_string=sm.SecretStringGenerator(
                                secret_string_template=json.dumps(db_master_username),
                                generate_string_key="db-master-user-password",
                                exclude_characters = " %+~`#$&*()|[]{}:;<>?!'/@\"\\",
                            )
        )

        # Creste the MYSQL database with t2.micro free tier instance.
        db_inst = rds.CfnDBInstance(
            self,
            "rds-instance",
            engine=props['db_instance_engine'],
            db_subnet_group_name="sgp-rds-db",
            db_instance_identifier=props['db_instance_identifier'],
            db_instance_class="db.t2.micro",
            deletion_protection=False,
            vpc_security_groups=[props['db_sg_id']],
            allocated_storage="20",
            master_username=props['db_master_username'],
            master_user_password=secret.secret_value_from_json("db-master-user-password").to_string(),
            db_name=props['db_name'],
            publicly_accessible=True,    
        )
        # Add the environment variable to the lamda function which will be used for RDS query
        lamd_function.add_environment("db_endpoint",db_inst.attr_endpoint_address)
        lamd_function.add_environment("db_username",props['db_master_username'])
        lamd_function.add_environment("db_password",secret.secret_value_from_json("db-master-user-password").to_string())
        lamd_function.add_environment("db_name",props['db_name'])
        
