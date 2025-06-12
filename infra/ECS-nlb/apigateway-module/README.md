# API Gateway + VPC Link Terraform Module

This module provisions an HTTP API Gateway integrated with an internal ECS service through a VPC Link and NLB listener.

---

## 📁 Module Structure

```
apigateway-module/
├── api.tf                # Defines aws_apigatewayv2_api
├── integration.tf        # HTTP_PROXY integration to NLB via VPC Link
├── outputs.tf            # Exports api_id, vpc_link_id
├── route.tf              # Defines ANY /{proxy+} route
├── stage.tf              # Configures $default deployment stage
├── vpc_link.tf           # Provisions VPC link using private subnets
├── variables.tf          # Input variables for the module
└── README.md             # Documentation
```

---

## 🔧 Input Variables

| Name                 | Type           | Description                                                             | Required |
| -------------------- | -------------- | ----------------------------------------------------------------------- | -------- |
| `project_name`       | `string`       | Name of the project, used to tag and name resources                     | ✅ Yes    |
| `private_subnet_ids` | `list(string)` | List of private subnet IDs for the VPC Link                             | ✅ Yes    |
| `ecs_service_sg_id`  | `string`       | Security Group ID used by the ECS service (for VPC Link connectivity)   | ✅ Yes    |
| `nlb_listener_arn`   | `string`       | ARN of the NLB listener used by the ECS service for backend integration | ✅ Yes    |

---

## 📤 Outputs

| Name           | Description                                    |
| -------------- | ---------------------------------------------- |
| `http_api_id`  | The ID of the created HTTP API Gateway         |
| `vpc_link_id`  | The ID of the created VPC Link                 |
| `api_endpoint` | The base URL of the deployed API Gateway stage |

---

## 🧹 Example Usage

```hcl
module "apigw" {
  source             = "./apigateway-module"

  project_name       = "bookstore"
  private_subnet_ids = module.network.private_subnet_ids
  ecs_service_sg_id  = aws_security_group.ecs_service_sg.id
  nlb_listener_arn   = aws_lb_listener.nlb_listener.arn
}
```

---

## 🖼️ Architecture Diagram

```mermaid
graph TD
  A[Client Request] --> B[API Gateway (HTTP API)]
  B --> C{Route: /{proxy+}}
  C --> D[VPC Link Integration]
  D --> E[NLB Listener (ECS Service)]
```

---

## 📝 Notes

- Ensure the NLB listener is reachable from the private subnets.
- VPC Link only supports NLB (not ALB).
- If you want to restrict access, use WAF or API Gateway authorizers.

---

## 📚 References

- [API Gateway HTTP API Docs](https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api.html)
- Terraform AWS Provider

