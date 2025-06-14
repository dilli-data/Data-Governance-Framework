provider "aws" {
  region = var.aws_region
}

# S3 buckets for data lake
resource "aws_s3_bucket" "data_lake" {
  bucket = "${var.project_name}-data-lake"
  
  tags = {
    Name        = "${var.project_name}-data-lake"
    Environment = var.environment
  }
}

resource "aws_s3_bucket_versioning" "data_lake" {
  bucket = aws_s3_bucket.data_lake.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "data_lake" {
  bucket = aws_s3_bucket.data_lake.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# IAM roles for data governance
resource "aws_iam_role" "data_steward" {
  name = "${var.project_name}-data-steward"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "glue.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role" "data_analyst" {
  name = "${var.project_name}-data-analyst"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "glue.amazonaws.com"
        }
      }
    ]
  })
}

# Lake Formation permissions
resource "aws_lakeformation_permissions" "data_steward" {
  principal   = aws_iam_role.data_steward.arn
  permissions = ["ALL"]
  resource {
    database {
      name = var.database_name
    }
  }
}

resource "aws_lakeformation_permissions" "data_analyst" {
  principal   = aws_iam_role.data_analyst.arn
  permissions = ["SELECT"]
  resource {
    database {
      name = var.database_name
    }
  }
}

# Glue database
resource "aws_glue_catalog_database" "data_governance" {
  name = var.database_name
}

# Glue crawler
resource "aws_glue_crawler" "student_records" {
  name          = "${var.project_name}-student-records-crawler"
  database_name = aws_glue_catalog_database.data_governance.name
  role          = aws_iam_role.data_steward.arn

  s3_target {
    path = "s3://${aws_s3_bucket.data_lake.bucket}/raw/student_records/"
  }

  schedule = "cron(0 0 * * ? *)"
}

# CloudWatch log group for data governance
resource "aws_cloudwatch_log_group" "data_governance" {
  name              = "/data-governance/access-logs"
  retention_in_days = 90
}

# SNS topic for alerts
resource "aws_sns_topic" "data_governance_alerts" {
  name = "${var.project_name}-data-governance-alerts"
}

# CloudWatch alarms
resource "aws_cloudwatch_metric_alarm" "data_quality" {
  alarm_name          = "${var.project_name}-data-quality-alarm"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "DataQualityScore"
  namespace           = "DataGovernance"
  period             = "300"
  statistic          = "Average"
  threshold          = "0.95"
  alarm_description  = "Data quality score below threshold"
  alarm_actions      = [aws_sns_topic.data_governance_alerts.arn]
}

resource "aws_cloudwatch_metric_alarm" "access_violations" {
  alarm_name          = "${var.project_name}-access-violations-alarm"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "AccessViolations"
  namespace           = "DataGovernance"
  period             = "300"
  statistic          = "Sum"
  threshold          = "0"
  alarm_description  = "Data access policy violations detected"
  alarm_actions      = [aws_sns_topic.data_governance_alerts.arn]
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

# Outputs
output "data_lake_bucket" {
  value = aws_s3_bucket.data_lake.bucket
}

output "glue_database" {
  value = aws_glue_catalog_database.data_governance.name
}

output "data_steward_role" {
  value = aws_iam_role.data_steward.arn
}

output "data_analyst_role" {
  value = aws_iam_role.data_analyst.arn
} 