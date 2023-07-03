kompose convert

kubectl apply -f mongodb-service.yaml,sdd-poc-server-service.yaml,mongodb-deployment.yaml,mongodata-persistentvolumeclaim.yaml,sdd-network-networkpolicy.yaml,sdd-poc-server-deployment.yaml,sdd-poc-server-claim0-persistentvolumeclaim.yaml,sdd-poc-server-claim1-persistentvolumeclaim.yaml
