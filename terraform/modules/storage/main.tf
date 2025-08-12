resource "aws_kms_key" "s3" {
  description             = "KMS key for S3 encryption"
  deletion_window_in_days = 30
}

 resource "aws_s3_bucket" "pipeline" {
   bucket = var.bucket_name

   server_side_encryption_configuration {
     rule {
       apply_server_side_encryption_by_default {
         sse_algorithm     = "aws:kms"
         kms_master_key_id = aws_kms_key.s3.arn
       }
     }
   }
 }

resource "aws_s3_bucket_logging" "pipeline" {
  bucket = aws_s3_bucket.pipeline.id

  target_bucket = var.audit_bucket_name
  target_prefix = "s3-access-logs/"
}

resource "aws_s3_bucket_versioning" "pipeline" {
  bucket = aws_s3_bucket.pipeline.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_public_access_block" "pipeline" {
  bucket                  = aws_s3_bucket.pipeline.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
