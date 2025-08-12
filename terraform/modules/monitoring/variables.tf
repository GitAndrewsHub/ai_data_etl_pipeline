variable "log_group_name" {
  description = "Name of the CloudWatch Logs group for batch jobs"
  type        = string
}

variable "audit_bucket" {
  description = "Name of the S3 bucket for CloudTrail and access logs"
  type        = string
}

variable "config_role_arn" {
  description = "ARN of the IAM role for AWS Config recorder"
  type        = string
}

variable "retention_days" {
  description = "Number of days to retain logs in CloudWatch"
  type        = number
  default     = 30
}
