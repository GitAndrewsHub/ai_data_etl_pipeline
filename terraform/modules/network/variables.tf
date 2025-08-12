variable "name" {
  type = string
}

variable "cidr" {
  type = string
}

variable "azs" {
  type = list(string)
}

variable "public_subnets" {
  type = list(string)
}

variable "private_subnets" {
  type = list(string)
}

variable "region" {
  type        = string
  description = "AWS region (for VPC endpoints)"
}

variable "endpoint_sg_id" {
  type        = string
  description = "Security Group for interface VPC endpoints (e.g. CloudWatch Logs)"
}
