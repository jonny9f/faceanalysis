
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}

variable "region" {
  description = "The AWS region"
  default     = "eu-west-1"
}

provider "aws" {
  region = var.region
}

variable "env_name" {
  description = "Environment name"
  default    = "dev"
}

data "aws_ecr_repository" "faceanalysis" {
  name = "faceanalysis"
}

resource "aws_lambda_function" "faceanalysis" {
  function_name = "faceanalysis-${var.env_name}"
  timeout       = 60 # seconds
  memory_size   = 2048 # 2 GB in MB
  image_uri     = "${data.aws_ecr_repository.faceanalysis.repository_url}:${var.env_name}"
  package_type  = "Image"

  role = aws_iam_role.faceanalysis_role.arn

  environment {
    variables = {
      ENVIRONMENT = var.env_name
    }
  }
}

resource "aws_iam_role" "faceanalysis_role" {
  name = "faceanalysis-role-${var.env_name}"

  assume_role_policy = jsonencode({
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      },
    ]
  })
}

resource "aws_api_gateway_rest_api" "faceanalysis" {
    name = "faceanalysis"  // The name should match the API Gateway's name in AWS

    endpoint_configuration {
    types = ["REGIONAL"]
     }
    
}

resource "aws_lambda_permission" "allow_apigateway" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.faceanalysis.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.faceanalysis.execution_arn}/*/*"
}


resource "aws_api_gateway_resource" "proxy" {
  rest_api_id = aws_api_gateway_rest_api.faceanalysis.id
  parent_id   = aws_api_gateway_rest_api.faceanalysis.root_resource_id
  path_part   = "{proxy+}" // Proxy resource

}

resource "aws_api_gateway_method" "proxy_method" {
  rest_api_id   = aws_api_gateway_rest_api.faceanalysis.id
  resource_id   = aws_api_gateway_resource.proxy.id
  http_method   = "ANY" // Or specify the method (GET, POST, etc.)
  authorization = "NONE"
  api_key_required = true
}

resource "aws_api_gateway_integration" "lambda_integration" {
  rest_api_id = aws_api_gateway_rest_api.faceanalysis.id
  resource_id = aws_api_gateway_resource.proxy.id
  http_method = aws_api_gateway_method.proxy_method.http_method
  integration_http_method = "POST"
  type        = "AWS_PROXY"
  uri         = aws_lambda_function.faceanalysis.invoke_arn
}


resource "aws_api_gateway_deployment" "deployment" {
  depends_on = [
    aws_api_gateway_integration.lambda_integration,
  ]
  rest_api_id = aws_api_gateway_rest_api.faceanalysis.id
  stage_name  = "dev"

  triggers = {
    redeployment = sha1(jsonencode(aws_api_gateway_rest_api.faceanalysis.body))
  }
}

resource "aws_api_gateway_api_key" "dev" {
  name        = "api-key-dev"
  description = "API Key"
  enabled     = true
}

resource "aws_api_gateway_usage_plan" "dev" {
  name        = "usgage-plan-dev"
  description = "Usage plan for the example API"

  api_stages {
    api_id = aws_api_gateway_rest_api.faceanalysis.id
    stage  = aws_api_gateway_deployment.deployment.stage_name
  }

  // Set throttle and quota limits as needed
  throttle_settings {
    burst_limit = 5
    rate_limit  = 10
  }
}

resource "aws_api_gateway_usage_plan_key" "dev" {
  key_id        = aws_api_gateway_api_key.dev.id
  key_type      = "API_KEY"
  usage_plan_id = aws_api_gateway_usage_plan.dev.id
}

output "api_gateway_url" {
  value = "https://${aws_api_gateway_rest_api.faceanalysis.id}.execute-api.${var.region}.amazonaws.com/${aws_api_gateway_deployment.deployment.stage_name}"
  description = "The URL of the deployed API Gateway"
}

