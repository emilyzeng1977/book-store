resource "aws_apigatewayv2_vpc_link" "vpc_link" {
  name               = "${var.project_name}-vpc-link"
  subnet_ids         = var.private_subnet_ids
  security_group_ids = [var.ecs_service_sg_id]
}