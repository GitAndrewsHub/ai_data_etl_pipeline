output "batch_compute_environment_arn" {
  value = aws_batch_compute_environment.pipeline_env.arn
}

output "batch_job_queue_arn" {
  value = aws_batch_job_queue.pipeline_queue.arn
}

output "text_ingest_job_definition_arn" {
  value = aws_batch_job_definition.text_ingest.arn
}

output "text_filter_job_definition_arn" {
  value = aws_batch_job_definition.text_filter.arn
}

output "toxicity_filter_job_definition_arn" {
  value = aws_batch_job_definition.toxicity_filter.arn
}

output "deduplication_job_definition_arn" {
  value = aws_batch_job_definition.deduplication.arn
}

output "global_deduplication_job_definition_arn" {
  value = aws_batch_job_definition.global_deduplication.arn
}

output "text_normalize_job_definition_arn" {
  value = aws_batch_job_definition.text_normalize.arn
}

output "tokenize_job_definition_arn" {
  value = aws_batch_job_definition.tokenize.arn
}