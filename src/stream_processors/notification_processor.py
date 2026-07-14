import json
import os
import boto3

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])

def lambda_handler(event, context):
    for record in event.get("Records", []):
        if record["eventName"] != "INSERT":
            continue

        new_image = record["dynamodb"]["NewImage"]

        if new_image.get("type", {}).get("S") != "MESSAGE":
            continue

        recipient_id = new_image.get("recipientId", {}).get("S")
        sender_id = new_image.get("senderId", {}).get("S")
        content = new_image.get("content", {}).get("S")
        message_id = new_image.get("messageId", {}).get("S")

        try:
            response = table.scan(
                FilterExpression="pk = :pk AND begins_with(sk, :sk)",
                ExpressionAttributeValues={
                    ":pk": f"USER#{recipient_id}",
                    ":sk": "CONN#"
                }
            )

            if not response.get("Items"):
                print(f"OFFLINE_NOTIFICATION: Message {message_id} from {sender_id} to {recipient_id}: {content}")
        except Exception as e:
            print(f"Error checking online status: {e}")

    return {"statusCode": 200}
