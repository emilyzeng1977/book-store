provider "aws" {
  region = "ap-southeast-2"  # 指定AWS区域，新加坡区域
}

# ---------------------------
# VPC 及网络配置
# ---------------------------

resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"  # VPC的IP地址范围
}

resource "aws_subnet" "public_subnet" {
  vpc_id            = aws_vpc.main.id       # 关联到上面创建的VPC
  cidr_block        = "10.0.1.0/24"         # 子网的IP地址范围
  availability_zone = "ap-southeast-2a"     # 可用区，指定在该区域的某个分区
#   map_public_ip_on_launch = true             # 启动实例时自动分配公网IP
}

resource "aws_subnet" "public_subnet_b" {
  vpc_id            = aws_vpc.main.id       # 关联到上面创建的VPC
  cidr_block        = "10.0.4.0/24"         # 子网的IP地址范围
  availability_zone = "ap-southeast-2b"     # 可用区，指定在该区域的某个分区
#   map_public_ip_on_launch = true             # 启动实例时自动分配公网IP
}

resource "aws_subnet" "private_subnet" {
  vpc_id            = aws_vpc.main.id       # 关联到上面创建的VPC
  cidr_block        = "10.0.3.0/24"         # 子网的IP地址范围
  availability_zone = "ap-southeast-2a"     # 可用区，指定在该区域的某个分区
#   map_public_ip_on_launch = true             # 启动实例时自动分配公网IP
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.main.id  # 为VPC创建并绑定一个Internet网关，实现互联网访问
}

resource "aws_route_table" "public_rt" {
  vpc_id = aws_vpc.main.id  # 创建路由表并关联VPC
}

resource "aws_route" "internet_access" {
  route_table_id         = aws_route_table.public_rt.id   # 路由表ID
  destination_cidr_block = "0.0.0.0/0"             # 所有目的地（默认路由）
  gateway_id             = aws_internet_gateway.igw.id  # 通过互联网网关路由流量
}

resource "aws_route_table_association" "public_assoc" {
  subnet_id      = aws_subnet.public_subnet.id  # 将路由表关联到子网，使子网内实例有对应路由规则
  route_table_id = aws_route_table.public_rt.id
}

### 弹性 IP (Elastic IP)：为 NAT Gateway 准备 ###
resource "aws_eip" "nat" {
    domain = "vpc"
}

### NAT Gateway：用于私有子网访问外网 ###
resource "aws_nat_gateway" "main" {
  allocation_id = aws_eip.nat.id                      # 使用上面创建的弹性 IP
  subnet_id     = aws_subnet.public_subnet.id         # 部署到公有子网
}

### 私有子网的路由表 ###
resource "aws_route_table" "private_rt" {
  vpc_id = aws_vpc.main.id                                # 关联到 VPC

  route {
    cidr_block     = "0.0.0.0/0"                          # 将所有流量路由到 NAT Gateway
    nat_gateway_id = aws_nat_gateway.main.id              # 使用上面创建的 NAT Gateway
  }

  tags = {
    Name = "Emily-private-rt"                    # 为路由表命名
  }
}

### 将私有子网与路由表关联 ###
resource "aws_route_table_association" "private_asso" {
  subnet_id      = aws_subnet.private_subnet.id # 指定子网
  route_table_id = aws_route_table.private_rt.id          # 指定路由表
}

# ---------------------------
# ECS 集群配置
# ---------------------------

resource "aws_ecs_cluster" "cluster" {
  name = "fargate-cluster"  # ECS集群名称
}

# ---------------------------
# ECS 任务执行角色（IAM Role）拉镜像、写日志
# ---------------------------

resource "aws_iam_role" "ecs_task_exec_role" {
  name = "ecsTaskExecutionRole1"  # 角色名称

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
resource "aws_iam_role_policy_attachment" "ecs_exec_policy" {
  role       = aws_iam_role.ecs_task_exec_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# ---------------------------
# ECS 容器内部代码执行 AWS 操作（如 Cognito）
# ---------------------------

resource "aws_iam_role" "ecs_task_role" {
  name = "ecsTaskRole"

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

# ✅ Attach Cognito Policy (NEW)
resource "aws_iam_policy" "cognito_access_policy" {
  name        = "CognitoAccessPolicy"
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

resource "aws_iam_role_policy_attachment" "ecs_task_role_cognito" {
  role       = aws_iam_role.ecs_task_role.name
  policy_arn = aws_iam_policy.cognito_access_policy.arn
}

# ---------------------------
# 安全组配置，控制网络访问
# ---------------------------

resource "aws_security_group" "ecs_sg" {
  name   = "fargate-sg"          # 安全组名称
  vpc_id = aws_vpc.main.id       # 关联VPC

  ingress {
    from_port   = 5000           # 入站规则，允许TCP 5000端口访问
    to_port     = 5000
    protocol    = "tcp"
    security_groups = [aws_security_group.alb_sg.id]
  }

  egress {
    from_port   = 0              # 出站规则，允许所有端口和协议访问
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]  # 允许访问所有IP
  }
}

# ---------------------------
# ECS 任务定义，描述容器和资源需求
# ---------------------------

resource "aws_ecs_task_definition" "bookstore_task" {
  family                   = "bookstore-task"          # 任务族名称
  requires_compatibilities = ["FARGATE"]               # 使用Fargate启动
  network_mode             = "awsvpc"                  # 网络模式，支持弹性网络接口
  cpu                      = "256"                     # CPU资源配置
  memory                   = "512"                     # 内存资源配置
  execution_role_arn       = aws_iam_role.ecs_task_exec_role.arn  # 拉镜像、写日志
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  depends_on = [aws_cloudwatch_log_group.bookstore]

  # 容器定义，包含镜像、端口映射
  container_definitions = jsonencode([
    {
      name  = "bookstore"          # 容器名称
      # image = "zengemily79/book-store:1.0.0-SNAPSHOT"  # 镜像地址
      image = "zengemily79/book-store:1.4.0-SNAPSHOT"  # 镜像地址
      portMappings = [
        {
          containerPort = 5000     # 容器内端口
          hostPort      = 5000     # 映射到宿主机端口
        }
      ]
      logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = "/ecs/bookstore"                  # CloudWatch Log Group 名称
        "awslogs-region"        = "ap-southeast-2"                  # 区域
        "awslogs-stream-prefix" = "bookstore"                       # 日志流前缀，方便区分不同任务或容器
      }
    }
    }
  ])
}

# ---------------------------
# 1. ALB Security Group
# ---------------------------
resource "aws_security_group" "alb_sg" {
  name        = "alb-sg"
  description = "Allow HTTP inbound from internet"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# ---------------------------
# 2. Application Load Balancer
# ---------------------------
resource "aws_lb" "ecs_alb" {
  name               = "bookstore-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb_sg.id]
  subnets            = [aws_subnet.public_subnet.id, aws_subnet.public_subnet_b.id]
}

# ---------------------------
# 3. Target Group
# ---------------------------
resource "aws_lb_target_group" "ecs_tg" {
  name        = "bookstore-tg1"
  port        = 5000
  protocol    = "HTTP"
  target_type = "ip"
  vpc_id      = aws_vpc.main.id

  health_check {
    path     = "/books"
    protocol = "HTTP"
  }
}

# ---------------------------
# 4. ALB Listener
# ---------------------------
resource "aws_lb_listener" "ecs_listener" {
  load_balancer_arn = aws_lb.ecs_alb.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.ecs_tg.arn
  }
}

# ---------------------------
# 5. ECS Fargate Service (with ALB)
# ---------------------------
resource "aws_ecs_service" "bookstore_service" {
  name            = "bookstore-service-v2"
  cluster         = aws_ecs_cluster.cluster.id
  task_definition = aws_ecs_task_definition.bookstore_task.arn
  launch_type     = "FARGATE"
  desired_count   = 1

  network_configuration {
    subnets          = [aws_subnet.private_subnet.id]
    assign_public_ip = false
    security_groups  = [aws_security_group.ecs_sg.id]
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.ecs_tg.arn
    container_name   = "bookstore"
    container_port   = 5000
  }

  depends_on = [
    aws_iam_role_policy_attachment.ecs_exec_policy,
    aws_lb_listener.ecs_listener
  ]
}

resource "aws_cloudwatch_log_group" "bookstore" {
  name              = "/ecs/bookstore"
  retention_in_days = 1   # 日志保留天数，根据需求调整
}

output "alb_dns_name" {
  description = "The DNS name of the ALB"
  value       = aws_lb.ecs_alb.dns_name
}
