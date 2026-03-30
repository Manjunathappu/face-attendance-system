import json
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Attendance-team')

def lambda_handler(event, context):
    try:
        # Get the key from the frontend request
        key = event.get("queryStringParameters", {}).get("key")
        print("Searching for image_key:", key)

        # ✅ NEW: Query the GSI instead of scanning the whole table
        response = table.query(
            IndexName='image_key-index',
            KeyConditionExpression=Key('image_key').eq(key)
        )

        items = response.get('Items', [])

        if not items:
            return {
                "statusCode": 200,
                "headers": {"Access-Control-Allow-Origin": "*"},
                "body": json.dumps({"message": "No face detected", "name": None})
            }

        # The query returns a list; we take the first match
        latest_item = items[0]
        
        return {
            "statusCode": 200,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({
                "name": latest_item.get("name"),
                "status": latest_item.get("status"),
                "time": latest_item.get("clock_out") or latest_item.get("clock_in"), # ✅ Gets the latest time
                "message": latest_item.get("message")
            })
        }

    except Exception as e:
        print("Error:", str(e))
        return {
            "statusCode": 500,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": str(e)})
        }