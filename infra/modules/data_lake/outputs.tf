output "raw_zone_bucket" {
  description = "Name of the raw zone S3 bucket"
  value       = aws_s3_bucket.raw_zone.bucket
}

output "curated_zone_bucket" {
  description = "Name of the curated zone S3 bucket"
  value       = aws_s3_bucket.curated_zone.bucket
}

output "raw_zone_arn" {
  description = "ARN of the raw zone S3 bucket"
  value       = aws_s3_bucket.raw_zone.arn
}

output "curated_zone_arn" {
  description = "ARN of the curated zone S3 bucket"
  value       = aws_s3_bucket.curated_zone.arn
} 