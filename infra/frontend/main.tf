provider "aws" {
  region = "ap-southeast-2"
}

provider "aws" {
  alias  = "virginia"
  region = "us-east-1"
}

module "static_site" {
  source     = "./static_site"

  aws_region   = var.aws_region
  project_name = "${var.project_name}"
  bucket_name = "${var.project_name}-tomniu"
  frontend_src = "${path.module}/../../app/frontend"
}

module "cloud_front" {
  source     = "./cloudfront"

  providers = {
    aws           = aws           # 默认 provider
    aws.us_east_1 = aws.virginia  # 传递别名 provider 给模块内使用
  }

  project_name = "${var.project_name}"
  static_website_domain_name = module.static_site.static_website_domain_name
}