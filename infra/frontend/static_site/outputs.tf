output "website_url" {
  value = "http://${aws_s3_bucket.frontend.bucket}.s3-website-${var.aws_region}.amazonaws.com"
}

output "domain_name" {
  value = "${aws_s3_bucket.frontend.bucket}.s3-website-${var.aws_region}.amazonaws.com"
}
