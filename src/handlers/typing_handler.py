import json
import os
import boto3

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])

api_endpoint = os.environ["API_GATEWAY_ENDPOINT"]
client = boto3.client("apigatewaymanagementapi", endpoint_url=f"https://{api_endpoint}")

def lambda_handler(event, context):
    body = json.loads(event.get("body", "{}"))
    connection_id = event["requestContext"]["connectionId"]
    conversation_id = body.get("conversationId")
    sender_id = body.get("senderId", "unknown")

    try:
        recipient_conn = table.scan(
            FilterExpression="begins_with(pk, :pk) AND begins_with(sk, :sk)",
            ExpressionAttributeValues={
                ":pk": "USER#",
                ":sk": "CONN#"
            }
        )

        for conn in recipient_conn.get("Items", []):
            if conn.get("userId") != sender_id:
                try:
                    client.post_to_connection(
                        ConnectionId=conn["connectionId"],
                        Data=json.dumps({
                            "action": "typingIndicator",
                            "userId": sender_id,
                            "conversationId": conversation_id
                        })
                    )
                except Exception:
                    pass
    except Exception:
        pass

    return {"statusCode": 200}
