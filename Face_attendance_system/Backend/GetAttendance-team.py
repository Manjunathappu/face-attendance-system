import json
import boto3

dynamodb = boto3.resource('dynamodb')

attendance_table = dynamodb.Table('Attendance-team')
employees_table = dynamodb.Table('Employees_team')

def lambda_handler(event, context):

    try:
        params = event.get("queryStringParameters") or {}

        name_filter = params.get("name", "")
        date_filter = params.get("date", "")
        status_filter = params.get("status", "")

        # 🔥 Get employee mapping
        emp_data = employees_table.scan()['Items']
        emp_map = {emp['employee_id']: emp['name'] for emp in emp_data}

        # 🔥 Get attendance
        response = attendance_table.scan()
        items = response['Items']

        filtered = []

        for item in items:

            emp_id = item.get("employee_id")

            # 🔥 Always attach correct name
            item["name"] = emp_map.get(emp_id, "Unknown")

            # Filters
            if name_filter and name_filter.lower() not in item["name"].lower():
                continue
            if date_filter and item.get("date") != date_filter:
                continue
            if status_filter and item.get("status") != status_filter:
                continue

            filtered.append(item)

        return {
            "statusCode": 200,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps(filtered)
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Access-Control-Allow-Origin": "*"},
            "body": json.dumps({"error": str(e)})
        }