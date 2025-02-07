#bin/bash
Kubectl delete -f ./deployment/service-account.yml
Kubectl delete -f ./deployment/cluster-role.yml
Kubectl delete -f ./deployment/cluster-role-binding.yml
Kubectl delete -f ./deployment/deployment.yml