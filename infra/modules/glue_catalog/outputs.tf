output "database_name" {
  description = "Name of the Glue database"
  value       = aws_glue_catalog_database.data_governance.name
}

output "crawler_name" {
  description = "Name of the Glue crawler"
  value       = aws_glue_crawler.data_governance.name
}

output "crawler_role_arn" {
  description = "ARN of the Glue crawler IAM role"
  value       = aws_iam_role.glue_crawler.arn
} 