output "frontend_url" {
  value = "https://${var.frontend_host}"
}

output "api_health_url" {
  value = "https://${var.frontend_host}/api/health/ready"
}

output "uptime_kuma_url" {
  value = "https://${var.uptime_host}"
}

output "ecs_cluster" {
  value = aws_ecs_cluster.this.name
}

output "api_service" {
  value = aws_ecs_service.api.name
}

output "frontend_service" {
  value = aws_ecs_service.frontend.name
}

output "uptime_service" {
  value = aws_ecs_service.uptime.name
}
