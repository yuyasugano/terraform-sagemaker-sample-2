provider "aws" {
  region = var.aws_region
  profile = var.aws_profile
  version = "2.23.0"
}

module "iam" {
  source = "../modules/iam"
  aws_region = var.aws_region

  # iam for sagemaker notebook
  iam_name = var.iam_name
  identifier = var.identifier

  # iam for lambda function
  iam_name_lambda = var.iam_name_lambda
  identifier_lambda = var.identifier_lambda
}

module "s3" {
  source = "../modules/s3"

  endpoint_name = var.endpoint_name
  notebook_bucket_name = var.notebook_bucket_name
  sagemaker_bucket_name = var.sagemaker_bucket_name

  role_arn = "${module.iam.iam_role_arn_lambda}"
}

module "sagemaker" {
  source = "../modules/sagemaker"

  sagemaker_notebook_name = var.sagemaker_notebook_name
  aws_iam_role = "${module.iam.iam_role_arn}"
  bucket_name = "${module.s3.bucket_name}"
}

module "cloudwatch" {
  source = "../modules/cloudwatch"

  event_name = var.event_name
  lambda_function_arn = "${module.lambda.lambda_function_arn}"
}

module "lambda" {
  source = "../modules/lambda"

  event_arn = "${module.cloudwatch.event_arn}"
  bucket_arn = "${module.s3.s3_bucket_arn}"
  lambda_role = "${module.iam.iam_role_arn_lambda}"
  lambda_object = "${module.s3.lambda_object}"
  bucket_name = "${module.s3.s3_bucket_name}"
}

