provider "aws" {
  region = var.region
}

 module "network" {
   source  = "./modules/network"
   name            = var.name
   cidr            = var.cidr
   azs             = var.azs
   public_subnets  = var.public_subnets
   private_subnets = var.private_subnets
   region          = var.region
   endpoint_sg_id  = var.endpoint_sg_id
 }


module "storage" {
  source            = "./modules/storage"
  bucket_name       = var.bucket_name
  audit_bucket_name = var.audit_bucket_name
}

module "ecr" {
  source           = "./modules/ecr"
  repository_name  = var.ecr_repository_name
}

module "iam" {
  source                      = "./modules/iam"
  batch_execution_role_name   = "batch_execution_role"
  batch_job_role_name         = "batch_job_role"
  step_functions_role_name    = "step-functions-batch-role"
  config_recorder_role_name   = "pipeline-config-recorder"
  bucket_arn                  = module.storage.bucket_arn
  batch_job_queue_arn         = module.batch.batch_job_queue_arn
}

module "batch" {
  source               = "./modules/batch"
  subnet_ids           = module.network.private_subnets
  security_group_ids   = [var.security_group_id]
  service_role_arn     = module.iam.batch_execution_role_arn
  execution_role_arn   = module.iam.batch_execution_role_arn
  job_role_arn         = module.iam.batch_job_role_arn
  ecr_image_uri        = module.ecr.repository_url
  region               = var.region
}

module "step_functions" {
  source               = "./modules/step_functions"
  state_machine_name   = var.state_machine_name
  role_arn             = module.iam.step_functions_role_arn
  job_queue_arn        = module.batch.batch_job_queue_arn
  job_definition_arns  = {
    text_ingest      = module.batch.text_ingest_job_definition_arn
    text_filter      = module.batch.text_filter_job_definition_arn
    toxicity_filter  = module.batch.toxicity_filter_job_definition_arn
    deduplication    = module.batch.deduplication_job_definition_arn
    global_dedupe    = module.batch.global_deduplication_job_definition_arn
    text_normalize   = module.batch.text_normalize_job_definition_arn
    tokenize         = module.batch.tokenize_job_definition_arn
  }
}

module "monitoring" {
  source          = "./modules/monitoring"
  log_group_name  = "/aws/batch/job"
  audit_bucket    = var.audit_bucket_name
  config_role_arn = module.iam.config_recorder_role_arn
}

output "state_machine_arn" {
  value = module.step_functions.state_machine_arn
}
