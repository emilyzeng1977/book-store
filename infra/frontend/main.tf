provider "aws" {
  region = "ap-southeast-2"
}

module "static_site" {
  source     = "./static_site"

  aws_region   = var.aws_region
  bucket_name = "${var.project_name}-tomniu"
  frontend_src = "${path.module}/../../app/frontend"
}