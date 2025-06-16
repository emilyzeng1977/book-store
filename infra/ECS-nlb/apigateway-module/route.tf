resource "aws_apigatewayv2_route" "proxy_route" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "ANY /{proxy+}"
  target    = "integrations/${aws_apigatewayv2_integration.vpc_link_integration.id}"
}

resource "aws_apigatewayv2_route" "auth_proxy_route" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "ANY /auth/{proxy+}"
  target    = "integrations/${aws_apigatewayv2_integration.vpc_link_integration.id}"
}