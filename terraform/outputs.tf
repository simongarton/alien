output "api_endpoint" {
  value = "${aws_api_gateway_stage.default.invoke_url}/alien"
}

output "api_key_value" {
  value     = aws_api_gateway_api_key.alien_api.value
  sensitive = true
}
