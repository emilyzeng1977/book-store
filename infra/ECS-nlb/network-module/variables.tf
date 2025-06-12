variable "project_name" {
  description = "Project name used for tagging resources"
  type        = string
}

variable "vpc_cidr" {
  description = "vpc cidr"
  type        = string
  default     = "10.0.0.0/16"
}


