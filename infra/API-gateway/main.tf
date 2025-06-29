provider "aws" {
  region = var.aws_region
}

# 1. 获取 ACM 证书
data "aws_acm_certificate" "dev_cert" {
  domain      = "*.be-devops.shop"
  statuses    = ["ISSUED"]
  most_recent = true
}

# 2. 创建 HTTP API（API Gateway v2）
resource "aws_apigatewayv2_api" "http_api" {
  name          = "${var.project_name}-api"
  protocol_type = "HTTP"
}

# 3. 显式创建dev阶段
resource "aws_apigatewayv2_stage" "dev" {
  api_id      = aws_apigatewayv2_api.http_api.id
  name        = "dev"
  auto_deploy = true
}

# 4. 创建 API Gateway 自定义域名
resource "aws_apigatewayv2_domain_name" "custom_domain" {
  domain_name = "dev-api.be-devops.shop"

  domain_name_configuration {
    certificate_arn = data.aws_acm_certificate.dev_cert.arn
    endpoint_type   = "REGIONAL"
    security_policy = "TLS_1_2"
  }
}

# 5. 将自定义域名绑定到 API Gateway 上（使用上面创建的阶段名）
resource "aws_apigatewayv2_api_mapping" "mapping" {
  api_id      = aws_apigatewayv2_api.http_api.id
  domain_name = aws_apigatewayv2_domain_name.custom_domain.domain_name
  stage       = aws_apigatewayv2_stage.dev.name
}
