resource "aws_service_discovery_private_dns_namespace" "book_store" {
  name        = "local"
  vpc         = var.bookStore_vpi_id
  description = "Private DNS for ECS service discovery"
}

resource "aws_service_discovery_service" "book_store_price" {
  name = "book_store_price"

  dns_config {
    namespace_id = aws_service_discovery_private_dns_namespace.book_store.id
    dns_records {
      type = "A"
      ttl  = 10
    }
    routing_policy = "MULTIVALUE"
  }

  health_check_custom_config {
    failure_threshold = 1
  }
}