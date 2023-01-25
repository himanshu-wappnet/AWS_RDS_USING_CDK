import aws_cdk as core
import aws_cdk.assertions as assertions

from s3_lamda_rds.s3_lamda_rds_stack import S3LamdaRdsStack

# example tests. To run these tests, uncomment this file along with the example
# resource in s3_lamda_rds/s3_lamda_rds_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = S3LamdaRdsStack(app, "s3-lamda-rds")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
