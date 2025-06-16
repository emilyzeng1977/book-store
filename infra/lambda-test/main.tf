terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  required_version = ">= 1.3.0"
}

provider "aws" {
  region = "ap-southeast-2"
}

module "python_lambda" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "~> 6.0"

  function_name = "my-python-lambda"
  handler       = "main.lambda_handler"
  runtime       = "python3.12"

  # 👇 指向 src 目录
  source_path = "${path.module}/src"

  build_in_docker = true

  # ✅ 推荐设置 memory 和 timeout
  memory_size = 256
  timeout     = 10

  # ✅ 添加环境变量
  environment_variables = {
    USER_POOL_ID  = "ap-southeast-2_09CeFqveZ"
    APP_CLIENT_ID = "1ktmj89m2g93t3pbb2u24mbl6s"
  }
}
