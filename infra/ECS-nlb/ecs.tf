# resource "aws_ecs_cluster" "main" {
#   name = "${var.project_name}-cluster"
# }
#
# resource "aws_ecs_task_definition" "book-store" {
#   family = "${var.project_name}-task"
#   requires_compatibilities = ["FARGATE"]
#   network_mode             = "awsvpc"
#   cpu                      = "256"
#   memory                   = "512"
#
#   container_definitions = jsonencode([
#     {
#       name      = "book-store"
#       image     = "zengemily79/book-store:latest"
#       portMappings = [
#         {
#           containerPort = 5000
#           protocol      = "tcp"
#         }
#       ]
#     }
#   ])
# }
#
# resource "aws_ecs_service" "book-store" {
#   name            = "book-store-service"
#   cluster         = aws_ecs_cluster.main.id
#   launch_type     = "FARGATE"
#   task_definition = aws_ecs_task_definition.book-store.arn
#   desired_count   = 1
#
#   network_configuration {
#     subnets         = [module.network.private_subnet_id]
#     assign_public_ip = false
#     security_groups  = [aws_security_group.ecs_service_sg.id]
#   }
#
#   load_balancer {
#     target_group_arn = aws_lb_target_group.ecs_tg.arn
#     container_name   = "book-store"
#     container_port   = 5000
#   }
#
#   depends_on = [aws_lb_listener.nlb_listener]
# }
