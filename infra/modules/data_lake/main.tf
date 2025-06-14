resource "aws_s3_bucket" "raw_zone" {
  bucket = "${var.project_name}-raw-zone-${var.environment}"
  
  tags = merge(var.tags, {
    Name        = "${var.project_name}-raw-zone"
    Environment = var.environment
    Zone        = "raw"
  })
}

resource "aws_s3_bucket" "curated_zone" {
  bucket = "${var.project_name}-curated-zone-${var.environment}"
  
  tags = merge(var.tags, {
    Name        = "${var.project_name}-curated-zone"
    Environment = var.environment
    Zone        = "curated"
  })
}

# Enable versioning for both buckets
resource "aws_s3_bucket_versioning" "raw_zone" {
  bucket = aws_s3_bucket.raw_zone.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_versioning" "curated_zone" {
  bucket = aws_s3_bucket.curated_zone.id
  versioning_configuration {
    status = "Enabled"
  }
}

# Enable server-side encryption for both buckets
resource "aws_s3_bucket_server_side_encryption_configuration" "raw_zone" {
  bucket = aws_s3_bucket.raw_zone.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "curated_zone" {
  bucket = aws_s3_bucket.curated_zone.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Block public access for both buckets
resource "aws_s3_bucket_public_access_block" "raw_zone" {
  bucket = aws_s3_bucket.raw_zone.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_public_access_block" "curated_zone" {
  bucket = aws_s3_bucket.curated_zone.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
} 