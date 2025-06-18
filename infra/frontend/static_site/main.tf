provider "aws" {
  region = var.aws_region
}

# 创建 S3 桶，用于托管静态网站
resource "aws_s3_bucket" "static_site" {
  bucket = var.bucket_name
  force_destroy = true

  tags = {
    Name = "${var.project_name}"
  }
}

# 取消 S3 桶的“公共访问阻止”设置，允许公开访问
resource "aws_s3_bucket_public_access_block" "public_access" {
  bucket = aws_s3_bucket.static_site.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

# 设置桶策略，允许所有用户读取桶中的对象（公开访问）
resource "aws_s3_bucket_policy" "public_read" {
  depends_on = [aws_s3_bucket_public_access_block.public_access]
  bucket = aws_s3_bucket.static_site.id
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect    = "Allow",
      Principal = "*",
      Action    = ["s3:GetObject"],
      Resource  = "${aws_s3_bucket.static_site.arn}/*"
    }]
  })
}

# 上传本地 website 目录下的所有文件到 S3 桶中
resource "aws_s3_object" "website_files" {
  for_each = fileset("${var.frontend_src}", "**")

  bucket = aws_s3_bucket.static_site.bucket
  key    = each.value

  source = "${var.frontend_src}/${each.value}"
  etag   = filemd5("${var.frontend_src}/${each.value}")

  depends_on = [aws_s3_bucket_public_access_block.public_access] # 👈 加上这个

  content_type = lookup({
    html = "text/html"
    css  = "text/css"
    js   = "application/javascript"
  }, split(".", each.value)[length(split(".", each.value)) - 1], "application/octet-stream")
}

# 配置 S3 桶为静态网站托管，设置默认首页和错误页
resource "aws_s3_bucket_website_configuration" "static_site" {
  bucket = aws_s3_bucket.static_site.id

  index_document {
    suffix = "index.html"
  }

  error_document {
    key = "error.html"
  }
}


