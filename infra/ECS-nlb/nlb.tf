resource "aws_lb" "nlb" {
  name = "${var.project_name}-nlb"
  internal           = true
  load_balancer_type = "network"
  subnets            = [module.network.private_subnet_id]
  security_groups    = [aws_security_group.nlb_sg.id]
}

resource "aws_lb_target_group" "ecs_tg" {
  name        = "book-store-tg"
  port        = 5000
  protocol    = "TCP"
  vpc_id      = module.network.vpc_id
  target_type = "ip"
}

resource "aws_lb_listener" "nlb_listener" {
  load_balancer_arn = aws_lb.nlb.arn
  port              = 80
  protocol          = "TCP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.ecs_tg.arn
  }
}
