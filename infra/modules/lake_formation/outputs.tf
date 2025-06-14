output "data_lake_settings" {
  description = "Lake Formation data lake settings"
  value       = aws_lakeformation_data_lake_settings.data_governance
}

output "database_permissions" {
  description = "Lake Formation database permissions"
  value       = aws_lakeformation_permissions.database
}

output "table_permissions" {
  description = "Lake Formation table permissions"
  value       = aws_lakeformation_permissions.table
} 