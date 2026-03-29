import boto3
import json
from datetime import datetime, timedelta

# Initialize AWS Clients
rekognition = boto3.client('rekognition')
dynamodb = boto3.resource('dynamodb')

# Table Names - Verify these match your AWS Console exactly
attendance_table = dynamodb.Table('Attendance-team')
employees_table = dynamodb.Table('Employees_team')

def lambda_handler(event, context):
    try:
        # 1. Get S3 Bucket and Key from Trigger
        bucket = event['Records'][0]['s3']['bucket']['name']
        key = event['Records'][0]['s3']['object']['key']

        print(f"Processing image: {key} from bucket: {bucket}")

        # 2. Search for Face in Rekognition Collection
        response = rekognition.search_faces_by_image(
            CollectionId='employee-collection',
            Image={'S3Object': {'Bucket': bucket, 'Name': key}},
            FaceMatchThreshold=70,
            MaxFaces=1
        )

        # Handle No Match Found
        if not response['FaceMatches']:
            print("No face match found in collection.")
            return {
                "statusCode": 200,
                "body": json.dumps("No match found")
            }

        # 3. Extract Employee ID (ExternalImageId)
        match = response['FaceMatches'][0]
        employee_id = match['Face']['ExternalImageId'].upper()
        print(f"Match found! Employee ID: {employee_id}")

        # 4. Get Employee Name from Employees_team Table
        emp = employees_table.get_item(Key={'employee_id': employee_id})
        name = emp.get('Item', {}).get('name', 'Unknown')

        # 5. Handle IST Time (UTC + 5:30)
        utc_now = datetime.utcnow()
        ist_now = utc_now + timedelta(hours=5, minutes=30)
        
        date_today = ist_now.strftime("%Y-%m-%d")
        time_now = ist_now.strftime("%H:%M")

        # 6. Determine Status (Late after 9:00 AM)
        status = "Present"
        if ist_now.hour >= 9:
            status = "Late"

        # 7. Check if record exists for today
        existing = attendance_table.get_item(
            Key={'employee_id': employee_id, 'date': date_today}
        )

        # --- CASE A: NEW CHECK-IN ---
        if 'Item' not in existing:
            attendance_table.put_item(
                Item={
                    'employee_id': employee_id,
                    'date': date_today,
                    'clock_in': time_now,
                    'clock_out': "",
                    'status': status,
                    'name': name,
                    'image_key': key,
                    'message': "Checked In"
                }
            )
            print(f"Successfully Checked In: {name} at {time_now}")

        else:
            item = existing['Item']

            # --- CASE C: ALREADY COMPLETED (Third Attempt) ---
            if item.get('clock_out'):
                print(f"User {name} already clocked out today.")
                attendance_table.update_item(
                    Key={'employee_id': employee_id, 'date': date_today},
                    UpdateExpression="SET #m = :msg, image_key = :ik",
                    ExpressionAttributeNames={"#m": "message"},
                    ExpressionAttributeValues={
                        ':msg': "Already Clocked Out for Today",
                        ':ik': key
                    }
                )

            # --- CASE B: CLOCK-OUT (Second Attempt) ---
            else:
                attendance_table.update_item(
                    Key={'employee_id': employee_id, 'date': date_today},
                    UpdateExpression="SET clock_out = :t, #m = :msg, image_key = :ik",
                    ExpressionAttributeNames={"#m": "message"},
                    ExpressionAttributeValues={
                        ':t': time_now,
                        ':msg': "Checked Out",
                        ':ik': key
                    }
                )
                print(f"Successfully Checked Out: {name} at {time_now}")

        return {
            "statusCode": 200,
            "body": json.dumps("Attendance processed successfully")
        }

    except Exception as e:
        print(f"ERROR: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps(str(e))
        }