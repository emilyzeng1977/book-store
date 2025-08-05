variable "region" {
  default = "ap-southeast-2"
}

variable "firehose_bucket" {
  default = "bookstore-dev-logs-cloudwatch"
}

variable "cloudwatch_log_group" {
  default = "/ecs/book_store"
}