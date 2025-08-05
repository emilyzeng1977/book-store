#############################################
# ✅ 1. AWS Provider
#############################################
provider "aws" {
  region = var.region
}

#############################################
# ✅ 2. S3（使用已有桶）
#############################################
data "aws_s3_bucket" "firehose_bucket" {
  bucket = var.firehose_bucket
}

#############################################
# ✅ 3. IAM Role for Firehose
#############################################
resource "aws_iam_role" "firehose_role" {
  name = "firehose_delivery_role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Service = "firehose.amazonaws.com"
        },
        Action = "sts:AssumeRole"
      },
      {
        Effect = "Allow",
        Principal = {
          Service = "logs.${var.region}.amazonaws.com"
        },
        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role_policy" "firehose_policy" {
  role = aws_iam_role.firehose_role.id
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "s3:PutObject",
          "s3:PutObjectAcl",
          "s3:ListBucket"
        ],
        Resource = [
          data.aws_s3_bucket.firehose_bucket.arn,
          "${data.aws_s3_bucket.firehose_bucket.arn}/*"
        ]
      },
      {
        Effect = "Allow",
        Action = [
          "lambda:InvokeFunction"
        ],
        Resource = "*"
      },
      {
        Effect = "Allow",
        Action = [
          "logs:PutSubscriptionFilter",
          "logs:DescribeLogGroups",
          "logs:DescribeLogStreams",
          "logs:PutLogEvents"
        ],
        Resource = "*"
      },
      {
        Effect = "Allow",
        Action = [
          "firehose:PutRecord",
          "firehose:PutRecordBatch"
        ],
        Resource = "arn:aws:firehose:ap-southeast-2:961341537777:deliverystream/cloudwatch-logs-firehose"
      }
    ]
  })
}
#############################################
# ✅ 4. Lambda Function (for Firehose transform)
#############################################
module "firehose_transform" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "~> 6.0"

  function_name = "firehose-transform-json-extract"
  handler       = "main.lambda_handler"
  runtime       = "python3.12"

  # 👇 指向 src 目录
  source_path = "${path.module}/src"
  build_in_docker = true

  memory_size = 256
  timeout     = 10

  attach_policy_statements = true

  policy_statements = [
    {
      effect = "Allow"
      actions = [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ]
      resources = ["arn:aws:logs:*:*:*"]
    }
  ]

  environment_variables = {
  }
}
#############################################
# ✅ 5. Kinesis Firehose Delivery Stream
#############################################
resource "aws_kinesis_firehose_delivery_stream" "firehose_stream" {
  name        = "cloudwatch-logs-firehose"
  destination = "extended_s3"

  extended_s3_configuration {
    bucket_arn         = data.aws_s3_bucket.firehose_bucket.arn
    role_arn           = aws_iam_role.firehose_role.arn
    buffering_size     = 5
    buffering_interval = 300
    compression_format = "GZIP"

    processing_configuration {
      enabled = true

      processors {
        type = "Lambda"
        parameters {
          parameter_name  = "LambdaArn"
          parameter_value = module.firehose_transform.lambda_function_arn
        }
        parameters {
          parameter_name  = "NumberOfRetries"
          parameter_value = "3"
        }
        parameters {
          parameter_name  = "RoleArn"
          parameter_value = aws_iam_role.firehose_role.arn
        }
      }
    }
  }
}

#############################################
# ✅ 6. CloudWatch Logs Subscription
#############################################
resource "aws_cloudwatch_log_subscription_filter" "firehose_subscribe" {
  name            = "firehose-subscription"
  log_group_name  = var.cloudwatch_log_group
  filter_pattern  = ""
  # to do list
  # arn:aws:firehose:<region>:<account>:deliverystream/<stream-name>
  # destination_arn = aws_kinesis_firehose_delivery_stream.firehose_stream.arn
  destination_arn = "arn:aws:firehose:ap-southeast-2:961341537777:deliverystream/cloudwatch-logs-firehose"
  role_arn        = aws_iam_role.firehose_role.arn

  depends_on = [
    aws_kinesis_firehose_delivery_stream.firehose_stream
  ]
}