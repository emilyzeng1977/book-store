variable "project_name" {
  description = "Project name prefix for all resources"
  type        = string
  default     = "book-store"
}

variable "static_website_domain_name" {
  description = "The custom domain name used to access the static website hosted on S3 via CloudFront"
}

variable "dev_domain_name" {
  description = "The domain name used to access the development version of the website, e.g. dev.be-devops.shop"
  default = "dev.be-devops.shop"
}