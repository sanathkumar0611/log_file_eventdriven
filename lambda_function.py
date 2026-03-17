import boto3
import os

s3 = boto3.client('s3')

# 🔥 Error → Debugging Commands Mapping
ERROR_SOLUTIONS = {
    "Disk space full": [
        "df -h",
        "du -sh *",
        "sudo journalctl --vacuum-time=3d",
        "rm -rf /tmp/*"
    ],
    "Memory issue": [
        "free -m",
        "top",
        "ps aux --sort=-%mem | head",
        "kill -9 <PID>"
    ],
    "CPU high": [
        "top",
        "htop",
        "ps aux --sort=-%cpu | head"
    ],
    "Database connection failed": [
        "systemctl status mysql",
        "netstat -tulnp | grep 3306",
        "telnet <db-host> 3306",
        "check DB credentials"
    ],
    "Timeout": [
        "check network latency",
        "ping <service>",
        "traceroute <service>",
        "increase timeout config"
    ],
    "Permission denied": [
        "ls -l",
        "chmod 755 <file>",
        "chown user:user <file>"
    ]
}

def lambda_handler(event, context):
    output_bucket = os.environ['OUTPUT_BUCKET']

    for record in event['Records']:
        input_bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']

        response = s3.get_object(Bucket=input_bucket, Key=key)
        content = response['Body'].read().decode('utf-8')

        output_lines = []

        for line in content.splitlines():
            if "ERROR" in line:
                output_lines.append(f"\n🔴 {line}")

                # Match error type
                matched = False
                for error_key in ERROR_SOLUTIONS:
                    if error_key.lower() in line.lower():
                        output_lines.append("💡 Suggested Debug Commands:")
                        for cmd in ERROR_SOLUTIONS[error_key]:
                            output_lines.append(f"   - {cmd}")
                        matched = True
                        break

                if not matched:
                    output_lines.append("💡 General Debugging:")
                    output_lines.append("   - check logs")
                    output_lines.append("   - restart service")
                    output_lines.append("   - verify configuration")

        if not output_lines:
            output_lines.append("✅ No errors found")

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
