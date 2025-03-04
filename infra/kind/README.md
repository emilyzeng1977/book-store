### Command line


```
kind create cluster --config kind-config.yaml
kind get clusters
kind delete cluster --name kind
```

安装Calico
```
kubectl apply -f https://docs.projectcalico.org/manifests/calico.yaml
```

验证Calico安装
```
kubectl get pods -n kube-system
```

```commandline
kubectl run test1 --image=busybox --restart=Never -- sleep 3600
kubectl run test2 --image=busybox --restart=Never -- sleep 3600
kubectl run test3 --image=busybox --restart=Never -- sleep 3600
kubectl exec test1 -- ping -c 4 test2
kubectl exec test1 -- nslookup test2
kubectl exec -it test1 -- cat /etc/resolv.conf
kubectl run -it --rm busybox --image=busybox:latest --restart=Never -- nslookup <pod-name>
kubectl run -it --rm busybox --image=busybox:latest --restart=Never -- ping 192.168.110.130
 --grace-period=0 --force

```


根据 kubectl get pods 的输出，你已经有名为 test1 和 test2 的 Pod，且它们处于 Running 状态。但是 nslookup test1 返回 NXDOMAIN，说明 Pod 名称并没有直接被解析。这是因为 Kubernetes 的默认 DNS 配置不会为单个 Pod 自动创建 DNS 记录。

以下是详细说明和解决方法：

Kubernetes DNS 工作机制
服务名解析
Kubernetes DNS 默认只解析服务名称，而不会为单个 Pod 名称创建 DNS 记录。
例如，如果你创建了一个 Service，名字是 test1，DNS 解析会将请求指向这个服务。

Pod 名称解析（需要 Headless Service）
如果你想为 Pod 提供 DNS 解析，需要创建一个 Headless Service，并使用 Pod 的 DNS 子域名进行解析。

```
helm repo add chaos-mesh https://charts.chaos-mesh.org
helm repo update
helm install chaos-mesh chaos-mesh/chaos-mesh \
  --namespace chaos-testing --create-namespace \
  --set chaosDaemon.runtime=containerd \
  --set chaosDaemon.socketPath=/run/containerd/containerd.sock

kubectl get pods -n chaos-testing

// kubectl get clusterrolebinding chaos-mesh-controller-manager

```
安装 Prometheus Operator
```commandline
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

kubectl create namespace monitoring
helm install prometheus-operator prometheus-community/kube-prometheus-stack --namespace monitoring
kubectl get pods -n monitoring
```

```commandline
kubectl port-forward svc/prometheus-operator-grafana 3000:80 -n monitoring
```

User name: admin
We could get password by below command
```commandline
kubectl get secret prometheus-operator-grafana -n monitoring -o jsonpath="{.data.admin-password}" | base64 --decode
```

```commandline
kubectl port-forward -n monitoring svc/prometheus-operator-kube-p-prometheus 9090:9090
```
