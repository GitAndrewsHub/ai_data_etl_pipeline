# Batch compute environment
resource "aws_batch_compute_environment" "pipeline_env" {
  name         = "pipeline-env"
  type         = "MANAGED"
  service_role = var.service_role_arn

  compute_resources {
    type               = "FARGATE"
    max_vcpus          = 4
    subnets            = var.subnet_ids
    security_group_ids = var.security_group_ids
  }
}

# Batch job queue
resource "aws_batch_job_queue" "pipeline_queue" {
  name     = "pipeline-queue"
  state    = "ENABLED"
  priority = 1

  compute_environment_order {
    order               = 1
    compute_environment = aws_batch_compute_environment.pipeline_env.arn
  }
}

# Job definition: Text Ingest 
resource "aws_batch_job_definition" "text_ingest" {
  name                  = "text-ingest-job"
  type                  = "container"
  platform_capabilities = ["FARGATE"]

  container_properties = jsonencode({
    image              = var.ecr_image_uri,
    executionRoleArn   = var.execution_role_arn,
    jobRoleArn         = var.job_role_arn,
    resourceRequirements = [
      { type = "VCPU",    value = "1" },
      { type = "MEMORY",  value = "2048" }
    ],
    command = [],                          # overridden by Step Functions
    environment = [
      { name = "AWS_REGION",          value = var.region }
    ],
    logConfiguration = {
      logDriver = "awslogs",
      options = {
        awslogs-group         = "/aws/batch/job",
        awslogs-region        = var.region,
        awslogs-stream-prefix = "batch"
      }
    },
    networkConfiguration = { assignPublicIp = "DISABLED" }
  })
}

# Job definition: Text Filter
resource "aws_batch_job_definition" "text_filter" {
  name                  = "text-filter-job"
  type                  = "container"
  platform_capabilities = ["FARGATE"]

  container_properties = jsonencode({
    image            = var.ecr_image_uri,
    executionRoleArn = var.execution_role_arn,
    jobRoleArn       = var.job_role_arn,
    resourceRequirements = [
      { type = "VCPU",   value = "1" },
      { type = "MEMORY", value = "2048" }
    ],
    command = ["python","filtering/text_filter.py"],
    logConfiguration = {
      logDriver = "awslogs",
      options = {
        awslogs-group         = "/aws/batch/job",
        awslogs-region        = var.region,
        awslogs-stream-prefix = "batch"
      }
    },
    networkConfiguration = { assignPublicIp = "DISABLED" }
  })
}

# Job definition: Toxicity Filter
resource "aws_batch_job_definition" "toxicity_filter" {
  name                  = "toxicity-filter-job"
  type                  = "container"
  platform_capabilities = ["FARGATE"]

  container_properties = jsonencode({
    image            = var.ecr_image_uri,
    executionRoleArn = var.execution_role_arn,
    jobRoleArn       = var.job_role_arn,
    resourceRequirements = [
      { type = "VCPU",   value = "1" },
      { type = "MEMORY", value = "2048" }
    ],
    command = ["python","filtering/toxicity_filter.py"],
    logConfiguration = {
      logDriver = "awslogs",
      options = {
        awslogs-group         = "/aws/batch/job",
        awslogs-region        = var.region,
        awslogs-stream-prefix = "batch"
      }
    },
    networkConfiguration = { assignPublicIp = "DISABLED" }
  })
}

# Job definition: Deduplication
resource "aws_batch_job_definition" "deduplication" {
  name                  = "deduplication-job"
  type                  = "container"
  platform_capabilities = ["FARGATE"]

  container_properties = jsonencode({
    image            = var.ecr_image_uri,
    executionRoleArn = var.execution_role_arn,
    jobRoleArn       = var.job_role_arn,
    resourceRequirements = [
      { type = "VCPU",   value = "1" },
      { type = "MEMORY", value = "2048" }
    ],
    command = ["python","deduplication/deduplicate.py"],
    logConfiguration = {
      logDriver = "awslogs",
      options = {
        awslogs-group         = "/aws/batch/job",
        awslogs-region        = var.region,
        awslogs-stream-prefix = "batch"
      }
    },
    networkConfiguration = { assignPublicIp = "DISABLED" }
  })
}

# Job definition: Global Deduplication
resource "aws_batch_job_definition" "global_deduplication" {
  name                  = "global-deduplication-job"
  type                  = "container"
  platform_capabilities = ["FARGATE"]

  container_properties = jsonencode({
    image            = var.ecr_image_uri,
    executionRoleArn = var.execution_role_arn,
    jobRoleArn       = var.job_role_arn,
    resourceRequirements = [
      { type = "VCPU",   value = "1" },
      { type = "MEMORY", value = "2048" }
    ],
    command = ["python","deduplication/global_deduplicate.py"],
    logConfiguration = {
      logDriver = "awslogs",
      options = {
        awslogs-group         = "/aws/batch/job",
        awslogs-region        = var.region,
        awslogs-stream-prefix = "batch"
      }
    },
    networkConfiguration = { assignPublicIp = "DISABLED" }
  })
}

# Job definition: Text Normalize
resource "aws_batch_job_definition" "text_normalize" {
  name                  = "text-normalize-job"
  type                  = "container"
  platform_capabilities = ["FARGATE"]

  container_properties = jsonencode({
    image            = var.ecr_image_uri,
    executionRoleArn = var.execution_role_arn,
    jobRoleArn       = var.job_role_arn,
    resourceRequirements = [
      { type = "VCPU",   value = "1" },
      { type = "MEMORY", value = "2048" }
    ],
    command = ["python","normalization/text_normalize.py"],
    logConfiguration = {
      logDriver = "awslogs",
      options = {
        awslogs-group         = "/aws/batch/job",
        awslogs-region        = var.region,
        awslogs-stream-prefix = "batch"
      }
    },
    networkConfiguration = { assignPublicIp = "DISABLED" }
  })
}

# Job definition: Tokenize
resource "aws_batch_job_definition" "tokenize" {
  name                  = "tokenize-job"
  type                  = "container"
  platform_capabilities = ["FARGATE"]

  container_properties = jsonencode({
    image            = var.ecr_image_uri,
    executionRoleArn = var.execution_role_arn,
    jobRoleArn       = var.job_role_arn,
    resourceRequirements = [
      { type = "VCPU",   value = "1" },
      { type = "MEMORY", value = "2048" }
    ],
    command = ["python","tokenization/tokenize_llama.py"],
    logConfiguration = {
      logDriver = "awslogs",
      options = {
        awslogs-group         = "/aws/batch/job",
        awslogs-region        = var.region,
        awslogs-stream-prefix = "batch"
      }
    },
    networkConfiguration = { assignPublicIp = "DISABLED" }
  })
}