import json
import os
import boto3

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])

def lambda_handler(event, context):
    connection_id = event["requestContext"]["connectionId"]

    response = table.scan(
        FilterExpression="connectionId = :cid",
        ExpressionAttributeValues={":cid": connection_id}
    )

    for item in response.get("Items", []):
        table.delete_item(Key={"pk": item["pk"], "sk": item["sk"]})

    return {"statusCode": 200}
