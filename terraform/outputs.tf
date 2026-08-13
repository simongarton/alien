output "api_endpoint" {
  value = "${aws_apigatewayv2_api.alien_api.api_endpoint}/alien"
}
