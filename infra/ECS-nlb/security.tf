# resource "aws_security_group" "ecs_service_sg" {
#   name = "${var.project_name}-ecs-sg"
#   vpc_id = module.network.vpc_id
#
#   ingress {
#     from_port   = 5000
#     to_port     = 5000
#     protocol    = "tcp"
#     cidr_blocks = ["10.0.0.0/16"]
#   }
#
#   ingress {
#     from_port   = 80
#     to_port     = 80
#     protocol    = "tcp"
#     cidr_blocks = ["10.0.0.0/16"]
#   }
#
#   egress {
#     from_port   = 0
#     to_port     = 0
#     protocol    = "-1"
#     cidr_blocks = ["0.0.0.0/0"]
#   }
# }


### SG: VPC Link（用于 API Gateway 的 VPC Link ENI）
resource "aws_security_group" "vpc_link_sg" {
  name = "${var.project_name}-vpc-link-sg"
  description = "Allow API Gateway VPC Link to access NLB"
  vpc_id = module.network.vpc_id

  egress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"]  # 允许访问 VPC 内部 NLB
  }

  # ingress not needed (ENI only sends requests)
}

### SG: NLB（2023年后可选，绑定到 NLB）
resource "aws_security_group" "nlb_sg" {
  name        = "${var.project_name}-nlb-sg"
  description = "Allow inbound traffic from VPC Link"
  vpc_id      = module.network.vpc_id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    security_groups = [aws_security_group.vpc_link_sg.id]  # 只允许来自 VPC Link SG 的流量
  }

  egress {
    from_port   = 5000
    to_port     = 5000
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"]  # 允许访问 ECS 服务
  }
}

### SG: ECS Fargate Task
resource "aws_security_group" "ecs_fargate_sg" {
  name = "${var.project_name}-ecs-sg"
  description = "Allow NLB to reach ECS app"
  vpc_id = module.network.vpc_id

  ingress {
    from_port   = 5000
    to_port     = 5000
    protocol    = "tcp"
    security_groups = [aws_security_group.nlb_sg.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}


