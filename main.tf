provider "aws" {
  region = var.aws_region
}

resource "random_id" "rand" {
  byte_length = 4
}

# -----------------------
# S3 BUCKETS
# -----------------------

resource "aws_s3_bucket" "input_bucket" {
  bucket        = "${var.project_name}-input-${random_id.rand.hex}"
  force_destroy = true

  tags = {
    Name = "Input Bucket"
  }
}

resource "aws_s3_bucket" "output_bucket" {
  bucket        = "${var.project_name}-output-${random_id.rand.hex}"
  force_destroy = true

  tags = {
    Name = "Output Bucket"
  }
}

# -----------------------
# IAM ROLE
# -----------------------

resource "aws_iam_role" "lambda_role" {
  name = "${var.project_name}-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

# Least privilege policy
resource "aws_iam_policy" "lambda_policy" {
  name = "${var.project_name}-lambda-policy-${random_id.rand.hex}"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "s3:GetObject",
          "s3:PutObject"
        ]
        Effect = "Allow"
        Resource = [
          "${aws_s3_bucket.input_bucket.arn}/*",
          "${aws_s3_bucket.output_bucket.arn}/*"
        ]
      },
      {
        Action = ["logs:*"]
        Effect = "Allow"
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "attach" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_policy.arn
}

resource "aws_iam_role_policy_attachment" "basic_lambda" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# -----------------------
# ZIP CREATION
# -----------------------

data "archive_file" "lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/lambda_function.py"
  output_path = "${path.module}/lambda.zip"
}

# -----------------------
# LAMBDA
# -----------------------

resource "aws_lambda_function" "log_processor" {
  function_name = "${var.project_name}-processor"

  role    = aws_iam_role.lambda_role.arn
  runtime = "python3.9"
  handler = "lambda_function.lambda_handler"

  filename = data.archive_file.lambda_zip.output_path

  timeout     = 60
  memory_size = 256

  environment {
    variables = {
      OUTPUT_BUCKET = aws_s3_bucket.output_bucket.bucket
    }
  }

  depends_on = [
    aws_iam_role_policy_attachment.attach,
    aws_iam_role_policy_attachment.basic_lambda
  ]
}

# -----------------------
# TRIGGER
# -----------------------

resource "aws_lambda_permission" "allow_s3" {
  statement_id  = "AllowS3Invoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.log_processor.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.input_bucket.arn
}

resource "aws_s3_bucket_notification" "trigger" {
  bucket = aws_s3_bucket.input_bucket.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.log_processor.arn
    events              = ["s3:ObjectCreated:*"]
    filter_suffix       = ".log"
  }

  depends_on = [aws_lambda_permission.allow_s3]
}
