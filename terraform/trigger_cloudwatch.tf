# Establish Cloudwatch Event Trigger - 1 Minute
resource "aws_cloudwatch_event_rule" "lambda_producer_trigger"{
    name                = "lambda_producer_trigger_terraform"
    description         = "Calls 1x per Minute"
    schedule_expression = "rate(1 minute)"
    is_enabled          = true
}

# Attached Trigger to Producer Lambda
resource "aws_cloudwatch_event_target" "target_producer" {
  target_id = "lambda_producer"
  rule      = "${aws_cloudwatch_event_rule.lambda_producer_trigger.name}"
  arn       = "${aws_lambda_function.lambda_producer.arn}"
}

resource "aws_lambda_permission" "producer_lambda" {
  action        = "lambda:InvokeFunction"
  function_name = "${aws_lambda_function.lambda_producer.function_name}"
  principal     = "events.amazonaws.com"
  source_arn    = "${aws_cloudwatch_event_rule.lambda_producer_trigger.arn}"
}