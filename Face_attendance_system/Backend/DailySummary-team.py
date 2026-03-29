import json
import boto3
from datetime import datetime, timedelta

# Initialize Clients
s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

# 🔥 DOUBLE CHECK THESE NAMES IN YOUR AWS CONSOLE
attendance_table = dynamodb.Table('Attendance-team') 
employees_table = dynamodb.Table('Employees_team')
BUCKET_NAME = 'attendance-reports-team'

def lambda_handler(event, context):
    try:
        # 1. Handle IST Time correctly
        # Using a fixed offset to ensure we get the IST date accurately
        ist_now = datetime.utcnow() + timedelta(hours=5, minutes=30)
        date_today = ist_now.strftime("%Y-%m-%d")
        print(f"Running Daily Summary for: {date_today}")

        # 2. Get all registered employees
        all_employees = employees_table.scan()['Items']
        
        # 3. Get today's attendance records from DynamoDB
        # We use a Scan with a FilterExpression to only get records for 'today'
        # This is more efficient than scanning the whole table and filtering in Python
        attendance_today = attendance_table.scan(
            FilterExpression=boto3.dynamodb.conditions.Attr('date').eq(date_today)
        )['Items']
        
        # Create a set of IDs who are already present/late
        present_ids = {item['employee_id'] for item in attendance_today}

        # 4. Mark missing people as Absent
        absentees = []
        for emp in all_employees:
            emp_id = emp['employee_id']
            
            if emp_id not in present_ids:
                absent_entry = {
                    'employee_id': emp_id,
                    'date': date_today,
                    'name': emp.get('name', 'Unknown'),
                    'status': 'Absent',
                    'clock_in': '-',
                    'clock_out': '-',
                    'message': 'System Auto-Absent'
                }
                # Write to DynamoDB
                attendance_table.put_item(Item=absent_entry)
                absentees.append(absent_entry)
                print(f"Marked {emp_id} as Absent")

        # 5. Generate metrics for S3 Report
        total_present_records = attendance_today + absentees
        
        report_data = {
            "summary_date": date_today,
            "metrics": {
                "total_employees": len(all_employees),
                "present": len([i for i in attendance_today if i.get('status') in ['Present', 'Late']]),
                "late": len([i for i in attendance_today if i.get('status') == 'Late']),
                "absent": len(absentees)
            },
            "detailed_attendance": total_present_records
        }

        # 6. Upload to S3
        file_name = f"daily-summary-{date_today}.json"
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=file_name,
            Body=json.dumps(report_data, indent=4),
            ContentType='application/json'
        )

        return {
            "statusCode": 200,
            "body": f"Success! Marked {len(absentees)} absent and uploaded {file_name}."
        }

    except Exception as e:
        print(f"Error: {str(e)}")
        return {"statusCode": 500, "body": str(e)}