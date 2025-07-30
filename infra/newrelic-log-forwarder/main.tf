locals {
  forwarder_lambda_arn = "arn:aws:lambda:ap-southeast-2:961341537777:function:newrelic-log-ingestion"
  forwarder_lambda_function_name = "newrelic-log-ingestion"
}

provider "aws" {
  region = "ap-southeast-2"
}
#------------------------------------------------
# book_store
#------------------------------------------------
resource "aws_cloudwatch_log_subscription_filter" "book_store" {
  name            = "forward-book-store-logs"
  log_group_name  = "/ecs/book_store"  # 指定你想转发的 log group
  filter_pattern  = "\"request_headers\"" # 空表示不过滤，全部转发
  destination_arn = local.forwarder_lambda_arn
  depends_on      = [aws_lambda_permission.book_store]
}

resource "aws_lambda_permission" "book_store" {
  statement_id  = "AllowExecutionFromCloudWatchBookStore"
  action        = "lambda:InvokeFunction"
  function_name = local.forwarder_lambda_function_name
  principal     = "logs.amazonaws.com"
  source_arn    = "arn:aws:logs:ap-southeast-2:961341537777:log-group:/ecs/book_store:*"
}
#------------------------------------------------
# book_store_price
#------------------------------------------------
resource "aws_cloudwatch_log_subscription_filter" "book_store_price" {
  name            = "forward-book-store-logs"
  log_group_name  = "/ecs/book_store_price"  # 指定你想转发的 log group
  filter_pattern  = ""                 # 空表示不过滤，全部转发
  destination_arn = local.forwarder_lambda_arn
  depends_on      = [aws_lambda_permission.book_store]
}

resource "aws_lambda_permission" "book_store_price" {
  statement_id  = "AllowExecutionFromCloudWatchBookStorePrice"
  action        = "lambda:InvokeFunction"
  function_name = local.forwarder_lambda_function_name
  principal     = "logs.amazonaws.com"
  source_arn    = "arn:aws:logs:ap-southeast-2:961341537777:log-group:/ecs/book_store_price:*"
}