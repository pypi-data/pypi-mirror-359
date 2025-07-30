from typing import List

from cdk_tutor.challenges import Challenge

# Sample S3 Bucket challenge
S3_BUCKET_CHALLENGE = Challenge(
    name="S3 Bucket Basics",
    description="Create a simple S3 bucket with website hosting enabled",
    difficulty="beginner",
    instructions="""
# S3 Bucket Basics

In this challenge, you'll create a simple S3 bucket with website hosting enabled.

## Task

Open the `app.py` file and complete the `S3WebsiteBucketStack` class:

1. Create an S3 bucket with the ID "WebsiteBucket"
2. Enable website hosting on the bucket
3. Configure the index document to "index.html"
4. Make the bucket publicly readable

## Testing

Once you've implemented the solution, run:

```
cdk-tutor grade .
```

## Hints

- Look at the AWS CDK documentation for S3 buckets
- The `website_index_document` parameter can be used to enable website hosting
- Use the `public_read_access` parameter to make the bucket publicly readable
""",
    expected_cf_template={
        "Resources": {
            "WebsiteBucket75C24D94": {
                "Type": "AWS::S3::Bucket",
                "Properties": {
                    "WebsiteConfiguration": {"IndexDocument": "index.html"},
                    "PublicAccessBlockConfiguration": {
                        "BlockPublicAcls": False,
                        "BlockPublicPolicy": False,
                        "IgnorePublicAcls": False,
                        "RestrictPublicBuckets": False,
                    },
                },
                "UpdateReplacePolicy": "Delete",
                "DeletionPolicy": "Delete",
            },
            "WebsiteBucketPolicyE10E3262": {
                "Type": "AWS::S3::BucketPolicy",
                "Properties": {
                    "Bucket": {"Ref": "WebsiteBucket75C24D94"},
                    "PolicyDocument": {
                        "Statement": [
                            {
                                "Action": "s3:GetObject",
                                "Effect": "Allow",
                                "Principal": {"AWS": "*"},
                                "Resource": {
                                    "Fn::Join": [
                                        "",
                                        [
                                            {
                                                "Fn::GetAtt": [
                                                    "WebsiteBucket75C24D94",
                                                    "Arn",
                                                ]
                                            },
                                            "/*",
                                        ],
                                    ]
                                },
                            }
                        ],
                        "Version": "2012-10-17",
                    },
                },
            },
        },
        "Outputs": {
            "WebsiteBucketUrl": {
                "Value": {"Fn::GetAtt": ["WebsiteBucket75C24D94", "WebsiteURL"]}
            }
        },
    },
    starter_code_files={
        "app.py": """#!/usr/bin/env python3
import aws_cdk as cdk
from aws_cdk import (
    aws_s3 as s3,
    Stack,
    CfnOutput
)
from constructs import Construct

class S3WebsiteBucketStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # TODO: Create an S3 bucket with website hosting enabled
        # - The bucket construct should have the ID "WebsiteBucket"
        # - Enable website hosting with index.html as the index document
        # - Make the bucket publicly readable
        
        # TODO: Add an output for the website URL

app = cdk.App()
S3WebsiteBucketStack(app, "S3WebsiteBucketStack")
app.synth()
""",
        "requirements.txt": """aws-cdk-lib>=2.0.0
constructs>=10.0.0
""",
    },
    next_challenge="Lambda Function",
)

# Sample Lambda challenge
LAMBDA_CHALLENGE = Challenge(
    name="Lambda Function",
    description="Create a Lambda function that returns a greeting message",
    difficulty="beginner",
    instructions="""
# Lambda Function Basics

In this challenge, you'll create a Lambda function that returns a greeting message.

## Task

Open the `app.py` file and complete the `LambdaStack` class:

1. Create a Lambda function with the ID "GreetingFunction"
2. Use the Python 3.10 runtime
3. The handler should be "index.handler"
4. The code should be in the "lambda" directory (already provided)
5. Make the function publicly accessible via an API Gateway

## Testing

Once you've implemented the solution, run:

```
cdk-tutor grade .
```

## Hints

- Look at the AWS CDK documentation for Lambda functions
- Use the `Runtime.PYTHON_3_10` for the Python 3.10 runtime
- Use `Code.from_asset()` to include the code from the "lambda" directory
- Use `LambdaRestApi` to create an API Gateway endpoint for the Lambda function
""",
    expected_cf_template={
        "Resources": {
            "GreetingFunctionServiceRoleDFC585EB": {
                "Type": "AWS::IAM::Role",
                "Properties": {
                    "AssumeRolePolicyDocument": {
                        "Statement": [
                            {
                                "Action": "sts:AssumeRole",
                                "Effect": "Allow",
                                "Principal": {"Service": "lambda.amazonaws.com"},
                            }
                        ],
                        "Version": "2012-10-17",
                    },
                    "ManagedPolicyArns": [
                        {
                            "Fn::Join": [
                                "",
                                [
                                    "arn:",
                                    {"Ref": "AWS::Partition"},
                                    ":iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
                                ],
                            ]
                        }
                    ],
                },
            },
            "GreetingFunction16D8FDDB": {
                "Type": "AWS::Lambda::Function",
                "Properties": {
                    "Code": {
                        "S3Bucket": {
                            "Fn::Sub": "cdk-hnb659fds-assets-${AWS::AccountId}-${AWS::Region}"
                        },
                        "S3Key": "911e8dd0d356b73464b98106a42179efa99a16cd780d313852c1415f275bca9e.zip",
                    },
                    "Handler": "index.handler",
                    "Role": {
                        "Fn::GetAtt": ["GreetingFunctionServiceRoleDFC585EB", "Arn"]
                    },
                    "Runtime": "python3.10",
                },
                "DependsOn": ["GreetingFunctionServiceRoleDFC585EB"],
            },
            "LambdaApi728714DB": {
                "Type": "AWS::ApiGateway::RestApi",
                "Properties": {"Name": "LambdaApi"},
            },
            "LambdaApiCloudWatchRole3EE5D16F": {
                "Type": "AWS::IAM::Role",
                "Properties": {
                    "AssumeRolePolicyDocument": {
                        "Statement": [
                            {
                                "Action": "sts:AssumeRole",
                                "Effect": "Allow",
                                "Principal": {"Service": "apigateway.amazonaws.com"},
                            }
                        ],
                        "Version": "2012-10-17",
                    },
                    "ManagedPolicyArns": [
                        {
                            "Fn::Join": [
                                "",
                                [
                                    "arn:",
                                    {"Ref": "AWS::Partition"},
                                    ":iam::aws:policy/service-role/AmazonAPIGatewayPushToCloudWatchLogs",
                                ],
                            ]
                        }
                    ],
                },
                "UpdateReplacePolicy": "Retain",
                "DeletionPolicy": "Retain",
            },
            "LambdaApiAccountF5D5B28A": {
                "Type": "AWS::ApiGateway::Account",
                "Properties": {
                    "CloudWatchRoleArn": {
                        "Fn::GetAtt": ["LambdaApiCloudWatchRole3EE5D16F", "Arn"]
                    }
                },
                "DependsOn": ["LambdaApi728714DB"],
                "UpdateReplacePolicy": "Retain",
                "DeletionPolicy": "Retain",
            },
            "LambdaApiDeployment415810029dfe2f3a20b8ef3bdefa27ea05354bfa": {
                "Type": "AWS::ApiGateway::Deployment",
                "Properties": {
                    "Description": "Automatically created by the RestApi construct",
                    "RestApiId": {"Ref": "LambdaApi728714DB"},
                },
                "DependsOn": ["LambdaApiGETD67BA188"],
            },
            "LambdaApiDeploymentStageprod51A299C1": {
                "Type": "AWS::ApiGateway::Stage",
                "Properties": {
                    "DeploymentId": {
                        "Ref": "LambdaApiDeployment415810029dfe2f3a20b8ef3bdefa27ea05354bfa"
                    },
                    "RestApiId": {"Ref": "LambdaApi728714DB"},
                    "StageName": "prod",
                },
                "DependsOn": ["LambdaApiAccountF5D5B28A"],
            },
            "LambdaApiGETApiPermissionLambdaStackLambdaApi07B37B96GET6C06573C": {
                "Type": "AWS::Lambda::Permission",
                "Properties": {
                    "Action": "lambda:InvokeFunction",
                    "FunctionName": {"Fn::GetAtt": ["GreetingFunction16D8FDDB", "Arn"]},
                    "Principal": "apigateway.amazonaws.com",
                    "SourceArn": {
                        "Fn::Join": [
                            "",
                            [
                                "arn:",
                                {"Ref": "AWS::Partition"},
                                ":execute-api:",
                                {"Ref": "AWS::Region"},
                                ":",
                                {"Ref": "AWS::AccountId"},
                                ":",
                                {"Ref": "LambdaApi728714DB"},
                                "/",
                                {"Ref": "LambdaApiDeploymentStageprod51A299C1"},
                                "/GET/",
                            ],
                        ]
                    },
                },
            },
            "LambdaApiGETApiPermissionTestLambdaStackLambdaApi07B37B96GETB878CEF2": {
                "Type": "AWS::Lambda::Permission",
                "Properties": {
                    "Action": "lambda:InvokeFunction",
                    "FunctionName": {"Fn::GetAtt": ["GreetingFunction16D8FDDB", "Arn"]},
                    "Principal": "apigateway.amazonaws.com",
                    "SourceArn": {
                        "Fn::Join": [
                            "",
                            [
                                "arn:",
                                {"Ref": "AWS::Partition"},
                                ":execute-api:",
                                {"Ref": "AWS::Region"},
                                ":",
                                {"Ref": "AWS::AccountId"},
                                ":",
                                {"Ref": "LambdaApi728714DB"},
                                "/test-invoke-stage/GET/",
                            ],
                        ]
                    },
                },
            },
            "LambdaApiGETD67BA188": {
                "Type": "AWS::ApiGateway::Method",
                "Properties": {
                    "AuthorizationType": "NONE",
                    "HttpMethod": "GET",
                    "Integration": {
                        "IntegrationHttpMethod": "POST",
                        "Type": "AWS_PROXY",
                        "Uri": {
                            "Fn::Join": [
                                "",
                                [
                                    "arn:",
                                    {"Ref": "AWS::Partition"},
                                    ":apigateway:",
                                    {"Ref": "AWS::Region"},
                                    ":lambda:path/2015-03-31/functions/",
                                    {"Fn::GetAtt": ["GreetingFunction16D8FDDB", "Arn"]},
                                    "/invocations",
                                ],
                            ]
                        },
                    },
                    "ResourceId": {
                        "Fn::GetAtt": ["LambdaApi728714DB", "RootResourceId"]
                    },
                    "RestApiId": {"Ref": "LambdaApi728714DB"},
                },
            },
        },
        "Outputs": {
            "LambdaApiEndpointB01FF32A": {
                "Value": {
                    "Fn::Join": [
                        "",
                        [
                            "https://",
                            {"Ref": "LambdaApi728714DB"},
                            ".execute-api.",
                            {"Ref": "AWS::Region"},
                            ".",
                            {"Ref": "AWS::URLSuffix"},
                            "/",
                            {"Ref": "LambdaApiDeploymentStageprod51A299C1"},
                            "/",
                        ],
                    ]
                }
            },
            "ApiEndpointURL": {
                "Value": {
                    "Fn::Join": [
                        "",
                        [
                            "https://",
                            {"Ref": "LambdaApi728714DB"},
                            ".execute-api.",
                            {"Ref": "AWS::Region"},
                            ".",
                            {"Ref": "AWS::URLSuffix"},
                            "/",
                            {"Ref": "LambdaApiDeploymentStageprod51A299C1"},
                            "/",
                        ],
                    ]
                }
            },
        },
    },
    starter_code_files={
        "app.py": """#!/usr/bin/env python3
import aws_cdk as cdk
from aws_cdk import (
    aws_lambda as lambda_,
    aws_apigateway as apigw,
    Stack,
    CfnOutput
)
from constructs import Construct

class LambdaStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # TODO: Create a Lambda function
        # - The function construct should have the ID "GreetingFunction"
        # - Use the Python 3.10 runtime
        # - The handler should be "index.handler"
        # - The code should be in the "lambda" directory
        
        # TODO: Create an API Gateway REST API for the Lambda function. Use "LambdaApi" as the construct ID.
        
        # TODO: Add a `GET /` endpoint to the API Gateway
        
        # TODO: Add an output for the API endpoint URL

app = cdk.App()
LambdaStack(app, "LambdaStack")
app.synth()
""",
        "lambda/index.py": """def handler(event, context):
    return {
        "statusCode": 200,
        "headers": { "Content-Type": "application/json" },
        "body": json.dumps({
            "message": "Hello from Lambda! Your CDK skills are growing!"
        })
    }
""",
        "requirements.txt": """aws-cdk-lib>=2.0.0
constructs>=10.0.0
""",
    },
    next_challenge="DynamoDB Table",
)

# DynamoDB Table Challenge
DYNAMODB_CHALLENGE = Challenge(
    name="DynamoDB Table",
    description="Create a DynamoDB table with partition and sort keys",
    difficulty="beginner",
    instructions="""
# DynamoDB Table Challenge

In this challenge, you'll create a DynamoDB table for storing user orders.

## Task

Open the `app.py` file and complete the `DynamoDBStack` class:

1. Create a DynamoDB table with the ID "OrdersTable"
2. Configure the partition key as "userId" of type string
3. Configure the sort key as "orderId" of type string
4. Enable point-in-time recovery for the table
5. Set the billing mode to PAY_PER_REQUEST (on-demand)
6. Add a Global Secondary Index (GSI) named "OrderDateIndex" with:
   - Partition key: "status" (string)
   - Sort key: "orderDate" (string)
7. Add an output for the table name with the ID `TableName`

## Testing

Once you've implemented the solution, run:

```
cdk-tutor grade .
```

## Hints

- Use `aws_dynamodb.Table` to create the DynamoDB table
- Set `partition_key` and `sort_key` parameters with `aws_dynamodb.Attribute`
- Use `billing_mode=aws_dynamodb.BillingMode.PAY_PER_REQUEST` for on-demand billing
- Set `point_in_time_recovery=True` to enable point-in-time recovery
- Use the `add_global_secondary_index` method to add the GSI
""",
    expected_cf_template={
        "Resources": {
            "OrdersTable315BB997": {
                "Type": "AWS::DynamoDB::Table",
                "Properties": {
                    "AttributeDefinitions": [
                        {"AttributeName": "userId", "AttributeType": "S"},
                        {"AttributeName": "orderId", "AttributeType": "S"},
                        {"AttributeName": "status", "AttributeType": "S"},
                        {"AttributeName": "orderDate", "AttributeType": "S"},
                    ],
                    "BillingMode": "PAY_PER_REQUEST",
                    "GlobalSecondaryIndexes": [
                        {
                            "IndexName": "OrderDateIndex",
                            "KeySchema": [
                                {"AttributeName": "status", "KeyType": "HASH"},
                                {"AttributeName": "orderDate", "KeyType": "RANGE"},
                            ],
                            "Projection": {"ProjectionType": "ALL"},
                        }
                    ],
                    "KeySchema": [
                        {"AttributeName": "userId", "KeyType": "HASH"},
                        {"AttributeName": "orderId", "KeyType": "RANGE"},
                    ],
                    "PointInTimeRecoverySpecification": {
                        "PointInTimeRecoveryEnabled": True
                    },
                },
                "UpdateReplacePolicy": "Retain",
                "DeletionPolicy": "Retain",
            },
        },
        "Outputs": {"TableName": {"Value": {"Ref": "OrdersTable315BB997"}}},
    },
    starter_code_files={
        "app.py": """#!/usr/bin/env python3
import aws_cdk as cdk
from aws_cdk import (
    aws_dynamodb as dynamodb,
    Stack,
    CfnOutput
)
from constructs import Construct

class DynamoDBStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # TODO: Create a DynamoDB table for orders
        # - The table should have the ID "OrdersTable"
        # - Set the partition key to "userId" (string)
        # - Set the sort key to "orderId" (string)
        # - Enable point-in-time recovery
        # - Set the billing mode to PAY_PER_REQUEST
        # - Add a Global Secondary Index named "OrderDateIndex" with:
        #   - Partition key: "status" (string)
        #   - Sort key: "orderDate" (string)
        
        # TODO: Add an output for the table name

app = cdk.App()
DynamoDBStack(app, "DynamoDBStack")
app.synth()
""",
        "requirements.txt": """aws-cdk-lib>=2.0.0
constructs>=10.0.0
""",
    },
    next_challenge="SNS Topic and SQS Queue",
)

# SNS Topic and SQS Queue Challenge
SNS_SQS_CHALLENGE = Challenge(
    name="SNS Topic and SQS Queue",
    description="Create an SNS topic with an SQS queue subscription",
    difficulty="intermediate",
    instructions="""
# SNS Topic and SQS Queue Challenge

In this challenge, you'll create an SNS topic with an SQS queue subscription for event-driven architectures.

## Task

Open the `app.py` file and complete the `MessagingStack` class:

1. Create an SNS topic with the ID "NotificationTopic"
2. Create an SQS queue with the ID "ProcessingQueue"
   - Configure the queue with a visibility timeout of 60 seconds
   - Enable dead-letter queue with max receives set to 3
3. Subscribe the SQS queue to the SNS topic
4. Add appropriate outputs for both the topic ARN with the ID `NotificationTopicArn` and queue URL with the ID `ProcessingQueueUrl`

## Testing

Once you've implemented the solution, run:

```
cdk-tutor grade .
```

## Hints

- Use `aws_sns.Topic` to create the SNS topic
- Use `aws_sqs.Queue` to create the SQS queue
- Create a dead-letter queue first with the ID `DeadLetterQueue`, then reference it when creating the main queue
- Use `aws_sns_subscriptions.SqsSubscription` to subscribe the queue to the topic
- Remember to grant the SNS topic permission to send messages to the queue
""",
    expected_cf_template={
        "Resources": {
            "NotificationTopicEB7A0DF1": {
                "Type": "AWS::SNS::Topic",
                "Properties": {"DisplayName": "Notification Topic"},
            },
            "DeadLetterQueue9F481546": {
                "Type": "AWS::SQS::Queue",
                "UpdateReplacePolicy": "Delete",
                "DeletionPolicy": "Delete",
            },
            "ProcessingQueue6DC600C3": {
                "Type": "AWS::SQS::Queue",
                "Properties": {
                    "RedrivePolicy": {
                        "deadLetterTargetArn": {
                            "Fn::GetAtt": ["DeadLetterQueue9F481546", "Arn"]
                        },
                        "maxReceiveCount": 3,
                    },
                    "VisibilityTimeout": 60,
                },
                "UpdateReplacePolicy": "Delete",
                "DeletionPolicy": "Delete",
            },
            "ProcessingQueuePolicyDDFFDBBA": {
                "Type": "AWS::SQS::QueuePolicy",
                "Properties": {
                    "PolicyDocument": {
                        "Statement": [
                            {
                                "Action": "sqs:SendMessage",
                                "Condition": {
                                    "ArnEquals": {
                                        "aws:SourceArn": {
                                            "Ref": "NotificationTopicEB7A0DF1"
                                        }
                                    }
                                },
                                "Effect": "Allow",
                                "Principal": {"Service": "sns.amazonaws.com"},
                                "Resource": {
                                    "Fn::GetAtt": ["ProcessingQueue6DC600C3", "Arn"]
                                },
                            }
                        ],
                        "Version": "2012-10-17",
                    },
                    "Queues": [{"Ref": "ProcessingQueue6DC600C3"}],
                },
            },
            "ProcessingQueueMessagingStackNotificationTopic9005B60C185B0AC3": {
                "Type": "AWS::SNS::Subscription",
                "Properties": {
                    "Endpoint": {"Fn::GetAtt": ["ProcessingQueue6DC600C3", "Arn"]},
                    "Protocol": "sqs",
                    "TopicArn": {"Ref": "NotificationTopicEB7A0DF1"},
                },
                "DependsOn": ["ProcessingQueuePolicyDDFFDBBA"],
            },
        },
        "Outputs": {
            "NotificationTopicArn": {"Value": {"Ref": "NotificationTopicEB7A0DF1"}},
            "ProcessingQueueUrl": {"Value": {"Ref": "ProcessingQueue6DC600C3"}},
        },
    },
    starter_code_files={
        "app.py": """#!/usr/bin/env python3
import aws_cdk as cdk
from aws_cdk import (
    aws_sns as sns,
    aws_sqs as sqs,
    aws_sns_subscriptions as subs,
    Stack,
    CfnOutput,
    Duration
)
from constructs import Construct

class MessagingStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # TODO: Create an SNS topic with "NotificationTopic" id
        
        # TODO: Create an SQS queue with "ProcessingQueue" id
        # - Set visibility timeout to 60 seconds
        # - Configure a dead-letter queue with max receives set to 3
        
        # TODO: Subscribe the SQS queue to the SNS topic
        
        # TODO: Add outputs for the topic ARN and queue URL

app = cdk.App()
MessagingStack(app, "MessagingStack")
app.synth()
""",
        "requirements.txt": """aws-cdk-lib>=2.0.0
constructs>=10.0.0
""",
    },
    next_challenge="VPC and Networking",
)

# VPC and Networking Challenge
VPC_CHALLENGE = Challenge(
    name="VPC and Networking",
    description="Create a custom VPC with public and private subnets",
    difficulty="intermediate",
    instructions="""
# VPC and Networking Challenge

In this challenge, you'll create a custom Virtual Private Cloud (VPC) with public and private subnets.

## Task

Open the `app.py` file and complete the `NetworkingStack` class:

1. Create a VPC with the ID "ApplicationVPC" that:
   - Spans 2 Availability Zones
   - Has 2 public subnets (one per AZ)
   - Has 2 private subnets (one per AZ)
   - Includes a NAT Gateway for private subnet internet access
   - Set the subnets to have a CIDR mask of /24
   - Uses custom CIDR range of "10.0.0.0/16"
2. Create a Security Group named "WebServerSecurityGroup" that:
   - Allows inbound HTTP (port 80) traffic from anywhere
   - Allows inbound HTTPS (port 443) traffic from anywhere
   - Allows SSH (port 22) only from a specific IP address (use "192.168.1.1/32")
3. Add outputs for the VPC ID and Security Group ID

## Testing

Once you've implemented the solution, run:

```
cdk-tutor grade .
```

## Hints

- Use `aws_ec2.Vpc` to create the VPC with appropriate subnet configuration
- Use `aws_ec2.SecurityGroup` to create the security group
- Use the `add_ingress_rule` method to add inbound rules to the security group
- Use `aws_ec2.Peer.ipv4()` to specify IP CIDR ranges for security group rules
""",
    expected_cf_template={
        "Resources": {
            "ApplicationVPCA4AE19E7": {
                "Type": "AWS::EC2::VPC",
                "Properties": {
                    "CidrBlock": "10.0.0.0/16",
                    "EnableDnsHostnames": True,
                    "EnableDnsSupport": True,
                    "InstanceTenancy": "default",
                    "Tags": [
                        {"Key": "Name", "Value": "NetworkingStack/ApplicationVPC"}
                    ],
                },
            },
            "ApplicationVPCPublicSubnetSubnet1Subnet982CEC7A": {
                "Type": "AWS::EC2::Subnet",
                "Properties": {
                    "AvailabilityZone": {"Fn::Select": [0, {"Fn::GetAZs": ""}]},
                    "CidrBlock": "10.0.0.0/24",
                    "MapPublicIpOnLaunch": True,
                    "Tags": [
                        {"Key": "aws-cdk:subnet-name", "Value": "PublicSubnet"},
                        {"Key": "aws-cdk:subnet-type", "Value": "Public"},
                        {
                            "Key": "Name",
                            "Value": "NetworkingStack/ApplicationVPC/PublicSubnetSubnet1",
                        },
                    ],
                    "VpcId": {"Ref": "ApplicationVPCA4AE19E7"},
                },
            },
            "ApplicationVPCPublicSubnetSubnet1RouteTable90EFEA1E": {
                "Type": "AWS::EC2::RouteTable",
                "Properties": {
                    "Tags": [
                        {
                            "Key": "Name",
                            "Value": "NetworkingStack/ApplicationVPC/PublicSubnetSubnet1",
                        }
                    ],
                    "VpcId": {"Ref": "ApplicationVPCA4AE19E7"},
                },
            },
            "ApplicationVPCPublicSubnetSubnet1RouteTableAssociation4AF32558": {
                "Type": "AWS::EC2::SubnetRouteTableAssociation",
                "Properties": {
                    "RouteTableId": {
                        "Ref": "ApplicationVPCPublicSubnetSubnet1RouteTable90EFEA1E"
                    },
                    "SubnetId": {
                        "Ref": "ApplicationVPCPublicSubnetSubnet1Subnet982CEC7A"
                    },
                },
            },
            "ApplicationVPCPublicSubnetSubnet1DefaultRouteD27E288F": {
                "Type": "AWS::EC2::Route",
                "Properties": {
                    "DestinationCidrBlock": "0.0.0.0/0",
                    "GatewayId": {"Ref": "ApplicationVPCIGWE1682340"},
                    "RouteTableId": {
                        "Ref": "ApplicationVPCPublicSubnetSubnet1RouteTable90EFEA1E"
                    },
                },
                "DependsOn": ["ApplicationVPCVPCGWEB31CD31"],
            },
            "ApplicationVPCPublicSubnetSubnet1EIP2015C4E8": {
                "Type": "AWS::EC2::EIP",
                "Properties": {
                    "Domain": "vpc",
                    "Tags": [
                        {
                            "Key": "Name",
                            "Value": "NetworkingStack/ApplicationVPC/PublicSubnetSubnet1",
                        }
                    ],
                },
            },
            "ApplicationVPCPublicSubnetSubnet1NATGatewayCF25C786": {
                "Type": "AWS::EC2::NatGateway",
                "Properties": {
                    "AllocationId": {
                        "Fn::GetAtt": [
                            "ApplicationVPCPublicSubnetSubnet1EIP2015C4E8",
                            "AllocationId",
                        ]
                    },
                    "SubnetId": {
                        "Ref": "ApplicationVPCPublicSubnetSubnet1Subnet982CEC7A"
                    },
                    "Tags": [
                        {
                            "Key": "Name",
                            "Value": "NetworkingStack/ApplicationVPC/PublicSubnetSubnet1",
                        }
                    ],
                },
                "DependsOn": [
                    "ApplicationVPCPublicSubnetSubnet1DefaultRouteD27E288F",
                    "ApplicationVPCPublicSubnetSubnet1RouteTableAssociation4AF32558",
                ],
            },
            "ApplicationVPCPublicSubnetSubnet2SubnetF8831BC8": {
                "Type": "AWS::EC2::Subnet",
                "Properties": {
                    "AvailabilityZone": {"Fn::Select": [1, {"Fn::GetAZs": ""}]},
                    "CidrBlock": "10.0.1.0/24",
                    "MapPublicIpOnLaunch": True,
                    "Tags": [
                        {"Key": "aws-cdk:subnet-name", "Value": "PublicSubnet"},
                        {"Key": "aws-cdk:subnet-type", "Value": "Public"},
                        {
                            "Key": "Name",
                            "Value": "NetworkingStack/ApplicationVPC/PublicSubnetSubnet2",
                        },
                    ],
                    "VpcId": {"Ref": "ApplicationVPCA4AE19E7"},
                },
            },
            "ApplicationVPCPublicSubnetSubnet2RouteTable89A11B28": {
                "Type": "AWS::EC2::RouteTable",
                "Properties": {
                    "Tags": [
                        {
                            "Key": "Name",
                            "Value": "NetworkingStack/ApplicationVPC/PublicSubnetSubnet2",
                        }
                    ],
                    "VpcId": {"Ref": "ApplicationVPCA4AE19E7"},
                },
            },
            "ApplicationVPCPublicSubnetSubnet2RouteTableAssociation9501C043": {
                "Type": "AWS::EC2::SubnetRouteTableAssociation",
                "Properties": {
                    "RouteTableId": {
                        "Ref": "ApplicationVPCPublicSubnetSubnet2RouteTable89A11B28"
                    },
                    "SubnetId": {
                        "Ref": "ApplicationVPCPublicSubnetSubnet2SubnetF8831BC8"
                    },
                },
            },
            "ApplicationVPCPublicSubnetSubnet2DefaultRouteFAA88B1A": {
                "Type": "AWS::EC2::Route",
                "Properties": {
                    "DestinationCidrBlock": "0.0.0.0/0",
                    "GatewayId": {"Ref": "ApplicationVPCIGWE1682340"},
                    "RouteTableId": {
                        "Ref": "ApplicationVPCPublicSubnetSubnet2RouteTable89A11B28"
                    },
                },
                "DependsOn": ["ApplicationVPCVPCGWEB31CD31"],
            },
            "ApplicationVPCPublicSubnetSubnet2EIP4EA2088F": {
                "Type": "AWS::EC2::EIP",
                "Properties": {
                    "Domain": "vpc",
                    "Tags": [
                        {
                            "Key": "Name",
                            "Value": "NetworkingStack/ApplicationVPC/PublicSubnetSubnet2",
                        }
                    ],
                },
            },
            "ApplicationVPCPublicSubnetSubnet2NATGateway0CA1DD54": {
                "Type": "AWS::EC2::NatGateway",
                "Properties": {
                    "AllocationId": {
                        "Fn::GetAtt": [
                            "ApplicationVPCPublicSubnetSubnet2EIP4EA2088F",
                            "AllocationId",
                        ]
                    },
                    "SubnetId": {
                        "Ref": "ApplicationVPCPublicSubnetSubnet2SubnetF8831BC8"
                    },
                    "Tags": [
                        {
                            "Key": "Name",
                            "Value": "NetworkingStack/ApplicationVPC/PublicSubnetSubnet2",
                        }
                    ],
                },
                "DependsOn": [
                    "ApplicationVPCPublicSubnetSubnet2DefaultRouteFAA88B1A",
                    "ApplicationVPCPublicSubnetSubnet2RouteTableAssociation9501C043",
                ],
            },
            "ApplicationVPCPrivateSubnetSubnet1Subnet2C3D04EA": {
                "Type": "AWS::EC2::Subnet",
                "Properties": {
                    "AvailabilityZone": {"Fn::Select": [0, {"Fn::GetAZs": ""}]},
                    "CidrBlock": "10.0.2.0/24",
                    "MapPublicIpOnLaunch": False,
                    "Tags": [
                        {"Key": "aws-cdk:subnet-name", "Value": "PrivateSubnet"},
                        {"Key": "aws-cdk:subnet-type", "Value": "Private"},
                        {
                            "Key": "Name",
                            "Value": "NetworkingStack/ApplicationVPC/PrivateSubnetSubnet1",
                        },
                    ],
                    "VpcId": {"Ref": "ApplicationVPCA4AE19E7"},
                },
            },
            "ApplicationVPCPrivateSubnetSubnet1RouteTable49AF9E89": {
                "Type": "AWS::EC2::RouteTable",
                "Properties": {
                    "Tags": [
                        {
                            "Key": "Name",
                            "Value": "NetworkingStack/ApplicationVPC/PrivateSubnetSubnet1",
                        }
                    ],
                    "VpcId": {"Ref": "ApplicationVPCA4AE19E7"},
                },
            },
            "ApplicationVPCPrivateSubnetSubnet1RouteTableAssociation463C9353": {
                "Type": "AWS::EC2::SubnetRouteTableAssociation",
                "Properties": {
                    "RouteTableId": {
                        "Ref": "ApplicationVPCPrivateSubnetSubnet1RouteTable49AF9E89"
                    },
                    "SubnetId": {
                        "Ref": "ApplicationVPCPrivateSubnetSubnet1Subnet2C3D04EA"
                    },
                },
            },
            "ApplicationVPCPrivateSubnetSubnet1DefaultRoute4DB67EEC": {
                "Type": "AWS::EC2::Route",
                "Properties": {
                    "DestinationCidrBlock": "0.0.0.0/0",
                    "NatGatewayId": {
                        "Ref": "ApplicationVPCPublicSubnetSubnet1NATGatewayCF25C786"
                    },
                    "RouteTableId": {
                        "Ref": "ApplicationVPCPrivateSubnetSubnet1RouteTable49AF9E89"
                    },
                },
            },
            "ApplicationVPCPrivateSubnetSubnet2SubnetE3303B14": {
                "Type": "AWS::EC2::Subnet",
                "Properties": {
                    "AvailabilityZone": {"Fn::Select": [1, {"Fn::GetAZs": ""}]},
                    "CidrBlock": "10.0.3.0/24",
                    "MapPublicIpOnLaunch": False,
                    "Tags": [
                        {"Key": "aws-cdk:subnet-name", "Value": "PrivateSubnet"},
                        {"Key": "aws-cdk:subnet-type", "Value": "Private"},
                        {
                            "Key": "Name",
                            "Value": "NetworkingStack/ApplicationVPC/PrivateSubnetSubnet2",
                        },
                    ],
                    "VpcId": {"Ref": "ApplicationVPCA4AE19E7"},
                },
            },
            "ApplicationVPCPrivateSubnetSubnet2RouteTableF27D71E9": {
                "Type": "AWS::EC2::RouteTable",
                "Properties": {
                    "Tags": [
                        {
                            "Key": "Name",
                            "Value": "NetworkingStack/ApplicationVPC/PrivateSubnetSubnet2",
                        }
                    ],
                    "VpcId": {"Ref": "ApplicationVPCA4AE19E7"},
                },
            },
            "ApplicationVPCPrivateSubnetSubnet2RouteTableAssociation57109373": {
                "Type": "AWS::EC2::SubnetRouteTableAssociation",
                "Properties": {
                    "RouteTableId": {
                        "Ref": "ApplicationVPCPrivateSubnetSubnet2RouteTableF27D71E9"
                    },
                    "SubnetId": {
                        "Ref": "ApplicationVPCPrivateSubnetSubnet2SubnetE3303B14"
                    },
                },
            },
            "ApplicationVPCPrivateSubnetSubnet2DefaultRoute7D9AE150": {
                "Type": "AWS::EC2::Route",
                "Properties": {
                    "DestinationCidrBlock": "0.0.0.0/0",
                    "NatGatewayId": {
                        "Ref": "ApplicationVPCPublicSubnetSubnet2NATGateway0CA1DD54"
                    },
                    "RouteTableId": {
                        "Ref": "ApplicationVPCPrivateSubnetSubnet2RouteTableF27D71E9"
                    },
                },
            },
            "ApplicationVPCIGWE1682340": {
                "Type": "AWS::EC2::InternetGateway",
                "Properties": {
                    "Tags": [{"Key": "Name", "Value": "NetworkingStack/ApplicationVPC"}]
                },
            },
            "ApplicationVPCVPCGWEB31CD31": {
                "Type": "AWS::EC2::VPCGatewayAttachment",
                "Properties": {
                    "InternetGatewayId": {"Ref": "ApplicationVPCIGWE1682340"},
                    "VpcId": {"Ref": "ApplicationVPCA4AE19E7"},
                },
            },
            "WebServerSecurityGroupEFBF953E": {
                "Type": "AWS::EC2::SecurityGroup",
                "Properties": {
                    "GroupDescription": "NetworkingStack/WebServerSecurityGroup",
                    "SecurityGroupEgress": [
                        {
                            "CidrIp": "0.0.0.0/0",
                            "Description": "Allow all outbound traffic by default",
                            "IpProtocol": "-1",
                        }
                    ],
                    "SecurityGroupIngress": [
                        {
                            "CidrIp": "0.0.0.0/0",
                            "Description": "from 0.0.0.0/0:80",
                            "FromPort": 80,
                            "IpProtocol": "tcp",
                            "ToPort": 80,
                        },
                        {
                            "CidrIp": "0.0.0.0/0",
                            "Description": "from 0.0.0.0/0:443",
                            "FromPort": 443,
                            "IpProtocol": "tcp",
                            "ToPort": 443,
                        },
                        {
                            "CidrIp": "192.168.1.1/32",
                            "Description": "from 192.168.1.1/32:22",
                            "FromPort": 22,
                            "IpProtocol": "tcp",
                            "ToPort": 22,
                        },
                    ],
                    "VpcId": {"Ref": "ApplicationVPCA4AE19E7"},
                },
            },
        },
        "Outputs": {
            "VpcId": {"Value": {"Ref": "ApplicationVPCA4AE19E7"}},
            "WebSecurityGroupId": {
                "Value": {"Fn::GetAtt": ["WebServerSecurityGroupEFBF953E", "GroupId"]}
            },
        },
    },
    starter_code_files={
        "app.py": """#!/usr/bin/env python3
import aws_cdk as cdk
from aws_cdk import (
    aws_ec2,
    Stack,
    CfnOutput
)
from constructs import Construct

class NetworkingStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # TODO: Create a VPC with "ApplicationVPC" id
        # - Use CIDR 10.0.0.0/16
        # - Have 2 public subnets (one per AZ) named "PublicSubnet"
        # - Have 2 private subnets (one per AZ) named "PrivateSubnet"
        # - Set the subnets to have a CIDR mask of /24
        # - Include a NAT Gateway for private subnet internet access
        
        # TODO: Create a security group with "WebServerSecurityGroup" id
        # - Allow HTTP (port 80) from anywhere
        # - Allow HTTPS (port 443) from anywhere
        # - Allow SSH (port 22) only from 192.168.1.1/32
        
        # TODO: Add outputs for VPC ID (named "VpcId") and Security Group ID (named "WebServerSecurityGroupId")

app = cdk.App()
NetworkingStack(app, "NetworkingStack")
app.synth()
""",
        "requirements.txt": """aws-cdk-lib>=2.0.0
constructs>=10.0.0
""",
    },
    next_challenge="EC2 Auto Scaling",
)

# EC2 Auto Scaling Challenge
EC2_AUTO_SCALING_CHALLENGE = Challenge(
    name="EC2 Auto Scaling",
    description="Create an EC2 Auto Scaling group with a load balancer",
    difficulty="advanced",
    instructions="""
# EC2 Auto Scaling Challenge

In this challenge, you'll create an EC2 Auto Scaling group with a load balancer to distribute traffic.

## Task

Open the `app.py` file and complete the `AutoScalingStack` class:

1. Create a VPC
2. Create an Application Load Balancer (ALB) with:
   - Internet-facing configuration
   - Security group allowing HTTP traffic (port 80)
   - HTTP listener on port 80
3. Create an Auto Scaling Group with:
   - Amazon Linux 2 AMI
   - t3.micro instance type
   - Minimum of 2 instances
   - Maximum of 4 instances
   - Desired capacity of 2 instances
   - User data to install and start Apache web server
4. Register the Auto Scaling Group as a target for the load balancer
5. Add an output for the load balancer DNS name

## Testing

Once you've implemented the solution, run:

```
cdk-tutor grade .
```

## Hints

- Use `aws_ec2.Vpc` to create the VPC (or use `ec2.Vpc.from_lookup` to use the default VPC)
- Use `aws_ec2.MachineImage.latest_amazon_linux` to get the latest Amazon Linux 2 AMI
- Use `aws_autoscaling.AutoScalingGroup` to create the Auto Scaling Group
- Use `aws_elasticloadbalancingv2.ApplicationLoadBalancer` for the ALB
- Use the `add_target` method to register the Auto Scaling Group with the load balancer
- For user data, use:
  ```
  #!/bin/bash
  yum update -y
  yum install -y httpd
  systemctl start httpd
  systemctl enable httpd
  echo '<h1>Hello from CDK Auto Scaling!</h1>' > /var/www/html/index.html
  ```
""",
    expected_cf_template={
        "Resources": {
            "DefaultVPC5503DC78": {
                "Type": "AWS::EC2::VPC",
                "Properties": {
                    "CidrBlock": "10.0.0.0/16",
                    "EnableDnsHostnames": True,
                    "EnableDnsSupport": True,
                    "InstanceTenancy": "default",
                    "Tags": [{"Key": "Name", "Value": "AutoScalingStack/DefaultVPC"}],
                },
            },
            "DefaultVPCPublicSubnet1Subnet45857342": {
                "Type": "AWS::EC2::Subnet",
                "Properties": {
                    "AvailabilityZone": {"Fn::Select": [0, {"Fn::GetAZs": ""}]},
                    "CidrBlock": "10.0.0.0/18",
                    "MapPublicIpOnLaunch": True,
                    "Tags": [
                        {"Key": "aws-cdk:subnet-name", "Value": "Public"},
                        {"Key": "aws-cdk:subnet-type", "Value": "Public"},
                        {
                            "Key": "Name",
                            "Value": "AutoScalingStack/DefaultVPC/PublicSubnet1",
                        },
                    ],
                    "VpcId": {"Ref": "DefaultVPC5503DC78"},
                },
            },
            "DefaultVPCPublicSubnet1RouteTableD432FC9A": {
                "Type": "AWS::EC2::RouteTable",
                "Properties": {
                    "Tags": [
                        {
                            "Key": "Name",
                            "Value": "AutoScalingStack/DefaultVPC/PublicSubnet1",
                        }
                    ],
                    "VpcId": {"Ref": "DefaultVPC5503DC78"},
                },
            },
            "DefaultVPCPublicSubnet1RouteTableAssociation0C4E2762": {
                "Type": "AWS::EC2::SubnetRouteTableAssociation",
                "Properties": {
                    "RouteTableId": {
                        "Ref": "DefaultVPCPublicSubnet1RouteTableD432FC9A"
                    },
                    "SubnetId": {"Ref": "DefaultVPCPublicSubnet1Subnet45857342"},
                },
            },
            "DefaultVPCPublicSubnet1DefaultRoute3A52FCAC": {
                "Type": "AWS::EC2::Route",
                "Properties": {
                    "DestinationCidrBlock": "0.0.0.0/0",
                    "GatewayId": {"Ref": "DefaultVPCIGW896174DD"},
                    "RouteTableId": {
                        "Ref": "DefaultVPCPublicSubnet1RouteTableD432FC9A"
                    },
                },
                "DependsOn": ["DefaultVPCVPCGW0B423978"],
            },
            "DefaultVPCPublicSubnet1EIP3DE2E08C": {
                "Type": "AWS::EC2::EIP",
                "Properties": {
                    "Domain": "vpc",
                    "Tags": [
                        {
                            "Key": "Name",
                            "Value": "AutoScalingStack/DefaultVPC/PublicSubnet1",
                        }
                    ],
                },
            },
            "DefaultVPCPublicSubnet1NATGateway0D561ED0": {
                "Type": "AWS::EC2::NatGateway",
                "Properties": {
                    "AllocationId": {
                        "Fn::GetAtt": [
                            "DefaultVPCPublicSubnet1EIP3DE2E08C",
                            "AllocationId",
                        ]
                    },
                    "SubnetId": {"Ref": "DefaultVPCPublicSubnet1Subnet45857342"},
                    "Tags": [
                        {
                            "Key": "Name",
                            "Value": "AutoScalingStack/DefaultVPC/PublicSubnet1",
                        }
                    ],
                },
                "DependsOn": [
                    "DefaultVPCPublicSubnet1DefaultRoute3A52FCAC",
                    "DefaultVPCPublicSubnet1RouteTableAssociation0C4E2762",
                ],
            },
            "DefaultVPCPublicSubnet2Subnet21115AAE": {
                "Type": "AWS::EC2::Subnet",
                "Properties": {
                    "AvailabilityZone": {"Fn::Select": [1, {"Fn::GetAZs": ""}]},
                    "CidrBlock": "10.0.64.0/18",
                    "MapPublicIpOnLaunch": True,
                    "Tags": [
                        {"Key": "aws-cdk:subnet-name", "Value": "Public"},
                        {"Key": "aws-cdk:subnet-type", "Value": "Public"},
                        {
                            "Key": "Name",
                            "Value": "AutoScalingStack/DefaultVPC/PublicSubnet2",
                        },
                    ],
                    "VpcId": {"Ref": "DefaultVPC5503DC78"},
                },
            },
            "DefaultVPCPublicSubnet2RouteTableFD927984": {
                "Type": "AWS::EC2::RouteTable",
                "Properties": {
                    "Tags": [
                        {
                            "Key": "Name",
                            "Value": "AutoScalingStack/DefaultVPC/PublicSubnet2",
                        }
                    ],
                    "VpcId": {"Ref": "DefaultVPC5503DC78"},
                },
            },
            "DefaultVPCPublicSubnet2RouteTableAssociationD1D339EB": {
                "Type": "AWS::EC2::SubnetRouteTableAssociation",
                "Properties": {
                    "RouteTableId": {
                        "Ref": "DefaultVPCPublicSubnet2RouteTableFD927984"
                    },
                    "SubnetId": {"Ref": "DefaultVPCPublicSubnet2Subnet21115AAE"},
                },
            },
            "DefaultVPCPublicSubnet2DefaultRoute584C6E3B": {
                "Type": "AWS::EC2::Route",
                "Properties": {
                    "DestinationCidrBlock": "0.0.0.0/0",
                    "GatewayId": {"Ref": "DefaultVPCIGW896174DD"},
                    "RouteTableId": {
                        "Ref": "DefaultVPCPublicSubnet2RouteTableFD927984"
                    },
                },
                "DependsOn": ["DefaultVPCVPCGW0B423978"],
            },
            "DefaultVPCPublicSubnet2EIPDA98A43D": {
                "Type": "AWS::EC2::EIP",
                "Properties": {
                    "Domain": "vpc",
                    "Tags": [
                        {
                            "Key": "Name",
                            "Value": "AutoScalingStack/DefaultVPC/PublicSubnet2",
                        }
                    ],
                },
            },
            "DefaultVPCPublicSubnet2NATGatewayF8AD1A18": {
                "Type": "AWS::EC2::NatGateway",
                "Properties": {
                    "AllocationId": {
                        "Fn::GetAtt": [
                            "DefaultVPCPublicSubnet2EIPDA98A43D",
                            "AllocationId",
                        ]
                    },
                    "SubnetId": {"Ref": "DefaultVPCPublicSubnet2Subnet21115AAE"},
                    "Tags": [
                        {
                            "Key": "Name",
                            "Value": "AutoScalingStack/DefaultVPC/PublicSubnet2",
                        }
                    ],
                },
                "DependsOn": [
                    "DefaultVPCPublicSubnet2DefaultRoute584C6E3B",
                    "DefaultVPCPublicSubnet2RouteTableAssociationD1D339EB",
                ],
            },
            "DefaultVPCPrivateSubnet1Subnet69F61BC0": {
                "Type": "AWS::EC2::Subnet",
                "Properties": {
                    "AvailabilityZone": {"Fn::Select": [0, {"Fn::GetAZs": ""}]},
                    "CidrBlock": "10.0.128.0/18",
                    "MapPublicIpOnLaunch": False,
                    "Tags": [
                        {"Key": "aws-cdk:subnet-name", "Value": "Private"},
                        {"Key": "aws-cdk:subnet-type", "Value": "Private"},
                        {
                            "Key": "Name",
                            "Value": "AutoScalingStack/DefaultVPC/PrivateSubnet1",
                        },
                    ],
                    "VpcId": {"Ref": "DefaultVPC5503DC78"},
                },
            },
            "DefaultVPCPrivateSubnet1RouteTable80B3BCFC": {
                "Type": "AWS::EC2::RouteTable",
                "Properties": {
                    "Tags": [
                        {
                            "Key": "Name",
                            "Value": "AutoScalingStack/DefaultVPC/PrivateSubnet1",
                        }
                    ],
                    "VpcId": {"Ref": "DefaultVPC5503DC78"},
                },
            },
            "DefaultVPCPrivateSubnet1RouteTableAssociationC4A133AC": {
                "Type": "AWS::EC2::SubnetRouteTableAssociation",
                "Properties": {
                    "RouteTableId": {
                        "Ref": "DefaultVPCPrivateSubnet1RouteTable80B3BCFC"
                    },
                    "SubnetId": {"Ref": "DefaultVPCPrivateSubnet1Subnet69F61BC0"},
                },
            },
            "DefaultVPCPrivateSubnet1DefaultRoute1AB9A008": {
                "Type": "AWS::EC2::Route",
                "Properties": {
                    "DestinationCidrBlock": "0.0.0.0/0",
                    "NatGatewayId": {
                        "Ref": "DefaultVPCPublicSubnet1NATGateway0D561ED0"
                    },
                    "RouteTableId": {
                        "Ref": "DefaultVPCPrivateSubnet1RouteTable80B3BCFC"
                    },
                },
            },
            "DefaultVPCPrivateSubnet2Subnet79FDD6A9": {
                "Type": "AWS::EC2::Subnet",
                "Properties": {
                    "AvailabilityZone": {"Fn::Select": [1, {"Fn::GetAZs": ""}]},
                    "CidrBlock": "10.0.192.0/18",
                    "MapPublicIpOnLaunch": False,
                    "Tags": [
                        {"Key": "aws-cdk:subnet-name", "Value": "Private"},
                        {"Key": "aws-cdk:subnet-type", "Value": "Private"},
                        {
                            "Key": "Name",
                            "Value": "AutoScalingStack/DefaultVPC/PrivateSubnet2",
                        },
                    ],
                    "VpcId": {"Ref": "DefaultVPC5503DC78"},
                },
            },
            "DefaultVPCPrivateSubnet2RouteTable8361218C": {
                "Type": "AWS::EC2::RouteTable",
                "Properties": {
                    "Tags": [
                        {
                            "Key": "Name",
                            "Value": "AutoScalingStack/DefaultVPC/PrivateSubnet2",
                        }
                    ],
                    "VpcId": {"Ref": "DefaultVPC5503DC78"},
                },
            },
            "DefaultVPCPrivateSubnet2RouteTableAssociation50C7324F": {
                "Type": "AWS::EC2::SubnetRouteTableAssociation",
                "Properties": {
                    "RouteTableId": {
                        "Ref": "DefaultVPCPrivateSubnet2RouteTable8361218C"
                    },
                    "SubnetId": {"Ref": "DefaultVPCPrivateSubnet2Subnet79FDD6A9"},
                },
            },
            "DefaultVPCPrivateSubnet2DefaultRouteBE7981E3": {
                "Type": "AWS::EC2::Route",
                "Properties": {
                    "DestinationCidrBlock": "0.0.0.0/0",
                    "NatGatewayId": {
                        "Ref": "DefaultVPCPublicSubnet2NATGatewayF8AD1A18"
                    },
                    "RouteTableId": {
                        "Ref": "DefaultVPCPrivateSubnet2RouteTable8361218C"
                    },
                },
            },
            "DefaultVPCIGW896174DD": {
                "Type": "AWS::EC2::InternetGateway",
                "Properties": {
                    "Tags": [{"Key": "Name", "Value": "AutoScalingStack/DefaultVPC"}]
                },
            },
            "DefaultVPCVPCGW0B423978": {
                "Type": "AWS::EC2::VPCGatewayAttachment",
                "Properties": {
                    "InternetGatewayId": {"Ref": "DefaultVPCIGW896174DD"},
                    "VpcId": {"Ref": "DefaultVPC5503DC78"},
                },
            },
            "LBSecurityGroup4464B654": {
                "Type": "AWS::EC2::SecurityGroup",
                "Properties": {
                    "GroupDescription": "AutoScalingStack/LBSecurityGroup",
                    "SecurityGroupEgress": [
                        {
                            "CidrIp": "0.0.0.0/0",
                            "Description": "Allow all outbound traffic by default",
                            "IpProtocol": "-1",
                        }
                    ],
                    "SecurityGroupIngress": [
                        {
                            "CidrIp": "0.0.0.0/0",
                            "Description": "from 0.0.0.0/0:80",
                            "FromPort": 80,
                            "IpProtocol": "tcp",
                            "ToPort": 80,
                        }
                    ],
                    "VpcId": {"Ref": "DefaultVPC5503DC78"},
                },
            },
            "ALBAEE750D2": {
                "Type": "AWS::ElasticLoadBalancingV2::LoadBalancer",
                "Properties": {
                    "LoadBalancerAttributes": [
                        {"Key": "deletion_protection.enabled", "Value": "false"}
                    ],
                    "Scheme": "internet-facing",
                    "SecurityGroups": [
                        {"Fn::GetAtt": ["LBSecurityGroup4464B654", "GroupId"]}
                    ],
                    "Subnets": [
                        {"Ref": "DefaultVPCPublicSubnet1Subnet45857342"},
                        {"Ref": "DefaultVPCPublicSubnet2Subnet21115AAE"},
                    ],
                    "Type": "application",
                },
                "DependsOn": [
                    "DefaultVPCPublicSubnet1DefaultRoute3A52FCAC",
                    "DefaultVPCPublicSubnet1RouteTableAssociation0C4E2762",
                    "DefaultVPCPublicSubnet2DefaultRoute584C6E3B",
                    "DefaultVPCPublicSubnet2RouteTableAssociationD1D339EB",
                ],
            },
            "ALBListener3B99FF85": {
                "Type": "AWS::ElasticLoadBalancingV2::Listener",
                "Properties": {
                    "DefaultActions": [
                        {
                            "TargetGroupArn": {
                                "Ref": "ALBListenerAppFleetGroupEB5556ED"
                            },
                            "Type": "forward",
                        }
                    ],
                    "LoadBalancerArn": {"Ref": "ALBAEE750D2"},
                    "Port": 80,
                    "Protocol": "HTTP",
                },
            },
            "ALBListenerAppFleetGroupEB5556ED": {
                "Type": "AWS::ElasticLoadBalancingV2::TargetGroup",
                "Properties": {
                    "Port": 80,
                    "Protocol": "HTTP",
                    "TargetGroupAttributes": [
                        {"Key": "stickiness.enabled", "Value": "false"}
                    ],
                    "TargetType": "instance",
                    "VpcId": {"Ref": "DefaultVPC5503DC78"},
                },
            },
            "WebServerSG4D0F372C": {
                "Type": "AWS::EC2::SecurityGroup",
                "Properties": {
                    "GroupDescription": "AutoScalingStack/WebServerSG",
                    "SecurityGroupEgress": [
                        {
                            "CidrIp": "0.0.0.0/0",
                            "Description": "Allow all outbound traffic by default",
                            "IpProtocol": "-1",
                        }
                    ],
                    "VpcId": {"Ref": "DefaultVPC5503DC78"},
                },
            },
            "WebServerSGfromAutoScalingStackLBSecurityGroup7E16D7FA804B186D70": {
                "Type": "AWS::EC2::SecurityGroupIngress",
                "Properties": {
                    "Description": "from AutoScalingStackLBSecurityGroup7E16D7FA:80",
                    "FromPort": 80,
                    "GroupId": {"Fn::GetAtt": ["WebServerSG4D0F372C", "GroupId"]},
                    "IpProtocol": "tcp",
                    "SourceSecurityGroupId": {
                        "Fn::GetAtt": ["LBSecurityGroup4464B654", "GroupId"]
                    },
                    "ToPort": 80,
                },
            },
            "ASGInstanceRoleE263A41B": {
                "Type": "AWS::IAM::Role",
                "Properties": {
                    "AssumeRolePolicyDocument": {
                        "Statement": [
                            {
                                "Action": "sts:AssumeRole",
                                "Effect": "Allow",
                                "Principal": {"Service": "ec2.amazonaws.com"},
                            }
                        ],
                        "Version": "2012-10-17",
                    },
                    "Tags": [{"Key": "Name", "Value": "AutoScalingStack/ASG"}],
                },
            },
            "ASGInstanceProfile0A2834D7": {
                "Type": "AWS::IAM::InstanceProfile",
                "Properties": {"Roles": [{"Ref": "ASGInstanceRoleE263A41B"}]},
            },
            "ASGLaunchConfigC00AF12B": {
                "Type": "AWS::AutoScaling::LaunchConfiguration",
                "Properties": {
                    "IamInstanceProfile": {"Ref": "ASGInstanceProfile0A2834D7"},
                    "ImageId": {
                        "Ref": "SsmParameterValueawsserviceamiamazonlinuxlatestamzn2amihvmx8664gp2C96584B6F00A464EAD1953AFF4B05118Parameter"
                    },
                    "InstanceType": "t3.micro",
                    "SecurityGroups": [
                        {"Fn::GetAtt": ["WebServerSG4D0F372C", "GroupId"]}
                    ],
                    "UserData": {
                        "Fn::Base64": "#!/bin/bash\nyum update -y\nyum install -y httpd\nsystemctl enable httpd\nsystemctl start httpd\necho '<h1>Hello from EC2 Auto Scaling Group</h1>' > /var/www/html/index.html\n"
                    },
                },
                "DependsOn": ["ASGInstanceRoleE263A41B"],
            },
            "ASG46ED3070": {
                "Type": "AWS::AutoScaling::AutoScalingGroup",
                "Properties": {
                    "DesiredCapacity": "2",
                    "LaunchConfigurationName": {"Ref": "ASGLaunchConfigC00AF12B"},
                    "MaxSize": "4",
                    "MinSize": "2",
                    "Tags": [
                        {
                            "Key": "Name",
                            "PropagateAtLaunch": True,
                            "Value": "AutoScalingStack/ASG",
                        }
                    ],
                    "TargetGroupARNs": [{"Ref": "ALBListenerAppFleetGroupEB5556ED"}],
                    "VPCZoneIdentifier": [
                        {"Ref": "DefaultVPCPrivateSubnet1Subnet69F61BC0"},
                        {"Ref": "DefaultVPCPrivateSubnet2Subnet79FDD6A9"},
                    ],
                },
                "UpdatePolicy": {
                    "AutoScalingScheduledAction": {
                        "IgnoreUnmodifiedGroupSizeProperties": True
                    }
                },
            },
        },
        "Parameters": {
            "SsmParameterValueawsserviceamiamazonlinuxlatestamzn2amihvmx8664gp2C96584B6F00A464EAD1953AFF4B05118Parameter": {
                "Type": "AWS::SSM::Parameter::Value<AWS::EC2::Image::Id>",
                "Default": "/aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-gp2",
            },
            "BootstrapVersion": {
                "Type": "AWS::SSM::Parameter::Value<String>",
                "Default": "/cdk-bootstrap/hnb659fds/version",
                "Description": "Version of the CDK Bootstrap resources in this environment, automatically retrieved from SSM Parameter Store. [cdk:skip]",
            },
        },
        "Outputs": {
            "LoadBalancerDNS": {"Value": {"Fn::GetAtt": ["ALBAEE750D2", "DNSName"]}}
        },
    },
    starter_code_files={
        "app.py": """#!/usr/bin/env python3
import aws_cdk as cdk
from aws_cdk import (
    aws_ec2 as ec2,
    aws_autoscaling as autoscaling,
    aws_elasticloadbalancingv2 as elbv2,
    Stack,
    CfnOutput
)
from constructs import Construct

class AutoScalingStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # TODO: Create a VPC with `DefaultVPC` ID
        
        # TODO: Create a security group for the load balancer. Use `LBSecurityGroup` as the construct ID.
        # - Allow HTTP (port 80) from anywhere
        # - Allow all outbound traffic
        
        # TODO: Create an Application Load Balancer. Use `ALB` as the construct ID.
        # - Make it internet-facing
        # - Add an HTTP listener on port 80
        
        # TODO: Create a security group for the web servers. Use `WebServerSG` as the construct ID.
        # - Allow HTTP (port 80) from the load balancer security group
        # - Allow all outbound traffic
        
        # TODO: Create an Auto Scaling Group. Use `ASG` as the construct ID.
        # - Use Amazon Linux 2 AMI
        # - Use t3.micro instance type
        # - Set min=2, max=4, desired=2 instances
        # - Add user data to install and run Apache
        
        # TODO: Register the Auto Scaling Group as a target for the load balancer. Use `AppFleet` as id.
        
        # TODO: Add an output for the load balancer DNS name. Use `LoadBalancerDNS` as id.

app = cdk.App()
AutoScalingStack(app, "AutoScalingStack")
app.synth()
""",
        "requirements.txt": """aws-cdk-lib>=2.0.0
constructs>=10.0.0
""",
    },
)

# List of sample challenges
SAMPLE_CHALLENGES: List[Challenge] = [
    S3_BUCKET_CHALLENGE,
    LAMBDA_CHALLENGE,
    DYNAMODB_CHALLENGE,
    SNS_SQS_CHALLENGE,
    VPC_CHALLENGE,
    EC2_AUTO_SCALING_CHALLENGE,
]
