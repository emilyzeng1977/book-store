variable "aws_region" {
  default = "ap-southeast-2"
}

variable "project_name" {
  description = "Project name prefix for all resources"
  type        = string
  default     = "book-store"
}

variable "static_website_domain_name" {
    description = "The custom domain name used to access the static website hosted on S3 via CloudFront"
}