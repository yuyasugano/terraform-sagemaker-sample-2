output "bucket_name" {
  value = aws_s3_bucket.notebook.id
}

output "s3_bucket_name" {
  value = aws_s3_bucket.sagemaker.id
}

output "bucket_arn" {
  value = aws_s3_bucket.notebook.arn
}

output "s3_bucket_arn" {
  value = aws_s3_bucket.sagemaker.arn
}

output "lambda_object" {
  value = aws_s3_bucket_object.lambda
}
