### EKS Cluster ###
resource "aws_eks_cluster" "eks_cluster" {
  name     = "${var.project}-eks-cluster"
  role_arn = aws_iam_role.eks_cluster_role.arn

  vpc_config {
    subnet_ids = concat(
      aws_subnet.public_subnet[*].id,
      aws_subnet.private_subnet[*].id
    )
    security_group_ids = [aws_security_group.eks_sg.id]
  }

  tags = {
    Name = "${var.project}-eks-cluster"
  }

  depends_on = [
    aws_iam_policy_attachment.eks_cluster_policy,
  ]
}

### EKS Node Group ###
resource "aws_eks_node_group" "eks_node_group" {
  cluster_name    = aws_eks_cluster.eks_cluster.name
  node_group_name = "${var.project}-eks-node-group"
  node_role_arn   = aws_iam_role.eks_node_role.arn
  subnet_ids      = aws_subnet.private_subnet[*].id
  capacity_type   = "SPOT"
  instance_types  = ["t2.small"]

  scaling_config {
    desired_size = 1
    max_size     = 1
    min_size     = 1
  }

  # Ensure that IAM Role permissions are created before and deleted after EKS Node Group handling.
  # Otherwise, EKS will not be able to properly delete EC2 Instances and Elastic Network Interfaces.
  depends_on = [
    aws_iam_policy_attachment.eks_node_policies,
  ]

  tags = {
    Name = "${var.project}-eks-node-group"
  }
}