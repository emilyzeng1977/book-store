variable "project_name" {
  description = "Project name used for tagging resources"
  type        = string
}

variable "vpc_cidr" {
  description = "vpc cidr"
  type        = string
  default     = "10.0.0.0/16"
}

variable "enable_vpc_flow_log" {
  description = "是否启用 VPC Flow Logs"
  type        = bool
  default     = false  # 默认不启用
}


