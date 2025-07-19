locals {
  book_store_container_name = "book_store"
}

# ---------------------------
# 创建 CloudWatch Log Group，用于存储 ECS 任务的容器日志
# ---------------------------
resource "aws_cloudwatch_log_group" "book_store" {
  name              = "/ecs/${local.book_store_container_name}"
  retention_in_days = 1   # 日志保留天数，根据需求调整
}

# ---------------------------
# ECS 任务执行角色（IAM Role）拉镜像、写日志
# ---------------------------
resource "aws_iam_role" "book_store_execution_role" {
  name = "${local.book_store_container_name}_execution_role"

  # 定义允许哪些服务可以假设此角色，这里是ecs-tasks服务
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Principal = {
        Service = "ecs-tasks.amazonaws.com"  # ECS任务服务
      },
      Action = "sts:AssumeRole"
    }]
  })
}

# 附加Amazon提供的托管策略，赋予任务拉取镜像、写日志等权限
resource "aws_iam_role_policy_attachment" "book_store_execution_policy_attach" {
  role       = aws_iam_role.book_store_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# ---------------------------
# ECS 容器内部执行 Cognito 和 X-Ray
# ---------------------------
resource "aws_iam_role" "book_store_task_role" {
  name = "${local.book_store_container_name}_task_role"

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

# ✅ 1. Define Cognito Policy (NEW)
resource "aws_iam_policy" "book_store_cognito_access_policy" {
  name        = "${local.book_store_container_name}-cognito-access-policy"
  description = "Allow ECS task to call Cognito authentication APIs"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "cognito-idp:AdminInitiateAuth",
          "cognito-idp:InitiateAuth",
          "cognito-idp:RespondToAuthChallenge",
          "cognito-idp:GetUser"
        ],
        Resource = "*"
      }
    ]
  })
}
# ✅ 2. Attach Cognito Policy (NEW)
resource "aws_iam_role_policy_attachment" "book_store_task_role_policy_attach" {
  role       = aws_iam_role.book_store_task_role.name
  policy_arn = aws_iam_policy.book_store_cognito_access_policy.arn
}

# --- X-Ray Access ---
resource "aws_iam_role_policy" "book_store_xray_policy" {
  name = "${local.book_store_container_name}-xray-policy"
  role = aws_iam_role.book_store_task_role.id

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

# ✅ --- NEW: CloudWatch Logs Read for X-Ray Console Integration ---
resource "aws_iam_role_policy" "book_store_logs_access_policy" {
  name = "${local.book_store_container_name}-logs-access"
  role = aws_iam_role.book_store_task_role.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Action = [
        "logs:GetLogEvents",
        "logs:FilterLogEvents",
        "logs:DescribeLogGroups",
        "logs:DescribeLogStreams"
      ],
      Resource = "*"
    }]
  })
}

# ---------------------------
# ECS Task Definition with X-Ray Daemon
# ---------------------------
resource "aws_ecs_task_definition" "book_store" {
  family                   = "${local.book_store_container_name}-task"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.book_store_execution_role.arn
  task_role_arn            = aws_iam_role.book_store_task_role.arn

  depends_on = [aws_cloudwatch_log_group.book_store]

  container_definitions = jsonencode([
    {
      name      = "${local.book_store_container_name}"
      image     = "961341537777.dkr.ecr.ap-southeast-2.amazonaws.com/book-store:latest"
      portMappings = [
        {
          containerPort = 5000
          protocol      = "tcp"
        }
      ]
      essential = true
      environment = [
        {
          name  = "PRICE_SERVER"
          value = "book_store_price.local"
        },
        {
          name  = "AWS_XRAY_DAEMON_ADDRESS"
          value = "127.0.0.1:2000"
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.book_store.name
          "awslogs-region"        = "ap-southeast-2"
          "awslogs-stream-prefix" = "${local.book_store_container_name}"
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
          "awslogs-group"         = aws_cloudwatch_log_group.book_store.name
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
# ECS Fargate Service
# ---------------------------
resource "aws_ecs_service" "book_store" {
  name            = "${local.book_store_container_name}-service"
  cluster         = aws_ecs_cluster.main.id
  launch_type     = "FARGATE"
  task_definition = aws_ecs_task_definition.book_store.arn
  desired_count   = 1

  network_configuration {
    subnets          = var.bookStore_service_subnet_ids
    assign_public_ip = false
    security_groups  = var.bookStore_service_sg_ids
  }

  load_balancer {
    target_group_arn = var.bookStore_lb_tg_arn
    container_name   = "${local.book_store_container_name}"
    container_port   = 5000
  }
}


