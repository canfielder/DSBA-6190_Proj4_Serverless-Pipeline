resource "aws_s3_bucket" "project_4_bucket" {
  bucket = "dsba-6190-project-4-terraform"
}

# Zip Each Lambda File
data "archive_file" "project_4_archive_producer" {
  type        = "zip"
  source_file = "${path.module}/../scripts/lambda_producer.py"
  output_path = "${path.module}/../scripts/zip/lambda_producer.zip"
}

data "archive_file" "project_4_archive_consumer" {
  type        = "zip"
  source_file = "${path.module}/../scripts/lambda_consumer.py"
  output_path = "${path.module}/../scripts/zip/lambda_consumer.zip"
}


# Upload Each Lambda Zip File
resource "aws_s3_bucket_object" "s3_project_4_upload" {
  for_each = fileset("${path.module}/../scripts/zip/", "*")

  bucket = "${aws_s3_bucket.project_4_bucket.id}"
  key    =  "lambda_files/${each.value}"
  source = "${path.module}/../scripts/zip/${each.value}"
}
