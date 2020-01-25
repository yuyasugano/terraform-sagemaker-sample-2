resource "aws_lambda_function" "default" {
  handler = "lambda_function.lambda_handler"
  function_name = "lambda_function"
  role = var.lambda_role
  s3_bucket = var.bucket_name
  s3_key = "lambda_function.zip" 

  runtime = "python3.7"
  depends_on = [var.lambda_object]
}

resource "aws_lambda_permission" "cloudwatch" {
  action = "lambda:InvokeFunction"
  function_name = aws_lambda_function.default.function_name
  principal = "events.amazonaws.com"
  source_arn = var.event_arn
}

resource "aws_lambda_permission" "s3" {
  action = "lambda:InvokeFunction"
  function_name = aws_lambda_function.default.function_name
  principal = "s3.amazonaws.com"
  source_arn = var.bucket_arn
}

