# 使用轻量 Alpine 作为基础镜像
FROM alpine:3.18

# 安装 curl、unzip、bash、python3 和 pip
RUN apk add --no-cache \
    curl \
    unzip \
    bash \
    python3 \
    py3-pip

# 安装 Terraform
ENV TERRAFORM_VERSION=1.7.5
RUN curl -sLo terraform.zip https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_linux_amd64.zip \
    && unzip terraform.zip \
    && mv terraform /usr/local/bin/ \
    && rm terraform.zip

# 安装 Terragrunt
ENV TERRAGRUNT_VERSION=0.78.1
RUN curl -sLo terragrunt https://github.com/gruntwork-io/terragrunt/releases/download/v${TERRAGRUNT_VERSION}/terragrunt_linux_amd64 \
    && chmod +x terragrunt \
    && mv terragrunt /usr/local/bin/

# 设置默认 Python 链接（可选）
RUN ln -sf python3 /usr/bin/python

# 默认入口（可选）
ENTRYPOINT [ "terragrunt" ]
