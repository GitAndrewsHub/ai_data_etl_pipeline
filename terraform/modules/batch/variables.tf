variable "subnet_ids" {
  description = "List of private subnet IDs for the compute environment"
  type        = list(string)
}

variable "security_group_ids" {
  description = "Security groups for the Batch compute resources"
  type        = list(string)
}

variable "service_role_arn" {
  description = "ARN of the IAM role Batch uses to manage compute (batch:serviceRole)"
  type        = string
}

variable "execution_role_arn" {
  description = "ARN of the ECS Task Execution Role (executionRoleArn in job definitions)"
  type        = string
}

variable "job_role_arn" {
  description = "ARN of the IAM role your container uses to access S3 / logs"
  type        = string
}

variable "ecr_image_uri" {
  description = "ECR image URI for all job definitions"
  type        = string
}

variable "region" {
  description = "AWS region"
  type        = string
}
