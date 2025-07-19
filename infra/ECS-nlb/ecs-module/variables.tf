variable "project_name" {
  description = "Project name used for tagging resources"
  type        = string
}

variable "bookStore_vpi_id" {
  description = "VPC id"
  type        = string
}

variable "bookStore_service_subnet_ids" {
  description = "List of private subnet IDs where book-store task run"
  type        = list(string)
}

variable "bookStore_service_sg_ids" {
  description = "List of security group for book-store service"
  type        = list(string)
}

variable "bookStore_lb_tg_arn" {
  description = "target group arn for nlb"
  type        = string
}

