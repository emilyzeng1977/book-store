# Interface VPC Endpoint = 把 AWS 的服务 "搬进" 你的私有网络里，不走公网，省钱又安全
#---------------------------------------------------
# ECR API, SSM, Secrets Manager, CloudWatch Logs 等
# 创建 ENI（网卡）
#---------------------------------------------------
resource "aws_vpc_endpoint" "ecr_api" {
  vpc_id            = data.aws_vpc.main.id
  service_name      = "com.amazonaws.ap-southeast-2.ecr.api"
  vpc_endpoint_type = "Interface"
  subnet_ids        = [aws_subnet.private.id]
  security_group_ids = [aws_security_group.vpc_endpoints.id]

  private_dns_enabled = true
}

resource "aws_vpc_endpoint" "ecr_dkr" {
  vpc_id              = data.aws_vpc.main.id
  service_name        = "com.amazonaws.ap-southeast-2.ecr.dkr"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = [aws_subnet.private.id]
  security_group_ids  = [aws_security_group.vpc_endpoints.id]

  private_dns_enabled = true
}

resource "aws_vpc_endpoint" "cloudwatch_logs" {
  vpc_id              = data.aws_vpc.main.id
  service_name        = "com.amazonaws.ap-southeast-2.logs"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = [aws_subnet.private.id]
  security_group_ids  = [aws_security_group.vpc_endpoints.id]

  private_dns_enabled = true
}

# 为 VPC Endpoint 创建一个安全组（允许 443）
resource "aws_security_group" "vpc_endpoints" {
  name        = "vpc-endpoint-sg"
  description = "Allow HTTPS for VPC endpoints"
  vpc_id      = data.aws_vpc.main.id

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = [data.aws_vpc.main.cidr_block]  # 允许内部访问
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_vpc_endpoint" "sts" {
  vpc_id            = data.aws_vpc.main.id
  service_name      = "com.amazonaws.ap-southeast-2.sts"
  vpc_endpoint_type = "Interface"
  subnet_ids        = [aws_subnet.private.id]
  security_group_ids = [aws_security_group.vpc_endpoints.id]
  private_dns_enabled = true
}

#---------------------------------------------------
# S3、DynamoDB
# 修改路由表
#---------------------------------------------------
resource "aws_vpc_endpoint" "s3" {
  vpc_id            = data.aws_vpc.main.id
  service_name      = "com.amazonaws.ap-southeast-2.s3"
  vpc_endpoint_type = "Gateway"
  route_table_ids   = [aws_route_table.private_rt.id]
}

# 接收 Atlas 发起的 VPC Peering（你需要填上 Atlas 提供的 peering connection id）
# 在请求里已经包含了VPC的ID, 所以不需要显式的提供
resource "aws_vpc_peering_connection_accepter" "atlas_peer" {
  vpc_peering_connection_id = "pcx-027d7792fdf057750"  # 从 Atlas UI 获取
  auto_accept               = true
}

