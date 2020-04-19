resource "aws_lambda_function" "lambda_producer" {
  handler       = "lambda_producer.lambda_handler"
  function_name = "proj_4_lambda_producer_terraform"
  depends_on = ["aws_iam_role_policy_attachment.lambda_logs", "aws_cloudwatch_log_group.proj_4_terraform"]
  role          = "${aws_iam_role.iam_for_lambda.arn}"
  s3_bucket     = "${aws_s3_bucket.project_4_bucket.id}"
  s3_key        = "lambda_files/lambda_producer.zip"




  # The filebase64sha256() function is available in Terraform 0.11.12 and later
  # For Terraform 0.11.11 and earlier, use the base64sha256() function and the file() function:
  # source_code_hash = "${base64sha256(file("lambda_function_payload.zip"))}"
  source_code_hash = "${filebase64sha256(data.archive_file.project_4_archive_producer.output_path)}"

  runtime = "python3.6"

}

resource "aws_lambda_function" "lambda_consumer" {
  handler       = "lambda_consumer.lambda_handler"
  function_name = "proj_4_lambda_consumer_terraform"
  role          = "${aws_iam_role.iam_for_lambda.arn}"
  s3_bucket     = "${aws_s3_bucket.project_4_bucket.id}"
  s3_key        = "lambda_files/lambda_consumer.zip"

  # The filebase64sha256() function is available in Terraform 0.11.12 and later
  # For Terraform 0.11.11 and earlier, use the base64sha256() function and the file() function:
  # source_code_hash = "${base64sha256(file("lambda_function_payload.zip"))}"
  source_code_hash = "${filebase64sha256(data.archive_file.project_4_archive_consumer.output_path)}"

  runtime = "python3.6"

}