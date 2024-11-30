# EKS 集群角色：eks_cluster_role 用于 EKS 集群管理，绑定了 AmazonEKSClusterPolicy。
# EKS 节点角色：eks_node_role 用于节点组的 EC2 实例，绑定了多种策略（如 AmazonEKSWorkerNodePolicy 等）。
# 动态策略绑定：通过 for_each 动态迭代，为节点组角色绑定多个策略，提高配置的灵活性和扩展性。

### IAM Role for Cluster ###
resource "aws_iam_role" "eks_cluster_role" {
  name = "${var.project}-eks-cluster-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "eks.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}

### Attach Policies to Cluster Role ###
resource "aws_iam_policy_attachment" "eks_cluster_policy" {
  name       = "${var.project}-eks-cluster-policy"
  roles      = [aws_iam_role.eks_cluster_role.name]
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
}

### IAM Role for Node Group ###
resource "aws_iam_role" "eks_node_role" {
  name = "${var.project}-eks-node-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_policy_attachment" "eks_node_policies" {
  for_each   = toset(var.eks_node_policies)
  name       = "${var.project}-eks-node-${basename(each.value)}"
  roles      = [aws_iam_role.eks_node_role.name]
  policy_arn = each.value
}