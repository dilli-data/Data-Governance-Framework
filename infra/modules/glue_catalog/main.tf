# Glue Database
resource "aws_glue_catalog_database" "data_governance" {
  name = var.database_name
  
  tags = merge(var.tags, {
    Name        = var.database_name
    Environment = var.environment
  })
}

# Glue Crawler IAM Role
resource "aws_iam_role" "glue_crawler" {
  name = "${var.project_name}-glue-crawler-${var.environment}"

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

  tags = merge(var.tags, {
    Name        = "${var.project_name}-glue-crawler"
    Environment = var.environment
  })
}

# Glue Crawler IAM Policy
resource "aws_iam_role_policy" "glue_crawler" {
  name = "${var.project_name}-glue-crawler-policy-${var.environment}"
  role = aws_iam_role.glue_crawler.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          "arn:aws:s3:::${var.s3_bucket_name}",
          "arn:aws:s3:::${var.s3_bucket_name}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "glue:*",
          "lakeformation:GetDataAccess"
        ]
        Resource = "*"
      }
    ]
  })
}

# Glue Crawler
resource "aws_glue_crawler" "data_governance" {
  name          = "${var.project_name}-${var.crawler_name}-crawler-${var.environment}"
  database_name = aws_glue_catalog_database.data_governance.name
  role          = aws_iam_role.glue_crawler.arn

  s3_target {
    path = "s3://${var.s3_bucket_name}/raw/"
  }

  schedule = "cron(0 0 * * ? *)"  # Run daily at midnight

  tags = merge(var.tags, {
    Name        = "${var.project_name}-${var.crawler_name}-crawler"
    Environment = var.environment
  })
} 