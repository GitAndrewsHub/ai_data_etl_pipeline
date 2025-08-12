variable "region"             { type = string }
variable "vpc_cidr"           { type = string }
variable "azs"                { type = list(string) }
variable "public_subnets"     { type = list(string) }
variable "private_subnets"    { type = list(string) }
variable "security_group_id"  { type = string }
variable "bucket_name"        { type = string }
variable "audit_bucket_name"  { type = string }
variable "ecr_repository_name"{ type = string }
variable "state_machine_name" { type = string }
variable "endpoint_sg_id" {
  description = "Security Group for VPC Interface Endpoints"
  type        = string
}
variable "name" {
  type        = string
  description = "Name for the VPC"
}
variable "cidr" {
  type        = string
  description = "CIDR block for the VPC"
}
