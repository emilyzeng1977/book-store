terraform {
  backend "s3" {
    bucket         = "tfstate-emily"         # 你刚刚创建的 S3 bucket 名
    key            = "book-store/backend/newrelic-lambda-forwarder/terraform.tfstate"  # 存储在 S3 中的路径
    region         = "ap-southeast-2"
    dynamodb_table = "tfstate-lock-emily"             # 如果你启用了锁表
    encrypt        = true
  }
}