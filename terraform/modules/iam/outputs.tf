output "batch_execution_role_arn"   { value = aws_iam_role.batch_execution_role.arn }
output "batch_job_role_arn"         { value = aws_iam_role.batch_job_role.arn }
output "step_functions_role_arn"    { value = aws_iam_role.step_functions_role.arn }
output "config_recorder_role_arn"   { value = aws_iam_role.config_recorder_role.arn }
