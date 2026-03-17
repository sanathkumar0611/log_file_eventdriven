import boto3
import os

s3 = boto3.client('s3')

def lambda_handler(event, context):
    output_bucket = os.environ['OUTPUT_BUCKET']

    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']

        response = s3.get_object(Bucket=bucket, Key=key)
        content = response['Body'].read().decode('utf-8')

        errors = [line for line in content.splitlines() if "ERROR" in line]

        s3.put_object(
            Bucket=output_bucket,
            Key=f"errors_{key}",
            Body="\n".join(errors)
        )

    return {"statusCode": 200}
