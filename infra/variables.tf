variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "environment" {
  description = "Environment (e.g., dev, prod)"
  type        = string
  default     = "dev"
}

variable "database_name" {
  description = "Name of the Glue database"
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