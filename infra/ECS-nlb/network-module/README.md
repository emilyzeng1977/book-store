# VPC Module Setup

本模块使用 Terraform 构建一个基本的 AWS 网络结构，包括：

- VPC
- 公有与私有子网
- Internet Gateway
- NAT Gateway 与 EIP
- 路由表与关联

结构图如下：

```
          +--------------------+
          |    Internet        |
          +--------+-----------+
                   |
         (Internet Gateway - IGW)
                   |
          +--------v-----------+
          |      VPC           |
          |  CIDR: 10.0.0.0/16 |
          +--------+-----------+
                   |
   +---------------+----------------+
   |                                |
+--v-----------+         +----------v---------+
| Public Subnet|         |  Private Subnet    |
| 10.0.0.0/24  |         |  10.0.1.0/24       |
| MapPublicIP ✔|         | MapPublicIP ✖     |
+------+--------+        +-----------+--------+
       |                             |
+------v--------+          +---------v---------+
| Route: IGW    |          | Route: NAT GW     |
+---------------+          +-------------------+
```

## 模块结构

```
vpc/
 ├── main.tf         # 主入口，提供 provider 和模块引用
 ├── vpc.tf          # 创建 VPC 和 Internet Gateway
 ├── subnets.tf      # 公有与私有子网定义
 ├── nat.tf          # Elastic IP 和 NAT Gateway
 ├── route_tables.tf # 路由表定义
 ├── associations.tf # 路由表与子网的关联
 └── variables.tf    # 输入变量定义
```

## 使用方式

```hcl
module "vpc" {
  source       = "./vpc"
  project_name = "demo-vpc"
}
```

## 输入变量

| 变量名        | 类型   | 描述                         |
|---------------|--------|------------------------------|
| `project_name` | string | 用于资源的标签标记和命名前缀 |

## 依赖

- Terraform >= 1.0
- AWS provider

## 初始化与部署

```bash
terraform init
terraform plan
terraform apply
```

## 注意事项

- 当前子网固定在 `ap-southeast-2a` 可用区，如需跨可用区部署，请调整 `availability_zone`。
- NAT Gateway 费用按小时计费，测试完成后建议销毁。

---

如需扩展更多子网、可用区或模块化拆分，也可继续迭代该模块。