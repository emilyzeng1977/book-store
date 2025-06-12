resource "aws_ecs_service" "book-store" {
  name            = "book-store-service"
  cluster         = aws_ecs_cluster.main.id
  launch_type     = "FARGATE"
  task_definition = aws_ecs_task_definition.book-store.arn
  desired_count   = 1

  network_configuration {
    subnets          = var.bookStore_service_subnet_ids
    assign_public_ip = false
    security_groups  = var.bookStore_service_sg_ids
  }

  load_balancer {
    target_group_arn = var.bookStore_lb_tg_arn
    container_name   = "book-store"
    container_port   = 5000
  }
  # depends_on = [aws_lb_listener.nlb_listener]
}
