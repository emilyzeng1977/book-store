variable "project" {
  description = "Project name"
  default     = "tom-demo"
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "ap-southeast-2"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets"
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets"
  default     = ["10.0.3.0/24", "10.0.4.0/24"]
}

variable "eks_node_policies" {
  default = [
    "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy", # 提供 EKS 工作节点的基本权限
    "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly", # 提供只读访问 Amazon ECR 的权限
    "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy" # 提供 EKS 容器网络接口 (CNI) 所需权限
  ]
}