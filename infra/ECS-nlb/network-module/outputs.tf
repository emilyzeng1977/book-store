output "vpc_id" {
  description = "The ID of the vpc"
  value       = aws_vpc.main.id
}

output "public_subnet_id" {
  description = "The ID of the public subnet"
  value       = aws_subnet.public.id
}


output "private_subnet_id" {
  description = "The ID of the private subnet"
  value       = aws_subnet.private.id
}

