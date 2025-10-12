# Kubernetes Deployment Order

This document specifies the correct order to deploy all Kubernetes resources for the NeoBank application with PostgreSQL.

## Deployment Steps

### 1. Create Namespace
```bash
kubectl apply -f k8s/namespace.yaml
```

**Wait**: Verify namespace is created
```bash
kubectl get namespace neotropolis
```

---

### 2. Create ConfigMaps
```bash
kubectl apply -f k8s/configmap.yaml
```

**Verify**:
```bash
kubectl get configmap -n neotropolis
```

---

### 3. Create Secrets

**IMPORTANT**: First, configure your secrets!

```bash
# Copy template
cp k8s/secret.yaml.template k8s/secret.yaml

# Generate secure values
python -c "import secrets; print('SECRET_KEY:', secrets.token_urlsafe(32))"
python -c "import secrets; print('POSTGRES_PASSWORD:', secrets.token_urlsafe(24))"

# Edit k8s/secret.yaml with your generated values
# Then apply:
kubectl apply -f k8s/secret.yaml
```

**Verify**:
```bash
kubectl get secrets -n neotropolis
```

---

### 4. Deploy PostgreSQL Database
```bash
kubectl apply -f k8s/postgres-deployment.yaml
```

**Wait**: Wait for PostgreSQL to be ready (this is critical!)
```bash
kubectl wait --for=condition=ready pod -l app=postgres -n neotropolis --timeout=180s
```

**Verify**:
```bash
kubectl get pods -n neotropolis -l app=postgres
kubectl get svc -n neotropolis -l app=postgres
kubectl get pvc -n neotropolis

# Test database connectivity
kubectl exec -n neotropolis deployment/postgres-deployment -- pg_isready -U neobank
```

---

### 5. Initialize Database

**Build and push your application image first**:
```bash
# Build image
podman build -t your-registry.com/neobank:latest -f Containerfile .

# Push to registry
podman push your-registry.com/neobank:latest

# Update image reference in k8s/db-init-job.yaml and k8s/deployment.yaml
```

**Run initialization job**:
```bash
kubectl apply -f k8s/db-init-job.yaml
```

**Wait**: Monitor initialization
```bash
kubectl wait --for=condition=complete job/neobank-db-init -n neotropolis --timeout=120s
kubectl logs job/neobank-db-init -n neotropolis
```

**Verify** database is initialized:
```bash
kubectl exec -n neotropolis deployment/postgres-deployment -- \
  psql -U neobank -d neobank -c "SELECT COUNT(*) FROM users;"
```

---

### 6. Deploy Application
```bash
kubectl apply -f k8s/deployment.yaml
```

**Wait**: Wait for application pods to be ready
```bash
kubectl wait --for=condition=ready pod -l app=neobank -n neotropolis --timeout=180s
```

**Verify**:
```bash
kubectl get pods -n neotropolis -l app=neobank
kubectl logs -f deployment/neobank-deployment -n neotropolis
```

---

### 7. Create Service
```bash
kubectl apply -f k8s/service.yaml
```

**Verify**:
```bash
kubectl get svc -n neotropolis -l app=neobank
```

---

### 8. Configure Ingress (Optional)

**Update** `k8s/ingress.yaml` with your domain first, then:
```bash
kubectl apply -f k8s/ingress.yaml
```

**Verify**:
```bash
kubectl get ingress -n neotropolis
kubectl describe ingress neobank-ingress -n neotropolis
```

---

## Complete Deployment Command

For automated deployment (after configuring secrets and updating image references):

```bash
kubectl apply -f k8s/namespace.yaml && \
kubectl apply -f k8s/configmap.yaml && \
kubectl apply -f k8s/secret.yaml && \
kubectl apply -f k8s/postgres-deployment.yaml && \
kubectl wait --for=condition=ready pod -l app=postgres -n neotropolis --timeout=180s && \
kubectl apply -f k8s/db-init-job.yaml && \
kubectl wait --for=condition=complete job/neobank-db-init -n neotropolis --timeout=120s && \
kubectl apply -f k8s/deployment.yaml && \
kubectl wait --for=condition=ready pod -l app=neobank -n neotropolis --timeout=180s && \
kubectl apply -f k8s/service.yaml && \
kubectl apply -f k8s/ingress.yaml
```

---

## Verification Commands

### Check All Resources
```bash
kubectl get all -n neotropolis
```

### Check Health
```bash
# Application health
kubectl exec -n neotropolis deployment/neobank-deployment -- curl http://localhost:5000/health

# Database connectivity
kubectl exec -n neotropolis deployment/neobank-deployment -- python -c "
from backend.app import app, db
with app.app_context():
    db.engine.connect()
    print('✅ Database connection successful')
"
```

### Check Logs
```bash
# Application logs
kubectl logs -f deployment/neobank-deployment -n neotropolis

# PostgreSQL logs
kubectl logs -f deployment/postgres-deployment -n neotropolis

# All logs
kubectl logs -f -n neotropolis --all-containers=true
```

### Port Forward for Testing
```bash
# Forward application port
kubectl port-forward -n neotropolis svc/neobank-service 8080:80

# Forward PostgreSQL port (for direct DB access)
kubectl port-forward -n neotropolis svc/postgres-service 5432:5432
```

---

## Troubleshooting

### PostgreSQL Pod Not Starting
```bash
# Check events
kubectl describe pod -l app=postgres -n neotropolis

# Check PVC
kubectl describe pvc postgres-pvc -n neotropolis

# Check storage class
kubectl get storageclass
```

### Application Pods Not Starting
```bash
# Check pod events
kubectl describe pod -l app=neobank -n neotropolis

# Check if secrets exist
kubectl get secret neobank-secret -n neotropolis -o yaml

# Verify DATABASE_URL is correct
kubectl get secret neobank-secret -n neotropolis -o jsonpath='{.data.DATABASE_URL}' | base64 -d
```

### Database Initialization Failed
```bash
# Check job logs
kubectl logs job/neobank-db-init -n neotropolis

# Re-run initialization job
kubectl delete job neobank-db-init -n neotropolis
kubectl apply -f k8s/db-init-job.yaml
```

---

## Cleanup

### Remove Everything
```bash
kubectl delete namespace neotropolis
```

### Selective Cleanup
```bash
# Remove application only (keep database)
kubectl delete deployment neobank-deployment -n neotropolis
kubectl delete svc neobank-service -n neotropolis

# Remove database (WARNING: deletes all data!)
kubectl delete deployment postgres-deployment -n neotropolis
kubectl delete svc postgres-service -n neotropolis
kubectl delete pvc postgres-pvc -n neotropolis
```

---

## Updating the Application

### Update Application Code
```bash
# Build new image with version tag
podman build -t your-registry.com/neobank:v1.1.0 -f Containerfile .
podman push your-registry.com/neobank:v1.1.0

# Update deployment
kubectl set image deployment/neobank-deployment neobank=your-registry.com/neobank:v1.1.0 -n neotropolis

# Monitor rollout
kubectl rollout status deployment/neobank-deployment -n neotropolis

# Rollback if needed
kubectl rollout undo deployment/neobank-deployment -n neotropolis
```

### Database Schema Changes

If you need to update the database schema:

1. Create a database migration script
2. Run it as a Kubernetes Job (similar to db-init-job.yaml)
3. Wait for migration to complete
4. Deploy updated application

---

## Production Checklist

Before deploying to production:

- [ ] Changed all default passwords in `k8s/secret.yaml`
- [ ] Updated `SECRET_KEY` to a secure random value
- [ ] Updated container image registry in all YAML files
- [ ] Configured appropriate resource limits/requests
- [ ] Set up proper ingress with TLS certificates
- [ ] Configured storage class for production (not "standard")
- [ ] Set up monitoring and alerting
- [ ] Configured backup strategy for PostgreSQL
- [ ] Changed admin user password from default
- [ ] Reviewed and adjusted rate limits
- [ ] Configured log aggregation
- [ ] Set up network policies (if required)
- [ ] Tested disaster recovery procedures
