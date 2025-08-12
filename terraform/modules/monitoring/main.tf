resource "aws_cloudwatch_log_group" "batch" {
  name              = var.log_group_name
  retention_in_days = var.retention_days
}

resource "aws_cloudtrail" "main" {
  name                        = "pipeline-trail"
  s3_bucket_name             = var.audit_bucket
  is_multi_region_trail      = true
  enable_log_file_validation = true
}

resource "aws_config_configuration_recorder" "recorder" {
  name     = "pipeline-config"
  role_arn = var.config_role_arn

  recording_group { all_supported = true }
}

resource "aws_config_delivery_channel" "channel" {
  name           = "pipeline-delivery"
  s3_bucket_name = var.audit_bucket
}
