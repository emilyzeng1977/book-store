resource "aws_route_table" "public_rt" {
  vpc_id = data.aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }
}

resource "aws_route_table" "private_rt" {
  vpc_id = data.aws_vpc.main.id

  dynamic "route" {
    for_each = var.enable_nat_gateway ? [aws_nat_gateway.nat[0].id] : []
    content {
      cidr_block     = "0.0.0.0/0"
      nat_gateway_id = route.value
    }
  }
}

resource "aws_route" "atlas_peer_route" {
  route_table_id            = aws_route_table.private_rt.id   # 你要替换成你的实际 route table
  destination_cidr_block    = "192.168.248.0/21"         # 从 Atlas 控制台获取 Atlas VPC CIDR
  vpc_peering_connection_id = aws_vpc_peering_connection_accepter.atlas_peer.id
}