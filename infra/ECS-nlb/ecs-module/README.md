# Terraform AWS ECS Fargate Setup for Book-Store Service

## 介绍

本项目使用 Terraform 配置了 AWS ECS Fargate 环境，部署一个名为 `book-store` 的容器服务。容器镜像为 `zengemily79/book-store:latest`，对外暴露 5000 端口。

主要资源包括：

- ECS Cluster
- ECS Task Definition（Fargate）
- ECS Service，绑定私有子网、安全组及负载均衡器

## 文件说明

| 文件名                  | 内容说明                           |
|-------------------------|----------------------------------|
| `ecs-cluster.tf`        | 定义 ECS 集群                    |
| `ecs-task-definition.tf`| 定义 Fargate 任务及容器配置      |
| `ecs-service.tf`        | 定义 ECS 服务及网络配置，关联负载均衡器 |

## 变量说明

- `var.project_name`：项目名称，用于命名集群和任务。
- `module.network.private_subnet_id`：私有子网 ID，用于 ECS Service 网络配置。
- `aws_security_group.ecs_service_sg.id`：服务的安全组 ID。
- `aws_lb_target_group.ecs_tg.arn`：负载均衡目标组 ARN。
- `aws_lb_listener.nlb_listener`：负载均衡监听器。

请确保以上资源和变量在你的 Terraform 项目中已定义。

## 使用步骤

1. 配置并初始化 Terraform：

   ```bash
   terraform init
   ```

2. 预览执行计划：

   ```bash
   terraform plan -var="project_name=your-project-name"
   ```

3. 执行应用：

   ```bash
   terraform apply -var="project_name=your-project-name"
   ```

4. 部署成功后，负载均衡器将会路由流量到你的 `book-store` 容器。

## 注意事项

- 确保私有子网允许访问相关资源。
- 安全组应允许容器端口（5000）的入站流量。
- 负载均衡器监听器和目标组需预先创建，或另行 Terraform 配置。

---

如需进一步帮助，请提供你的网络模块配置和安全组定义，以便完善整体部署方案。
