output "api_endpoint" {
  description = "The http api endpoint"
  value       = data.aws_apigatewayv2_api.http_api.api_endpoint
}

output "auth_lambda_log_group" {
  value = module.authorizer_lambda.lambda_cloudwatch_log_group_name
}