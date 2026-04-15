import boto3
import os
import urllib.parse

s3 = boto3.client('s3')

ERROR_SOLUTIONS = {
    "Disk space full": ["df -h", "du -sh *", "rm -rf /tmp/*"],
    "Memory issue": ["free -m", "top", "ps aux --sort=-%mem | head"],
    "CPU high": ["top", "ps aux --sort=-%cpu | head"],
    "Database connection failed": ["systemctl status mysql", "netstat -tulnp | grep 3306"],
    "Timeout": ["ping <service>", "traceroute <service>"],
    "Permission denied": ["ls -l", "chmod 755 <file>"]
}

def lambda_handler(event, context):
    output_bucket = os.environ['OUTPUT_BUCKET']

    for record in event['Records']:
        input_bucket = record['s3']['bucket']['name']
        key = urllib.parse.unquote_plus(record['s3']['object']['key'])

        print(f"Processing file: {key}")

        try:
            response = s3.get_object(Bucket=input_bucket, Key=key)
            content = response['Body'].read().decode('utf-8')
        except Exception as e:
            print("Error reading file:", str(e))
            continue

        output_lines = []

        for line in content.splitlines():
            if "ERROR" in line:
                output_lines.append(f"[ERROR] {line}")

                matched = False
                for error_key in ERROR_SOLUTIONS:
                    if error_key.lower() in line.lower():
                        output_lines.append("Suggested Debug Commands:")
                        for cmd in ERROR_SOLUTIONS[error_key]:
                            output_lines.append(f" - {cmd}")
                        matched = True
                        break

                if not matched:
                    output_lines.append("General Debugging:")
                    output_lines.append(" - check logs")
                    output_lines.append(" - restart service")

        if not output_lines:
            output_lines.append("No errors found")

        output_key = f"errors/{key}_debug.txt"

        s3.put_object(
            Bucket=output_bucket,
            Key=output_key,
            Body="\n".join(output_lines)
        )

    return {
        "statusCode": 200,
        "message": "Debug report generated"
    }
