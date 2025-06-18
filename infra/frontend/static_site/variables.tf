variable "aws_region" {
  default = "ap-southeast-2"
}

variable "project_name" {
  description = "Project name prefix for all resources"
  type        = string
  default     = "book-store"
}

variable "bucket_name" {
  description = "The name of the S3 bucket to host the frontend static website"
}

variable "frontend_src" {
  description = "The local path to the frontend build directory to be uploaded to the S3 bucket"
}