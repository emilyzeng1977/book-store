provider "aws" {
  region = "ap-southeast-2"  # 指定AWS区域
}

# ---------------------------
# VPC 及网络配置
# ---------------------------

resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"  # VPC的IP地址范围
}

resource "aws_subnet" "subnet" {
  vpc_id                 = aws_vpc.main.id  # 关联到上面创建的VPC
  cidr_block             = "10.0.1.0/24"    # 子网的IP地址范围
  availability_zone      = "ap-southeast-2a" # 可用区
  map_public_ip_on_launch = true             # 启动时自动分配公网IP
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.main.id  # 互联网网关关联到VPC
}

resource "aws_route_table" "rt" {
  vpc_id = aws_vpc.main.id  # 路由表绑定到VPC
}

resource "aws_route" "internet_access" {
  route_table_id         = aws_route_table.rt.id
  destination_cidr_block = "0.0.0.0/0"          # 默认路由，访问所有地址
  gateway_id             = aws_internet_gateway.igw.id # 通过互联网网关出去
}

resource "aws_route_table_association" "assoc" {
  subnet_id      = aws_subnet.subnet.id       # 子网绑定路由表，决定网络流向
  route_table_id = aws_route_table.rt.id
}

# ---------------------------
# ECS 集群
# ---------------------------

resource "aws_ecs_cluster" "cluster" {
  name = "fargate-cluster"  # 集群名称
}

# ---------------------------
# ECS Task执行角色 (IAM Role)
# ---------------------------

resource "aws_iam_role" "ecs_task_exec_role" {
  name = "ecsTaskExecutionRole"

  # 允许 ECS 任务使用该角色
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect    = "Allow",
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      },
      Action = "sts:AssumeRole"
    }]
  })
}

# 附加AWS官方托管策略，赋予基础执行权限（比如拉镜像、写日志等）
resource "aws_iam_role_policy_attachment" "ecs_exec_policy" {
  role       = aws_iam_role.ecs_task_exec_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# ---------------------------
# 自定义托管策略：允许读取 SSM 参数
# ---------------------------

resource "aws_iam_policy" "ssm_read_policy" {
  name        = "AllowSSMParameterRead"
  description = "允许 ECS 任务读取 SSM 参数存储中的参数"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect   = "Allow",
        Action   = [
          "ssm:GetParameter",
          "ssm:GetParameters"
        ],
        Resource = aws_ssm_parameter.datadog_api_key.arn  # 仅允许访问指定参数
      }
    ]
  })
}

# 将自定义托管策略附加给 ECS 任务执行角色
resource "aws_iam_role_policy_attachment" "ssm_read_policy_attachment" {
  role       = aws_iam_role.ecs_task_exec_role.name
  policy_arn = aws_iam_policy.ssm_read_policy.arn
}

# ---------------------------
# SSM 参数存储，保存Datadog API Key
# ---------------------------

resource "aws_ssm_parameter" "datadog_api_key" {
  name  = "/datadog/api_key"    # 参数名称，建议用路径规范
  type  = "SecureString"        # 安全字符串，参数会加密存储
  value = "your_datadog_api_key_here"  # 真实的密钥值
}

# ---------------------------
# ECS 服务所用安全组
# ---------------------------

resource "aws_security_group" "ecs_sg" {
  name   = "fargate-sg"
  vpc_id = aws_vpc.main.id

  # 允许外部通过TCP 5000端口访问服务
  ingress {
    from_port   = 5000
    to_port     = 5000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # 允许所有出站流量
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# ---------------------------
# ECS 任务定义
# ---------------------------

resource "aws_ecs_task_definition" "bookstore_task" {
  family                   = "bookstore-task"  # 任务定义名称
  requires_compatibilities = ["FARGATE"]       # 使用Fargate启动
  network_mode             = "awsvpc"          # 网络模式，awsvpc支持弹性网络接口
  cpu                      = "256"             # CPU资源
  memory                   = "512"             # 内存资源
  execution_role_arn       = aws_iam_role.ecs_task_exec_role.arn  # 使用上面定义的执行角色

  # 容器定义，定义镜像、端口和环境变量（秘密）
  container_definitions = jsonencode([
    {
      name  = "bookstore"
      image = "zengemily79/book-store:1.0.0-SNAPSHOT"
      portMappings = [
        {
          containerPort = 5000
          hostPort      = 5000
        }
      ]
      secrets = [
        {
          name      = "DD_API_KEY"                     # 容器内的环境变量名
          valueFrom = aws_ssm_parameter.datadog_api_key.arn  # 关联SSM参数的ARN，注入机密
        }
      ]
    }
  ])
}

# ---------------------------
# ECS 服务，运行任务
# ---------------------------

resource "aws_ecs_service" "bookstore_service" {
  name            = "bookstore-service"           # 服务名称
  cluster         = aws_ecs_cluster.cluster.id    # 关联集群
  task_definition = aws_ecs_task_definition.bookstore_task.arn  # 任务定义
  launch_type     = "FARGATE"                      # 启动方式Fargate
  desired_count   = 1                              # 期望运行的任务数

  network_configuration {
    subnets          = [aws_subnet.subnet.id]     # 使用的子网
    assign_public_ip = true                        # 分配公网IP
    security_groups  = [aws_security_group.ecs_sg.id]  # 绑定安全组
  }

  # 依赖角色策略的附加，确保权限已准备好
  depends_on = [
    aws_iam_role_policy_attachment.ecs_exec_policy,
    aws_iam_role_policy_attachment.ssm_read_policy_attachment
  ]
}
