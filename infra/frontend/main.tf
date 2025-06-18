provider "aws" {
  region = "ap-southeast-2"
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

  aws_region   = var.aws_region
  project_name = "${var.project_name}"
  static_website_domain_name = module.static_site.static_website_domain_name
}