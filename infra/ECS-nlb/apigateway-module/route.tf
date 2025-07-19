resource "aws_apigatewayv2_route" "proxy_route" {
  api_id    = data.aws_apigatewayv2_api.http_api.id
  route_key = "ANY /{proxy+}"
  target    = "integrations/${aws_apigatewayv2_integration.vpc_link_integration.id}"

  authorization_type = "CUSTOM"
  authorizer_id      = aws_apigatewayv2_authorizer.lambda_auth.id
}

resource "aws_apigatewayv2_route" "auth_proxy_route" {
  api_id    = data.aws_apigatewayv2_api.http_api.id
  route_key = "ANY /auth/{proxy+}"
  target    = "integrations/${aws_apigatewayv2_integration.vpc_link_integration.id}"
}

resource "aws_apigatewayv2_route" "options_route" {
  api_id    = data.aws_apigatewayv2_api.http_api.id
  route_key = "OPTIONS /{proxy+}"
  target    = "integrations/${aws_apigatewayv2_integration.vpc_link_integration.id}"
}