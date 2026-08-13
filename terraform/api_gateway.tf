resource "aws_api_gateway_rest_api" "alien_api" {
  name               = "alien-generator-api"
  binary_media_types = ["image/png"]
}

resource "aws_api_gateway_resource" "alien" {
  rest_api_id = aws_api_gateway_rest_api.alien_api.id
  parent_id   = aws_api_gateway_rest_api.alien_api.root_resource_id
  path_part   = "alien"
}

resource "aws_api_gateway_method" "get_alien" {
  rest_api_id      = aws_api_gateway_rest_api.alien_api.id
  resource_id      = aws_api_gateway_resource.alien.id
  http_method      = "GET"
  authorization    = "NONE"
  api_key_required = true
}

resource "aws_api_gateway_integration" "lambda" {
  rest_api_id             = aws_api_gateway_rest_api.alien_api.id
  resource_id             = aws_api_gateway_resource.alien.id
  http_method             = aws_api_gateway_method.get_alien.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.alien_api.invoke_arn
}

resource "aws_api_gateway_deployment" "alien_api" {
  rest_api_id = aws_api_gateway_rest_api.alien_api.id

  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_resource.alien.id,
      aws_api_gateway_method.get_alien.id,
      aws_api_gateway_integration.lambda.id,
    ]))
  }

  lifecycle {
    create_before_destroy = true
  }

  depends_on = [aws_api_gateway_integration.lambda]
}

resource "aws_api_gateway_stage" "default" {
  rest_api_id   = aws_api_gateway_rest_api.alien_api.id
  deployment_id = aws_api_gateway_deployment.alien_api.id
  stage_name    = "default"
}

resource "aws_lambda_permission" "apigw" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.alien_api.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.alien_api.execution_arn}/*/*"
}

resource "aws_api_gateway_api_key" "alien_api" {
  name = "alien-generator-key"
}

resource "aws_api_gateway_usage_plan" "alien_api" {
  name = "alien-generator-usage-plan"

  api_stages {
    api_id = aws_api_gateway_rest_api.alien_api.id
    stage  = aws_api_gateway_stage.default.stage_name
  }

  throttle_settings {
    rate_limit  = 2
    burst_limit = 5
  }

  quota_settings {
    limit  = 100
    period = "DAY"
  }
}

resource "aws_api_gateway_usage_plan_key" "alien_api" {
  key_id        = aws_api_gateway_api_key.alien_api.id
  key_type      = "API_KEY"
  usage_plan_id = aws_api_gateway_usage_plan.alien_api.id
}
