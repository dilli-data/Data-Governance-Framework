variable "project_name" {
  description = "Name of the project"
  type        = string
}

variable "environment" {
  description = "Environment (e.g., dev, prod)"
  type        = string
}

variable "database_name" {
  description = "Name of the Glue database"
  type        = string
}

variable "data_lake_admin" {
  description = "Data lake admin"
  type        = string
}

variable "tags" {
  description = "Tags for resources"
  type        = map(string)
  default     = {}
} 