resource "aws_ecr_repository" "pipeline" {
  name = var.repository_name

  image_scanning_configuration { scan_on_push = true }
  encryption_configuration     { encryption_type = "KMS" }
}
