locals {
  definition = templatefile("${path.module}/definition.asl.json", {
    job_queue_arn       = var.job_queue_arn
    job_definition_arns = var.job_definition_arns
  })
}

resource "aws_sfn_state_machine" "pipeline_sm" {
  name       = var.state_machine_name
  role_arn   = var.role_arn
  definition = local.definition
}
