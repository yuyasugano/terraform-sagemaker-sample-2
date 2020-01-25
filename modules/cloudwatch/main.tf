resource "aws_cloudwatch_event_rule" "default" {
  name = var.event_name
  schedule_expression = "rate(1 minute)"
  is_enabled = false
}

resource "aws_cloudwatch_event_target" "default" {
  target_id = "TargetFunctionV1"
  rule = aws_cloudwatch_event_rule.default.name
  arn = var.lambda_function_arn
}
  
