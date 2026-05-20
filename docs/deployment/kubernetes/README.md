# Kubernetes Deployment Guide

## Suggested manifest layout

```text
deploy/k8s/
  base/
    deployment.yaml
    service.yaml
    configmap.yaml
    kustomization.yaml
  overlays/
    prod/
      kustomization.yaml
      patch-resources.yaml
      patch-replicas.yaml
```

## Core resources

- `Deployment`: Streamlit container with probes and resource limits.
- `Service`: ClusterIP/LoadBalancer depending on hosting provider.
- `ConfigMap`: non-secret runtime configuration.
- `Secret`: API keys and Notion token.
- `Ingress`: TLS + hostname routing.

## Secret management

- Do not commit base64 secrets to git.
- Use sealed-secrets, SOPS, or cluster secret manager integration.
- Scope secret access to namespace and service account.

## Operational recommendations

- Keep replicas >= 2 for `main` production branch.
- Enable horizontal pod autoscaling when traffic fluctuates.
- Add readiness/liveness probes before production rollout.
- Use rolling update strategy with max unavailable 0 for zero downtime.
