locals {
  book_store_price_container_name = "book_store_price"
}

# ---------------------------
# 创建 CloudWatch Log Group，用于存储 ECS 任务的容器日志
# ---------------------------
resource "aws_cloudwatch_log_group" "book_store_price" {
  name              = "/ecs/${local.book_store_price_container_name}"
  retention_in_days = 1   # 日志保留天数，根据需求调整
}

# ---------------------------
# ECS 任务执行角色（IAM Role）拉镜像、写日志
# ---------------------------
resource "aws_iam_role" "book_store_price_execution_role" {
  name = "${local.book_store_price_container_name}_execution_role"  # 角色名称

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
resource "aws_iam_role_policy_attachment" "book_store_price_execution_policy_attach" {
  role       = aws_iam_role.book_store_price_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# ---------------------------
# ECS 容器内部代码执行 AWS 操作（如 Cognito）
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
# ---------------------------
# 定义 ECS Fargate 的任务定义，包括容器配置、日志设置、CPU/内存等
# ---------------------------
resource "aws_ecs_task_definition" "book_store_price" {
  family                   = "${local.book_store_price_container_name}-task"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn = aws_iam_role.book_store_price_execution_role.arn  # 拉镜像、写日志
  task_role_arn = aws_iam_role.book_store_price_task_role.arn

  depends_on = [aws_cloudwatch_log_group.book_store_price]

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
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group" = aws_cloudwatch_log_group.book_store_price.name # CloudWatch Log Group 名称
          "awslogs-region" = "ap-southeast-2"                              # 区域
          "awslogs-stream-prefix" = "${local.book_store_price_container_name}"              # 日志流前缀，方便区分不同任务或容器
        }
      }
    }
  ])
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
    # 此处也用了和book_store一样的SG, 因为book-store-price也是监听5000端口
    security_groups  = var.bookStore_service_sg_ids
  }
}