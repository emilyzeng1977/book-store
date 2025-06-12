variable "project_name" {
  description = "Project name prefix for all resources"
  type        = string
  default     = "book-store-nlb"
}

variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "ap-southeast-2"
}
