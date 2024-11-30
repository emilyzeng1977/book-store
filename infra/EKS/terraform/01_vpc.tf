# VPC 部分：提供基础的网络环境，所有资源都部署在 VPC 中。
# 子网部分：区分公有和私有子网，公有子网连接到 Internet Gateway，私有子网通过 NAT Gateway 访问外网。
# Internet Gateway 和 NAT Gateway：分别用于公有子网和私有子网的外网访问。
# 路由表和关联：定义流量规则并将子网绑定到对应的路由表。

# 数据块：获取可用的可用区（AZ）
data "aws_availability_zones" "available" {
  state = "available" # 仅选择状态为“可用”的可用区，确保部署的资源稳定
}

# VPC 的 IP 范围为 10.0.0.0/16
### VPC：创建虚拟私有云 ###
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr              # 定义 VPC 的 CIDR 范围
  enable_dns_support   = true                      # 启用内部 DNS 支持，便于域名解析
  enable_dns_hostnames = true                      # 启用主机名解析，便于通过实例名称访问

  tags = {
    Name = "${var.project}-vpc"                    # 为 VPC 添加标签，方便管理
  }
}

### 公有子网 ###
resource "aws_subnet" "public_subnet" {
  count                   = length(var.public_subnet_cidrs) # 根据变量定义的 CIDR 数量动态创建多个子网
  vpc_id                  = aws_vpc.main.id                 # 关联到上面创建的 VPC
  cidr_block              = var.public_subnet_cidrs[count.index] # 分配每个子网的 CIDR 块
  map_public_ip_on_launch = true                            # 自动为实例分配公有 IP
  availability_zone       = element(data.aws_availability_zones.available.names, count.index) # 将子网分布到不同的可用区

  tags = {
    Name = "${var.project}-public-${count.index}"           # 为每个子网命名
  }
}

### 私有子网 ###
resource "aws_subnet" "private_subnet" {
  count             = length(var.private_subnet_cidrs)      # 动态创建多个私有子网
  vpc_id            = aws_vpc.main.id                      # 关联到上面创建的 VPC
  cidr_block        = var.private_subnet_cidrs[count.index] # 分配每个子网的 CIDR 块
  availability_zone = element(data.aws_availability_zones.available.names, count.index) # 将子网分布到不同的可用区

  tags = {
    Name = "${var.project}-private-${count.index}"          # 为每个子网命名
  }
}

### Internet Gateway：连接 VPC 与公网 ###
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id                                # 关联到上面创建的 VPC

  tags = {
    Name = "${var.project}-igw"                           # 为 Internet Gateway 命名
  }
}

### 公有子网的路由表 ###
resource "aws_route_table" "public_rt" {
  vpc_id = aws_vpc.main.id                                # 关联到 VPC

  route {
    cidr_block = "0.0.0.0/0"                              # 将所有流量路由到 Internet Gateway
    gateway_id = aws_internet_gateway.main.id             # 使用上面创建的 Internet Gateway
  }

  tags = {
    Name = "${var.project}-public-rt"                     # 为路由表命名
  }
}

### 将公有子网与路由表关联 ###
resource "aws_route_table_association" "public_association" {
  count          = length(aws_subnet.public_subnet)       # 根据公有子网的数量创建关联
  subnet_id      = aws_subnet.public_subnet[count.index].id # 指定子网
  route_table_id = aws_route_table.public_rt.id           # 指定路由表
}

### 弹性 IP (Elastic IP)：为 NAT Gateway 准备 ###
resource "aws_eip" "nat" {
  tags = {
    Name = "${var.project}-nat-eip-${count.index}"        # 为每个弹性 IP 命名
  }
}

### NAT Gateway：用于私有子网访问外网 ###
resource "aws_nat_gateway" "main" {
  allocation_id = aws_eip.nat[0].id                       # 使用上面创建的第一个弹性 IP
  subnet_id     = aws_subnet.public_subnet[0].id          # 部署到第一个公有子网

  tags = {
    Name = "${var.project}-nat-gateway"                   # 为 NAT Gateway 命名
  }
}

### 私有子网的路由表 ###
resource "aws_route_table" "private_rt" {
  vpc_id = aws_vpc.main.id                                # 关联到 VPC

  route {
    cidr_block     = "0.0.0.0/0"                          # 将所有流量路由到 NAT Gateway
    nat_gateway_id = aws_nat_gateway.main.id              # 使用上面创建的 NAT Gateway
  }

  tags = {
    Name = "${var.project}-private-rt"                    # 为路由表命名
  }
}

### 将私有子网与路由表关联 ###
resource "aws_route_table_association" "private_association" {
  count          = length(aws_subnet.private_subnet)      # 根据私有子网的数量创建关联
  subnet_id      = aws_subnet.private_subnet[count.index].id # 指定子网
  route_table_id = aws_route_table.private_rt.id          # 指定路由表
}