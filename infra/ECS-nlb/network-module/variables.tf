variable "project_name" {
  description = "Project name used for tagging resources"
  type        = string
}

variable "vpc_cidr" {
  description = "vpc cidr"
  type        = string
  default     = "10.0.0.0/16"
}

variable "enable_nat_gateway" {
  description = "Whether to create a NAT Gateway for private subnet Internet access"
  type        = bool
  default     = false
}

variable "enable_interface_vpc_endpoint" {
  type        = bool
  default     = false
  description = "Set to true to create Interface VPC Endpoint for private access to AWS services (e.g., ECR API). When enabled, the module will create the necessary ENIs and DNS settings."
}

