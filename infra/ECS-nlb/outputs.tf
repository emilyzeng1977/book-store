output "api_url" {
  value = module.apigw.api_endpoint
  description = "URL of http api"
}

output "gateway_auth_log_group" {
  value = module.apigw.auth_lambda_log_group
}