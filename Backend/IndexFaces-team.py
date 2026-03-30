import boto3
import time

rekognition = boto3.client('rekognition')
s3 = boto3.client('s3')

COLLECTION_ID = 'employee-collection'
BUCKET = 'employee-faces-team'

def lambda_handler(event, context):
    try:
        # Define the list of new employees to index
        new_employees = [
            {"name": "Supritha", "folder": "images/supritha/", "id": "EMP001"},
            {"name": "Sneha", "folder": "images/sneha/", "id": "EMP003"},
            {"name": "Babu", "folder": "images/Babu/", "id": "EMP004"}
            
        ]

        for employee in new_employees:
            folder = employee["folder"]
            employee_id = employee["id"]
            
            print(f"--- Starting indexing for: {employee_id} in {folder} ---")

            # Get all images inside folder
            response = s3.list_objects_v2(
                Bucket=BUCKET,
                Prefix=folder
            )

            if 'Contents' not in response:
                print(f"No images found for {employee_id}")
                continue

            for obj in response['Contents']:
                key = obj['Key']

                # Skip folder itself
                if key.endswith("/"):
                    continue

                # Process images (Added .jpeg support based on your S3 screenshots)
                if key.lower().endswith((".jpg", ".png", ".jpeg")):
                    print(f"Indexing: {key}")

                    rekognition.index_faces(
                        CollectionId=COLLECTION_ID,
                        Image={
                            'S3Object': {
                                'Bucket': BUCKET,
                                'Name': key
                            }
                        },
                        ExternalImageId=employee_id,
                        DetectionAttributes=[]
                    )

                    # Avoid Rekognition throttling
                    time.sleep(0.3)

        print("All specified employees indexed successfully")
        return {
            "statusCode": 200,
            "body": "Indexing for completed successfully"
        }

    except Exception as e:
        print("ERROR:", str(e))
        return {
            "statusCode": 500,
            "body": str(e)
        }