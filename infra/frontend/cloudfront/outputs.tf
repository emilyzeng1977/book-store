output "cloud_front_url" {
  description = "The public URL of the CloudFront distribution"
  value       = "http://${aws_cloudfront_distribution.cdn.domain_name}"
}