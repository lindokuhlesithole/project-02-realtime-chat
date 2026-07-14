import json
import os
import boto3
import uuid
from datetime import datetime

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])

api_endpoint = os.environ["API_GATEWAY_ENDPOINT"]
client = boto3.client("apigatewaymanagementapi", endpoint_url=f"https://{api_endpoint}")

def lambda_handler(event, context):
    body = json.loads(event.get("body", "{}"))
    connection_id = event["requestContext"]["connectionId"]
    conversation_id = body.get("conversationId")
    content = body.get("content")
    sender_id = body.get("senderId", "unknown")
    recipient_id = body.get("recipientId")
    message_id = f"msg-{uuid.uuid4()}"
    timestamp = datetime.utcnow().isoformat()

    table.put_item(Item={
        "pk": f"CONV#{conversation_id}",
        "sk": f"MSG#{timestamp}#{message_id}",
        "messageId": message_id,
        "conversationId": conversation_id,
        "senderId": sender_id,
        "recipientId": recipient_id,
        "content": content,
        "timestamp": timestamp,
        "gsi1pk": f"USER#{recipient_id}",
        "gsi1sk": f"UNREAD#{timestamp}",
        "type": "MESSAGE"
    })

    try:
        recipient_conn = table.scan(
            FilterExpression="pk = :pk AND begins_with(sk, :sk)",
            ExpressionAttributeValues={
                ":pk": f"USER#{recipient_id}",
                ":sk": "CONN#"
            }
        )

        for conn in recipient_conn.get("Items", []):
            try:
                client.post_to_connection(
                    ConnectionId=conn["connectionId"],
                    Data=json.dumps({
                        "action": "messageReceived",
                        "messageId": message_id,
                        "content": content,
                        "senderId": sender_id,
                        "conversationId": conversation_id,
                        "timestamp": timestamp
                    })
                )
            except Exception:
                pass
    except Exception:
        pass

    try:
        client.post_to_connection(
            ConnectionId=connection_id,
            Data=json.dumps({
                "action": "messageDelivered",
                "messageId": message_id,
                "clientMessageId": body.get("clientMessageId")
            })
        )
    except Exception:
        pass

    return {"statusCode": 200}
