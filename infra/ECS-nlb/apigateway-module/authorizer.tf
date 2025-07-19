#------------------------------------------------
# 创建一个 Lambda 函数，包括 IAM 权限、CloudWatch 日志、打包代码等
#------------------------------------------------
module "authorizer_lambda" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "~> 6.0"

  function_name = "${var.project_name}-lambda"
  handler       = "main.lambda_handler"
  runtime       = "python3.12"

  # 👇 指向 src 目录
  source_path = "${path.module}/src"

  build_in_docker = true

  # ✅ 推荐设置 memory 和 timeout
  memory_size = 256
  timeout     = 10

  attach_policy_statements = true

  policy_statements = [
    {
      effect = "Allow"
      actions = [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ]
      resources = ["arn:aws:logs:*:*:*"]
    }
  ]

  # ✅ 添加环境变量
  environment_variables = {
    USER_POOL_ID  = "ap-southeast-2_09CeFqveZ"
    APP_CLIENT_ID = "1ktmj89m2g93t3pbb2u24mbl6s"
  }
}
#------------------------------------------------
# Lambda Authorizer 配置资源，用于 AWS API Gateway v2 (HTTP API)
#------------------------------------------------
resource "aws_apigatewayv2_authorizer" "lambda_auth" {
  name                             = "${var.project_name}-authorizer"
  api_id                           = data.aws_apigatewayv2_api.http_api.id
  authorizer_type                  = "REQUEST"
  authorizer_uri                   = "arn:aws:apigateway:${var.aws_region}:lambda:path/2015-03-31/functions/${module.authorizer_lambda.lambda_function_arn}/invocations"
  identity_sources                 = var.use_cookie_auth ? [
    "$request.header.Cookie"
  ] : [
    "$request.header.Authorization"
  ]
  authorizer_payload_format_version = "2.0"
  enable_simple_responses           = true
}
#------------------------------------------------
# Lambda 函数权限配置，允许 API Gateway 调用该 Lambda Authorizer
#------------------------------------------------
resource "aws_lambda_permission" "apigw_invoke_auth" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = module.authorizer_lambda.lambda_function_name
  principal     = "apigateway.amazonaws.com"

  # 👇 确保匹配你的 API Gateway ARN
  source_arn = "${data.aws_apigatewayv2_api.http_api.execution_arn}/*"

  depends_on = [
    module.authorizer_lambda,
    aws_apigatewayv2_authorizer.lambda_auth
  ]
}
