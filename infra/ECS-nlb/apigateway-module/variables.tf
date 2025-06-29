variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "ap-southeast-2"
}

variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "private_subnet_ids" {
  description = "List of private subnet IDs for VPC Link"
  type        = list(string)
}

variable "ecs_service_sg_id" {
  description = "Security group ID for ECS service"
  type        = string
}

variable "nlb_listener_arn" {
  description = "ARN of the NLB listener"
  type        = string
}
