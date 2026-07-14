import json
import os
import boto3

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])

def lambda_handler(event, context):
    connection_id = event["requestContext"]["connectionId"]
    user_id = event.get("queryStringParameters", {}).get("userId", "anonymous")

    table.put_item(Item={
        "pk": f"USER#{user_id}",
        "sk": f"CONN#{connection_id}",
        "connectionId": connection_id,
        "userId": user_id,
        "connectedAt": event["requestContext"]["requestTime"],
        "type": "CONNECTION"
    })

    return {"statusCode": 200}
