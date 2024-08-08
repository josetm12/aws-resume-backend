import boto3
import os
import json
from botocore.exceptions import ClientError
from botocore.config import Config
from decimal import Decimal

# Configuration for DynamoDB
config = Config(
    region_name="us-west-2",
    signature_version="v4",
    retries={"max_attempts": 10, "mode": "standard"}
)

# Initialize a DynamoDB session
session = boto3.Session(
    aws_access_key_id="acid",
    aws_secret_access_key="asa",
    region_name="us-west-2"
)
dynamodb = session.resource(
    "dynamodb",
    endpoint_url=os.getenv("DYNAMODB_ENDPOINT"),
    config=config
)
table = dynamodb.Table("VisitCounter")

# Helper function to convert DynamoDB items to JSON-serializable format
def decimal_default(obj):
    if isinstance(obj, Decimal):
        return int(obj)
    raise TypeError

def lambda_handler(event, context):
    print("Reached handler")
    print("ENV", os.getenv("DYNAMODB_ENDPOINT"))

    # Handle CORS preflight request
    if event["httpMethod"] == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "PUT,OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type,Authorization"
            }
        }

    try:
        page = "home"
        response = table.update_item(
            Key={"page": page},
            UpdateExpression="SET VisitCount = if_not_exists(VisitCount, :start) + :inc",
            ExpressionAttributeValues={":start": 0, ":inc": 1},
            ReturnValues="UPDATED_NEW"
        )
        visit_count = response["Attributes"]["VisitCount"]
        print(f"Visit count for page '{page}': {visit_count}")
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({"page": page, "visits": visit_count}, default=decimal_default)
        }
    except ClientError as e:
        print(f"DynamoDB ClientError: {e}")
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({"error": "Internal Server Error DynamoDB ClientError"})
        }
    except Exception as e:
        print(f"Unexpected error: {e}")
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({"error": "Internal Server Error"})
        }
