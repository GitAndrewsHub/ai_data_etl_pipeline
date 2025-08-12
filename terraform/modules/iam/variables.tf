variable "batch_execution_role_name" {
  type        = string
  description = "Name of the Batch execution IAM role"
}

variable "batch_job_role_name" {
  type        = string
  description = "Name of the Batch in-container IAM role"
}

variable "step_functions_role_name" {
  type        = string
  description = "Name of the Step Functions IAM role"
}

variable "config_recorder_role_name" {
  type        = string
  description = "Name of the AWS Config recorder role"
}

variable "bucket_arn" {
  type        = string
  description = "ARN of the pipeline S3 bucket (for IAM policies)"
}

variable "batch_job_queue_arn" {
  type        = string
  description = "ARN of the Batch job queue (for Step Functions policy)"
}
