import json
import boto3
from datetime import datetime, timedelta

dynamodb = boto3.resource('dynamodb')
attendance_table = dynamodb.Table('Attendance-team')
employees_table = dynamodb.Table('Employees_team')

def lambda_handler(event, context):

    response = attendance_table.scan()
    items = response['Items']

    # 🔥 Get total employees
    employees = employees_table.scan()['Items']
    total = len(employees)

    today_str = datetime.now().strftime("%Y-%m-%d")

    present_set = set()
    late_set = set()

    # 🔥 Weekly tracking
    today = datetime.now()
    last_week = today - timedelta(days=7)

    weekly_present_set = set()
    weekly_late_set = set()
    weekly_total_set = set()

    for item in items:

        emp_id = item.get("employee_id")
        status = item.get("status")
        date_str = item.get("date")

        # ✅ DAILY LOGIC (only today)
        if date_str == today_str:
            if status == "Present":
                present_set.add(emp_id)
            elif status == "Late":
                late_set.add(emp_id)
                present_set.add(emp_id)

        # ✅ WEEKLY LOGIC
        if date_str:
            record_date = datetime.strptime(date_str, "%Y-%m-%d")

            if record_date >= last_week:
                weekly_total_set.add(emp_id)

                if status == "Present":
                    weekly_present_set.add(emp_id)
                elif status == "Late":
                    weekly_late_set.add(emp_id)
                    weekly_present_set.add(emp_id)

    # ✅ FINAL COUNTS
    present = len(present_set)
    late = len(late_set)
    absent = total - present

    weekly_total = len(weekly_total_set)
    weekly_present = len(weekly_present_set)
    weekly_late = len(weekly_late_set)
    weekly_absent = total - weekly_present

    # ✅ Percentages
    wp = (weekly_present / total * 100) if total else 0
    wl = (weekly_late / total * 100) if total else 0
    wa = (weekly_absent / total * 100) if total else 0

    return {
        "statusCode": 200,
        "headers": {"Access-Control-Allow-Origin": "*"},
        "body": json.dumps({
            "total": total,
            "present": present,
            "late": late,
            "absent": absent,
            "weeklyPresent": round(wp, 1),
            "weeklyLate": round(wl, 1),
            "weeklyAbsent": round(wa, 1)
        })
    }