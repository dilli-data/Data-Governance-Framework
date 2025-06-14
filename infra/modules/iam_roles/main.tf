# Data Steward Role
resource "aws_iam_role" "data_steward" {
  name = "${var.project_name}-data-steward-${var.environment}"

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
    Name        = "${var.project_name}-data-steward"
    Environment = var.environment
  })
}

# Data Analyst Role
resource "aws_iam_role" "data_analyst" {
  name = "${var.project_name}-data-analyst-${var.environment}"

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
    Name        = "${var.project_name}-data-analyst"
    Environment = var.environment
  })
}

# Data Engineer Role
resource "aws_iam_role" "data_engineer" {
  name = "${var.project_name}-data-engineer-${var.environment}"

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
    Name        = "${var.project_name}-data-engineer"
    Environment = var.environment
  })
}

# Data Steward Policy
resource "aws_iam_role_policy" "data_steward" {
  name = "${var.project_name}-data-steward-policy-${var.environment}"
  role = aws_iam_role.data_steward.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:*",
          "glue:*",
          "lakeformation:*"
        ]
        Resource = "*"
      }
    ]
  })
}

# Data Analyst Policy
resource "aws_iam_role_policy" "data_analyst" {
  name = "${var.project_name}-data-analyst-policy-${var.environment}"
  role = aws_iam_role.data_analyst.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:ListBucket",
          "glue:GetTable",
          "glue:GetTables",
          "glue:GetDatabase",
          "glue:GetDatabases",
          "lakeformation:GetDataAccess"
        ]
        Resource = [
          "arn:aws:s3:::${var.data_lake_bucket}",
          "arn:aws:s3:::${var.data_lake_bucket}/*",
          "arn:aws:glue:*:*:catalog",
          "arn:aws:glue:*:*:database/*",
          "arn:aws:glue:*:*:table/*"
        ]
      }
    ]
  })
}

# Data Engineer Policy
resource "aws_iam_role_policy" "data_engineer" {
  name = "${var.project_name}-data-engineer-policy-${var.environment}"
  role = aws_iam_role.data_engineer.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:*",
          "glue:*",
          "lakeformation:GetDataAccess",
          "lakeformation:GrantPermissions"
        ]
        Resource = "*"
      }
    ]
  })
} 