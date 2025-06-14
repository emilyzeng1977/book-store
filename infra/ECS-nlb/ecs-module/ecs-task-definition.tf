resource "aws_ecs_task_definition" "book-store" {
  family        = "${var.project_name}-task"
  requires_compatibilities = ["FARGATE"]
  network_mode  = "awsvpc"
  cpu           = "256"
  memory        = "512"
  execution_role_arn = aws_iam_role.ecs_task_exec_role.arn  # 拉镜像、写日志
  task_role_arn = aws_iam_role.ecs_task_role.arn

  depends_on = [aws_cloudwatch_log_group.bookstore]

  container_definitions = jsonencode([
    {
      name  = "book-store"
      image = "zengemily79/book-store:latest"
      portMappings = [
        {
          containerPort = 5000
          protocol      = "tcp"
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group" = "/ecs/bookstore"                  # CloudWatch Log Group 名称
          "awslogs-region" = "ap-southeast-2"                  # 区域
          "awslogs-stream-prefix" = "bookstore"                       # 日志流前缀，方便区分不同任务或容器
        }
      }
    }
  ])
}

resource "aws_cloudwatch_log_group" "bookstore" {
  name              = "/ecs/bookstore"
  retention_in_days = 1   # 日志保留天数，根据需求调整
}

