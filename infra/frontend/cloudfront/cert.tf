provider "aws" {
  alias  = "virginia"
  region = "us-east-1"
}

data "aws_acm_certificate" "wildcard_dev" {
  provider    = aws.us_east_1
  domain      = "*.be-devops.shop"
  statuses    = ["ISSUED"]
  most_recent = true
}