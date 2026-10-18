terraform {
  required_version = ">= 1.11.0"
  # bucket get key are supplied at init time:
  #   terraform init \
  #     -backend-config="bucket=<state bucket>" \
  #     -backend-config="key=placeholder-store/<environment>.tfstate"
  backend "s3" {
    region       = "ap-southeast-2"
    use_lockfile = true
    encrypt      = true
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Application = "placeholder-store"
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}
