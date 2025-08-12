output "bucket_id"   { value = aws_s3_bucket.pipeline.id }
output "bucket_arn"  { value = aws_s3_bucket.pipeline.arn }
output "kms_key_arn" { value = aws_kms_key.s3.arn }
