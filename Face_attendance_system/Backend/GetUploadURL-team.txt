import json
import boto3
import uuid

s3 = boto3.client('s3')

def lambda_handler(event, context):
    try:
        file_key = f"uploads/{uuid.uuid4()}.jpg"

        upload_url = s3.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': 'attendance-captures-team',
                'Key': file_key,
                'ContentType': 'image/jpeg'
            },
            ExpiresIn=300
        )

        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "uploadURL": upload_url,
                "fileName": file_key
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "error": str(e)
            })
        }