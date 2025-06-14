output "data_steward_role" {
  description = "ARN of the data steward IAM role"
  value       = aws_iam_role.data_steward.arn
}

output "data_analyst_role" {
  description = "ARN of the data analyst IAM role"
  value       = aws_iam_role.data_analyst.arn
}

output "data_engineer_role" {
  description = "ARN of the data engineer IAM role"
  value       = aws_iam_role.data_engineer.arn
} 