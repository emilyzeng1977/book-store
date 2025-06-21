# ========== 1. CloudWatch Log Group ==========
resource "aws_cloudwatch_log_group" "vpc_flow_log_group" {
  count             = var.enable_vpc_flow_log ? 1 : 0
  name              = "/vpc-flow-logs/"
  retention_in_days = 30  # 可根据需要设置为 7, 30, 90 等
}

# ========== 2. IAM Role for VPC Flow Logs ==========
resource "aws_iam_role" "vpc_flow_log_role" {
  count = var.enable_vpc_flow_log ? 1 : 0
  name  = "vpc-flow-logs-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "vpc-flow-logs.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })
}

# ========== 3. IAM Policy Attachment ==========
resource "aws_iam_role_policy_attachment" "vpc_flow_log_attach" {
  count      = var.enable_vpc_flow_log ? 1 : 0
  role       = aws_iam_role.vpc_flow_log_role[0].name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonAPIGatewayPushToCloudWatchLogs"
}

# 可选：手动写一个最小权限策略也行，使用 AWS 托管策略更简单

# ========== 4. 启用 VPC Flow Log ==========
resource "aws_flow_log" "vpc_flow" {
  count                = var.enable_vpc_flow_log ? 1 : 0
  log_destination_type = "cloud-watch-logs"
  log_destination      = aws_cloudwatch_log_group.vpc_flow_log_group[0].arn
  iam_role_arn         = aws_iam_role.vpc_flow_log_role[0].arn
  traffic_type         = "ALL"  # 可选值: ACCEPT, REJECT, ALL
  vpc_id               = data.aws_vpc.main.id
}