# API Gateway + VPC Link

resource "aws_apigatewayv2_api" "http_api" {
  name = "${var.project_name}-api"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_vpc_link" "vpc_link" {
  name               = "ecs-vpc-link"
  subnet_ids         = [aws_subnet.private.id]
  security_group_ids = [aws_security_group.ecs_service_sg.id]
}

resource "aws_apigatewayv2_integration" "vpc_link_integration" {
  api_id             = aws_apigatewayv2_api.http_api.id
  integration_type   = "HTTP_PROXY"
  connection_type    = "VPC_LINK"
  connection_id      = aws_apigatewayv2_vpc_link.vpc_link.id
  integration_method = "ANY"
  integration_uri    = aws_lb_listener.nlb_listener.arn
}

resource "aws_apigatewayv2_route" "proxy_route" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "ANY /{proxy+}"
  target    = "integrations/${aws_apigatewayv2_integration.vpc_link_integration.id}"
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.http_api.id
  name        = "$default"
  auto_deploy = true
}
