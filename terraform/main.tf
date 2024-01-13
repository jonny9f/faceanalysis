provider "aws" {
  region = "eu-west-2"  
}



resource "aws_api_gateway_rest_api" "faceanalysis" {
    name = "faceanalysis"  // The name should match the API Gateway's name in AWS
    // other configurations if necessary
}

resource "aws_iam_role" "test_service_role" {
  // The name is necessary, but other properties can be added later
  name = "test-role-7plo54o1"

   assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Effect = "Allow",
        Principal = {
          Service = "lambda.amazonaws.com"
        },
      },
    ],
  })
}


resource "aws_lambda_function" "faceanalysis" {
    function_name = "test"
    role = aws_iam_role.test_service_role.arn
    image_uri = "302605622298.dkr.ecr.eu-west-2.amazonaws.com/faceanalysis@sha256:d355abcf7234ef1e463ec6668c83dafeedaec31dafebcc654ab593b0a5a28cae"
          
}
