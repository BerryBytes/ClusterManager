#bin/bash
Kubectl apply -f ./deployment/service-account.yml
Kubectl apply -f ./deployment/cluster-role.yml
Kubectl apply -f ./deployment/cluster-role-binding.yml
Kubectl apply -f ./deployment/deployment.yml