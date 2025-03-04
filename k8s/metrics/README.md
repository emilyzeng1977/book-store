### 安装
安装
```
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install prometheus-operator prometheus-community/kube-prometheus-stack --namespace monitoring --create-namespace
```

你可以通过端口转发访问 Prometheus 或 Grafana：
```
kubectl port-forward svc/prometheus-operated 9090 -n monitoring
kubectl port-forward svc/grafana 3000 -n monitoring
```
然后在浏览器中访问：

Prometheus: http://localhost:9090
Grafana: http://localhost:3000
默认用户名：admin，密码：prom-operator（可以修改）


