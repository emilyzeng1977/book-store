locals {
  book_store_price_container_name = "book_store_price"
}

# ---------------------------
# 创建 CloudWatch Log Group，用于存储 ECS 任务的容器日志
# ---------------------------
data "aws_cloudwatch_log_group" "book_store_price" {
  name              = "/ecs/${local.book_store_price_container_name}"
  # retention_in_days = 1   # 日志保留天数，根据需求调整
}

# ---------------------------
# ECS 任务执行角色（IAM Role）拉镜像、写日志
# ---------------------------
resource "aws_iam_role" "book_store_price_execution_role" {
  name = "${local.book_store_price_container_name}_execution_role"

  # 定义允许哪些服务可以假设此角色，这里是ecs-tasks服务
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      },
      Action = "sts:AssumeRole"
    }]
  })
}

# 附加Amazon提供的托管策略，赋予任务拉取镜像、写日志等权限
resource "aws_iam_role_policy_attachment" "book_store_price_execution_policy_attach" {
  role       = aws_iam_role.book_store_price_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# ---------------------------
# ECS 任务角色 + X-Ray 权限
# ---------------------------
resource "aws_iam_role" "book_store_price_task_role" {
  name = "${local.book_store_price_container_name}_task_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      },
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy" "book_store_price_xray_policy" {
  name = "${local.book_store_price_container_name}-xray-policy"
  role = aws_iam_role.book_store_price_task_role.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "xray:PutTraceSegments",
          "xray:PutTelemetryRecords",
          "xray:GetSamplingRules",
          "xray:GetSamplingTargets",
          "xray:GetSamplingStatisticSummaries"
        ],
        Resource = "*"
      }
    ]
  })
}

# ---------------------------
# 定义 ECS Fargate 的任务定义，包括容器配置、日志设置、CPU/内存等
# ---------------------------
resource "aws_ecs_task_definition" "book_store_price" {
  family                   = "${local.book_store_price_container_name}-task"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.book_store_price_execution_role.arn
  task_role_arn            = aws_iam_role.book_store_price_task_role.arn

  depends_on = [data.aws_cloudwatch_log_group.book_store_price]

  container_definitions = jsonencode([
    {
      name      = "${local.book_store_price_container_name}"
      image     = "961341537777.dkr.ecr.ap-southeast-2.amazonaws.com/book-store-price:latest"
      portMappings = [
        {
          containerPort = 5000
          protocol      = "tcp"
        }
      ]
      essential = true
      environment = [
        {
          name  = "AWS_XRAY_DAEMON_ADDRESS"
          value = "127.0.0.1:2000"
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = data.aws_cloudwatch_log_group.book_store_price.name
          "awslogs-region"        = "ap-southeast-2"
          "awslogs-stream-prefix" = "${local.book_store_price_container_name}"
        }
      }
    },
    {
      name      = "xray-daemon"
      image     = "amazon/aws-xray-daemon"
      essential = false
      portMappings = [
        {
          containerPort = 2000
          protocol      = "udp"
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = data.aws_cloudwatch_log_group.book_store_price.name
          "awslogs-region"        = "ap-southeast-2"
          "awslogs-stream-prefix" = "xray"
        }
      }
      healthCheck = {
        command     = ["CMD-SHELL", "nc -z 127.0.0.1 2000 || exit 1"]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 10
      }
    }
  ])
}

# ---------------------------
# Security Group
# ---------------------------
resource "aws_security_group" "sg_book_store_price" {
  name        = "${local.book_store_price_container_name}-ecs-sg"
  description = "Allow book-store to book-store-price"
  vpc_id      = var.bookStore_vpi_id

  ingress {
    from_port       = 5000
    to_port         = 5000
    protocol        = "tcp"
    security_groups = var.bookStore_service_sg_ids
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# ---------------------------
# 创建 ECS Service，用于部署并运行 Fargate 容器任务
# ---------------------------
resource "aws_ecs_service" "book_store_price" {
  name            = "${local.book_store_price_container_name}-service"
  cluster         = aws_ecs_cluster.main.id
  launch_type     = "FARGATE"
  task_definition = aws_ecs_task_definition.book_store_price.arn
  desired_count   = 1

  network_configuration {
    subnets          = var.bookStore_service_subnet_ids
    assign_public_ip = false
    security_groups  = [aws_security_group.sg_book_store_price.id]
  }

  service_registries {
    registry_arn = aws_service_discovery_service.book_store_price.arn
  }
}
