resource "null_resource" "lambda_build" {
  triggers = {
    handler_hash      = filesha256("${path.module}/../lambda/handler.py")
    requirements_hash = filesha256("${path.module}/../lambda/requirements.txt")
    generator_hash    = filesha256("${path.module}/../src/alien_generator.py")
    painter_hash      = filesha256("${path.module}/../src/image_painter.py")
    text_hash         = filesha256("${path.module}/../src/alien_json_to_text.py")
    build_script_hash = filesha256("${path.module}/build_lambda.sh")
  }

  provisioner "local-exec" {
    command = "${path.module}/build_lambda.sh"
  }
}

data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/.build/lambda"
  output_path = "${path.module}/.build/lambda.zip"

  depends_on = [null_resource.lambda_build]
}
