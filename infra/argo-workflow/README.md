### Command line
https://argo-workflows.readthedocs.io/en/latest/quick-start/

```
kubectl create namespace argo
kubectl apply -n argo -f "https://github.com/argoproj/argo-workflows/releases/download/v3.5.14/quick-start-minimal.yaml"
```

验证
```
kubectl get pods -n argo
```
暴露端口
```
kubectl -n argo port-forward svc/argo-server 2746:2746
```

```
helm uninstall argo --namespace argo
```

argo submit https://raw.githubusercontent.com/argoproj/argo-workflows/master/examples/hello-world.yaml --watch

example
example 4-1
example 4-2
example 4-3
```
kubectl apply -f checkout.yaml -n argo
```