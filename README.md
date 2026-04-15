# 📊 Event-Driven Log Analyzer (AWS + Terraform)

## 🚀 Project Overview

This project implements an **event-driven log processing system** using AWS services and Terraform.
Whenever a log file is uploaded to an S3 bucket, an AWS Lambda function is automatically triggered to:

* Detect errors in logs
* Suggest debugging commands
* Store the processed output in another S3 bucket

---

## 🧠 Architecture

* **Amazon S3 (Input Bucket)** → Upload log files
* **AWS Lambda** → Processes logs and detects errors
* **Amazon S3 (Output Bucket)** → Stores debug reports
* **AWS IAM** → Provides secure access
* **Terraform** → Automates infrastructure provisioning

---

## 📁 Project Structure

```
.
├── main.tf
├── variables.tf
├── outputs.tf
├── terraform.tfvars
├── lambda_function.py
└── README.md
```

---

## ⚙️ Prerequisites

Before you start, ensure you have:

* AWS account
* AWS CLI configured (`aws configure`)
* Terraform installed
* Python (for Lambda development)

---

## 🔧 Step-by-Step Setup

### Step 1: Clone Repository

```
git clone https://github.com/your-username/log-file-event-driven.git
cd log-file-event-driven
```

---

### Step 2: Initialize Terraform

```
terraform init
```

---

### Step 3: Review Execution Plan

```
terraform plan
```

---

### Step 4: Deploy Infrastructure

```
terraform apply
```

Type `yes` when prompted.

---

### Step 5: Verify Resources

After deployment, Terraform will create:

* Input S3 bucket
* Output S3 bucket
* Lambda function
* IAM roles and policies

---

### Step 6: Upload Log File

Upload a `.log` file to the **input S3 bucket**.

Example log file:

```
ERROR: disk space full
ERROR: permission denied
```

---

### Step 7: Check Output

Go to the **output S3 bucket** and navigate to:

```
errors/
```

You will find a file like:

```
<filename>_debug.txt
```

---

## 📄 Sample Output

```
Processed at: 2026-04-15

[ERROR] ERROR: disk space full
Suggested Debug Commands:
 - df -h
 - du -sh *
 - rm -rf /tmp/*

[ERROR] ERROR: permission denied
Suggested Debug Commands:
 - ls -l
 - chmod 755 <file>
```

---

## ✨ Features

* Event-driven automation
* Real-time log processing
* Predefined troubleshooting suggestions
* Regex-based error detection
* Fully automated infrastructure using Terraform

---

## 🔐 Security Best Practices

* IAM roles with least privilege access
* Environment variables for configuration
* Controlled S3 access permissions

---

## 🧹 Cleanup

To destroy all resources:

```
terraform destroy
```

---

## 🚀 Future Enhancements

* Add SNS alerts for critical errors
* Integrate CloudWatch dashboards
* Store error patterns in DynamoDB
* Add CI/CD pipeline using GitHub Actions

---
