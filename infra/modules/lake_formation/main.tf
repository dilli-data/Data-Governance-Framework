# Lake Formation Data Lake Settings
resource "aws_lakeformation_data_lake_settings" "data_governance" {
  admins = [var.data_lake_admin]
  
  create_database_default_permissions {
    principal   = "IAM_ALLOWED_PRINCIPALS"
    permissions = ["ALL"]
  }

  create_table_default_permissions {
    principal   = "IAM_ALLOWED_PRINCIPALS"
    permissions = ["ALL"]
  }
}

# Lake Formation Database Permissions
resource "aws_lakeformation_permissions" "database" {
  principal   = var.data_lake_admin
  permissions = ["ALL"]
  
  resource {
    database {
      name = var.database_name
    }
  }
}

# Lake Formation Table Permissions
resource "aws_lakeformation_permissions" "table" {
  principal   = var.data_lake_admin
  permissions = ["ALL"]
  
  resource {
    table {
      database_name = var.database_name
      name         = "*"
    }
  }
}

# Lake Formation Resource Policy
resource "aws_lakeformation_resource" "data_lake" {
  arn = "arn:aws:lakeformation:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:database/${var.database_name}"
  
  tags = merge(var.tags, {
    Name        = "${var.project_name}-lake-formation"
    Environment = var.environment
  })
}

# Get current region and account ID
data "aws_region" "current" {}
data "aws_caller_identity" "current" {} 