variable "aws_region" {
  type    = string
  default = "ap-southeast-2"
}

variable "environment" {
  type = string

  validation {
    condition     = contains(["staging", "production"], var.environment)
    error_message = "environment must be staging or production."
  }
}

variable "vpc_cidr" {
  type    = string
  default = "10.40.0.0/16"
}

variable "availability_zones" {
  type    = list(string)
  default = ["ap-southeast-2a", "ap-southeast-2b"]
}

variable "api_image" {
  type = string
}

variable "frontend_image" {
  type = string
}

variable "uptime_kuma_image" {
  type    = string
  default = "louislam/uptime-kuma:1"
}

variable "certificate_arn" {
  type        = string
  description = "ACM certificate covering the frontend and API host names."
}

variable "frontend_host" {
  type = string
}

variable "uptime_host" {
  type = string
}

variable "db_instance_class" {
  type    = string
  default = "db.t4g.micro"
}

variable "alert_email" {
  type    = string
  default = ""
}
