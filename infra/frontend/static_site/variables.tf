variable "aws_region" {
  default = "ap-southeast-2"
}

variable "project_name" {
  description = "Project name prefix for all resources"
  type        = string
  default     = "book-store"
}

variable "bucket_name" {
  default = "my-book-store-12345678"
}

variable "frontend_src" {
}