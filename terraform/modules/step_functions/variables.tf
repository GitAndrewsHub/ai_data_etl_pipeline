variable "state_machine_name" { type = string }
variable "role_arn"           { type = string }
variable "job_queue_arn"      { type = string }
variable "job_definition_arns"{ type = map(string) }
