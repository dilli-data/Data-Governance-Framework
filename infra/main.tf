terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  required_version = ">= 1.0.0"
}

provider "aws" {
  region = var.aws_region
}

# S3 Data Lake Module
module "data_lake" {
  source = "./modules/data_lake"

  project_name     = var.project_name
  environment      = var.environment
  data_lake_bucket = var.data_lake_bucket
  tags            = var.tags
}

# Glue Catalog Module
module "glue_catalog" {
  source = "./modules/glue_catalog"

  project_name     = var.project_name
  environment      = var.environment
  database_name    = var.database_name
  crawler_name     = var.crawler_name
  s3_bucket_name   = module.data_lake.raw_zone_bucket
  tags            = var.tags
}

# Lake Formation Module
module "lake_formation" {
  source = "./modules/lake_formation"

  project_name     = var.project_name
  environment      = var.environment
  database_name    = var.database_name
  data_lake_admin  = var.data_lake_admin
  tags            = var.tags
}

# IAM Roles Module
module "iam_roles" {
  source = "./modules/iam_roles"

  project_name     = var.project_name
  environment      = var.environment
  data_lake_bucket = module.data_lake.raw_zone_bucket
  tags            = var.tags
}

# Variables
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "data-governance"
}

variable "environment" {
  description = "Environment"
  type        = string
  default     = "dev"
}

variable "database_name" {
  description = "Glue database name"
  type        = string
  default     = "higher_ed_data"
}

variable "data_lake_bucket" {
  description = "S3 bucket for data lake"
  type        = string
}

variable "data_lake_admin" {
  description = "Data lake admin"
  type        = string
}

variable "crawler_name" {
  description = "Glue crawler name"
  type        = string
  default     = "student_records"
}

variable "tags" {
  description = "Tags for resources"
  type        = map(string)
  default     = {}
}

# Outputs
output "data_lake_bucket" {
  value = module.data_lake.raw_zone_bucket
}

output "glue_database" {
  value = module.glue_catalog.database_name
}

output "data_steward_role" {
  value = module.iam_roles.data_steward_role
}

output "data_analyst_role" {
  value = module.iam_roles.data_analyst_role
} 