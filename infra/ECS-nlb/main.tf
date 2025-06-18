provider "aws" {
  region = var.aws_region
}

module "network" {
  source             = "./network-module"
  enable_nat_gateway = true
  enable_interface_vpc_endpoint = true
  project_name       = var.project_name
  # enable_vpc_flow_log = true
}

module "apigw" {
  source             = "./apigateway-module"

  project_name       = var.project_name
  private_subnet_ids = [module.network.private_subnet_id]
  ecs_service_sg_id  = aws_security_group.vpc_link_sg.id
  nlb_listener_arn   = aws_lb_listener.nlb_listener.arn
}

module "ecs" {
  source                       = "./ecs-module"

  project_name                 = var.project_name
  bookStore_service_subnet_ids = [module.network.private_subnet_id]
  bookStore_service_sg_ids     = [aws_security_group.ecs_fargate_sg.id]
  bookStore_lb_tg_arn          = aws_lb_target_group.ecs_tg.arn
}