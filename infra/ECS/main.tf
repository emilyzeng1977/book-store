provider "aws" {
  region = "ap-southeast-2"  # 指定AWS区域，新加坡区域
}

# ---------------------------
# VPC 及网络配置
# ---------------------------

resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"  # VPC的IP地址范围
}

resource "aws_subnet" "subnet" {
  vpc_id            = aws_vpc.main.id       # 关联到上面创建的VPC
  cidr_block        = "10.0.1.0/24"         # 子网的IP地址范围
  availability_zone = "ap-southeast-2a"     # 可用区，指定在该区域的某个分区
  map_public_ip_on_launch = true             # 启动实例时自动分配公网IP
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.main.id  # 为VPC创建并绑定一个Internet网关，实现互联网访问
}

resource "aws_route_table" "rt" {
  vpc_id = aws_vpc.main.id  # 创建路由表并关联VPC
}

resource "aws_route" "internet_access" {
  route_table_id         = aws_route_table.rt.id   # 路由表ID
  destination_cidr_block = "0.0.0.0/0"             # 所有目的地（默认路由）
  gateway_id             = aws_internet_gateway.igw.id  # 通过互联网网关路由流量
}

resource "aws_route_table_association" "assoc" {
  subnet_id      = aws_subnet.subnet.id  # 将路由表关联到子网，使子网内实例有对应路由规则
  route_table_id = aws_route_table.rt.id
}

# ---------------------------
# ECS 集群配置
# ---------------------------

resource "aws_ecs_cluster" "cluster" {
  name = "fargate-cluster"  # ECS集群名称
}

# ---------------------------
# ECS 任务执行角色（IAM Role）
# ---------------------------

resource "aws_iam_role" "ecs_task_exec_role" {
  name = "ecsTaskExecutionRole"  # 角色名称

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
# 安全组配置，控制网络访问
# ---------------------------

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
  name   = "fargate-sg"          # 安全组名称
  vpc_id = aws_vpc.main.id       # 关联VPC

  ingress {
    from_port   = 5000           # 入站规则，允许TCP 5000端口访问
    to_port     = 5000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # 允许所有IP访问（公网）
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
  execution_role_arn       = aws_iam_role.ecs_task_exec_role.arn  # 任务执行角色

  # 容器定义，包含镜像、端口映射
  container_definitions = jsonencode([
    {
      name  = "bookstore"          # 容器名称
      image = "zengemily79/book-store:1.0.0-SNAPSHOT"  # 镜像地址
      portMappings = [
        {
          containerPort = 5000     # 容器内端口
          hostPort      = 5000     # 映射到宿主机端口
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
# ECS 服务，负责运行和管理任务
# ---------------------------

resource "aws_ecs_service" "bookstore_service" {
  name            = "bookstore-service"           # 服务名称
  cluster         = aws_ecs_cluster.cluster.id    # 所属ECS集群
  task_definition = aws_ecs_task_definition.bookstore_task.arn  # 关联任务定义
  launch_type     = "FARGATE"                      # 启动类型为Fargate无服务器容器
  desired_count   = 1                              # 期望启动1个任务实例

  network_configuration {
    subnets          = [aws_subnet.subnet.id]     # 任务运行的子网
    assign_public_ip = true                        # 分配公网IP，方便外部访问
    security_groups  = [aws_security_group.ecs_sg.id]  # 绑定安全组
  }

  # 依赖角色策略的附加，确保权限已准备好
  depends_on = [
    aws_iam_role_policy_attachment.ecs_exec_policy  # 确保角色权限已附加后再创建服务
  ]
}