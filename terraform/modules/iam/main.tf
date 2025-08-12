data "aws_iam_policy_document" "batch_execution_assume" {
  statement {
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = [
        "ecs-tasks.amazonaws.com",
        "batch.amazonaws.com"
      ]
    }
    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "batch_execution_role" {
  name               = var.batch_execution_role_name
  assume_role_policy = data.aws_iam_policy_document.batch_execution_assume.json
}

# S3 access for Batch Execution
data "aws_iam_policy_document" "batch_s3_access" {
  statement {
    effect    = "Allow"
    actions   = [
      "s3:GetObject",
      "s3:PutObject",
      "s3:ListBucket"
    ]
    resources = [
      var.bucket_arn,
      "${var.bucket_arn}/*"
    ]
  }
}

resource "aws_iam_policy" "batch_s3_policy" {
  name   = "${var.batch_execution_role_name}-s3-access"
  policy = data.aws_iam_policy_document.batch_s3_access.json
}

resource "aws_iam_role_policy_attachment" "batch_s3_attach" {
  role       = aws_iam_role.batch_execution_role.name
  policy_arn = aws_iam_policy.batch_s3_policy.arn
}

# Batch Job Role
data "aws_iam_policy_document" "batch_job_assume" {
  statement {
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "batch_job_role" {
  name               = var.batch_job_role_name
  assume_role_policy = data.aws_iam_policy_document.batch_job_assume.json
}

# Logs + S3 for in-container processing
data "aws_iam_policy_document" "batch_job_policy_doc" {
  statement {
    effect    = "Allow"
    actions   = [
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources = ["arn:aws:logs:*:*:log-group:/aws/batch/job*"]
  }
  statement {
    effect    = "Allow"
    actions   = [
      "s3:GetObject",
      "s3:PutObject"
    ]
    resources = ["${var.bucket_arn}/*"]
  }
}

resource "aws_iam_policy" "batch_job_policy" {
  name   = "${var.batch_job_role_name}-policy"
  policy = data.aws_iam_policy_document.batch_job_policy_doc.json
}

resource "aws_iam_role_policy_attachment" "batch_job_attach" {
  role       = aws_iam_role.batch_job_role.name
  policy_arn = aws_iam_policy.batch_job_policy.arn
}

# Step Functions Role 
data "aws_iam_policy_document" "sfn_assume" {
  statement {
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["states.amazonaws.com"]
    }
    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "step_functions_role" {
  name               = var.step_functions_role_name
  assume_role_policy = data.aws_iam_policy_document.sfn_assume.json
}

# Permissions to submit and describe Batch jobs
data "aws_iam_policy_document" "sfn_policy_doc" {
  statement {
    effect    = "Allow"
    actions   = [
      "batch:SubmitJob",
      "batch:DescribeJobs"
    ]
    resources = [var.batch_job_queue_arn]
  }
  statement {
    effect    = "Allow"
    actions   = ["iam:PassRole"]
    resources = [
      aws_iam_role.batch_execution_role.arn,
      aws_iam_role.batch_job_role.arn
    ]
  }
}

resource "aws_iam_policy" "sfn_policy" {
  name   = "${var.step_functions_role_name}-policy"
  policy = data.aws_iam_policy_document.sfn_policy_doc.json
}

resource "aws_iam_role_policy_attachment" "sfn_attach" {
  role       = aws_iam_role.step_functions_role.name
  policy_arn = aws_iam_policy.sfn_policy.arn
}

# AWS Config Recorder Role 
data "aws_iam_policy_document" "config_recorder_assume" {
  statement {
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["config.amazonaws.com"]
    }
    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "config_recorder_role" {
  name               = var.config_recorder_role_name
  assume_role_policy = data.aws_iam_policy_document.config_recorder_assume.json
}

resource "aws_iam_policy" "config_recorder_policy" {
  name   = "${var.config_recorder_role_name}-policy"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect   = "Allow",
        Action   = [
          "config:Put*",
          "config:Delete*",
          "config:Get*",
          "config:Describe*"
        ],
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "config_recorder_attach" {
  role       = aws_iam_role.config_recorder_role.name
  policy_arn = aws_iam_policy.config_recorder_policy.arn
}