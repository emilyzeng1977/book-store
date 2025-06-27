output "api_endpoint" {
  description = "The http api endpoint"
  value       = data.aws_apigatewayv2_api.http_api.api_endpoint
}