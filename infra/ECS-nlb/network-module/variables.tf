variable "project_name" {
  description = "Project name used for tagging resources"
  type        = string
}

variable "vpc_id" {
  description = "vpc id"
  default     = "vpc-064fb58bd18cc2c75"
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

variable "enable_vpc_flow_log" {
  description = "是否启用 VPC Flow Logs"
  type        = bool
  default     = false  # 默认不启用
}




