# aws_vpc 和 IGW
# resource "aws_vpc" "main" {
#   cidr_block = var.vpc_cidr
#   # -----------------------------------
#   # 启用 VPC 内的 DNS 解析，允许解析 AWS 服务和内部资源的私有域名
#   # 建议始终开启（默认 true）
#   # -----------------------------------
#   enable_dns_support = true
#
#   # -----------------------------------
#   # 启用子网实例自动分配 DNS 主机名（例如 EC2 实例的私有 DNS 名称）
#   # 建议在使用 Interface VPC Endpoint 时开启，否则 DNS 解析可能失败
#   # -----------------------------------
#   enable_dns_hostnames = var.enable_interface_vpc_endpoint
#
#   tags = {
#     Name = var.project_name
#   }
# }

data "aws_vpc" "main" {
  id = "vpc-064fb58bd18cc2c75"
}

resource "aws_internet_gateway" "igw" {
  vpc_id = data.aws_vpc.main.id
}
