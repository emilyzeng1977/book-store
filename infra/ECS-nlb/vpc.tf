# # VPC, Subnet, IGW, NAT, Route
# #                              +--------------------+
# #                              |    Internet        |
# #                              +--------+-----------+
# #                                       |
# #                             (Internet Gateway - IGW)
# #                                       |
# #                              +--------v-----------+
# #                              |      VPC           |
# #                              |  CIDR: 10.0.0.0/16  |
# #                              +--------+-----------+
# #                                       |
# #        +------------------------------+------------------------------+
# #        |                                                             |
# # +------v------+                                             +--------v--------+
# # | Public Subnet|                                             | Private Subnet |
# # | 10.0.0.0/24  |                                             | 10.0.1.0/24     |
# # | AZ: a        |                                             | AZ: a          |
# # | MapPublicIP: ✔|                                             | MapPublicIP: ✖ |
# # +------+-------+                                             +--------+-------+
# #        |                                                             |
# #        |                                                             |
# # +------v-----------+                                         +-------v--------+
# # | Route Table:     |                                         | Route Table:   |
# # | public_rt        |                                         | private_rt     |
# # | Route:           |                                         | Route:         |
# # | 0.0.0.0/0 -> IGW |                                         | 0.0.0.0/0 ->   |
# # +------------------+                                         | NAT Gateway    |
# #                                                              +-------+--------+
# #                                                                      |
# #                                                            +---------v--------+
# #                                                            |   NAT Gateway    |
# #                                                            | In Public Subnet |
# #                                                            +---------+--------+
# #                                                                      |
# #                                                            +---------v--------+
# #                                                            | Elastic IP (EIP) |
# #                                                            +------------------+
#
# provider "aws" {
#   region = "ap-southeast-2"
# }
#
# resource "aws_vpc" "main" {
#   cidr_block = "10.0.0.0/16"
#   tags = {
#     Name = "${var.project_name}"
#   }
# }
#
# resource "aws_subnet" "public" {
#   vpc_id                  = aws_vpc.main.id
#   cidr_block              = "10.0.0.0/24"
#   availability_zone       = "ap-southeast-2a"
#   map_public_ip_on_launch = true
#   tags = {
#     Name = "${var.project_name}"
#   }
# }
#
# resource "aws_subnet" "private" {
#   vpc_id                  = aws_vpc.main.id
#   cidr_block              = "10.0.1.0/24"
#   availability_zone       = "ap-southeast-2a"
#   map_public_ip_on_launch = false
# }
#
# resource "aws_internet_gateway" "igw" {
#   vpc_id = aws_vpc.main.id
# }
#
# resource "aws_eip" "nat" {
#   vpc = true
# }
#
# resource "aws_nat_gateway" "nat" {
#   allocation_id = aws_eip.nat.id
#   subnet_id     = aws_subnet.public.id
#   depends_on    = [aws_internet_gateway.igw]
#   tags = {
#     Name = "${var.project_name}"
#   }
# }
#
# resource "aws_route_table" "public_rt" {
#   vpc_id = aws_vpc.main.id
#
#   route {
#     cidr_block = "0.0.0.0/0"
#     gateway_id = aws_internet_gateway.igw.id
#   }
# }
#
# resource "aws_route_table_association" "public_assoc" {
#   subnet_id      = aws_subnet.public.id
#   route_table_id = aws_route_table.public_rt.id
# }
#
# resource "aws_route_table" "private_rt" {
#   vpc_id = aws_vpc.main.id
#
#   route {
#     cidr_block     = "0.0.0.0/0"
#     nat_gateway_id = aws_nat_gateway.nat.id
#   }
# }
#
# resource "aws_route_table_association" "private_assoc" {
#   subnet_id      = aws_subnet.private.id
#   route_table_id = aws_route_table.private_rt.id
# }
