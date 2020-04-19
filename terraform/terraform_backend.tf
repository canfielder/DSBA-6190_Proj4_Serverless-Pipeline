terraform {
  backend "s3" {
    bucket = "dsba-6190-project4-serverless-data-engineering-pipeline"
    key    = "terraform.tfstate"
    region = "us-east-1"
  }
}