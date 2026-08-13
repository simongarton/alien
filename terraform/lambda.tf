resource "aws_cloudwatch_log_group" "alien_api" {
  name              = "/aws/lambda/alien-generator"
  retention_in_days = 14
}

resource "aws_lambda_function" "alien_api" {
  function_name = "alien-generator"
  role          = aws_iam_role.lambda_exec.arn
  handler       = "handler.lambda_handler"
  runtime       = var.lambda_runtime
  architectures = ["x86_64"]
  timeout       = 10
  memory_size   = 256

  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256

  depends_on = [aws_cloudwatch_log_group.alien_api]
}
