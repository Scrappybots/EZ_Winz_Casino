# 🚀 Deployment Guide - NeoBank & Chrome Slots

## Prerequisites

- **Docker** or **Podman** (for local development)
- **Kubernetes cluster** (for production deployment)
- **kubectl** configured to access your cluster
- Python 3.11+ (for local testing without containers)
- **PostgreSQL 16** (for production database)

## 📦 Local Development Setup

### Option 1: Using Docker/Podman Compose (Recommended)

**Quick Setup:**
```powershell
# Automated setup with PostgreSQL
python setup_postgres.py
```

**Manual Setup:**
```powershell
# Build and start all services (app + PostgreSQL)
docker-compose up --build

# Or run in detached mode
docker-compose up -d --build

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f neobank
docker-compose logs -f postgres

# Stop the application
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

**Access:**
- Application: **http://localhost:8080**
- PostgreSQL: **localhost:5432** (user: neobank, password: neobank_dev_password)

**Database Access:**
```powershell
# Connect to PostgreSQL
docker exec -it neobank-postgres psql -U neobank -d neobank

# Or with Podman
podman exec -it neobank-postgres psql -U neobank -d neobank
```

### Option 2: Native Python with External PostgreSQL (Development)

**Prerequisites:**
1. Install and start PostgreSQL locally
2. Create database: `CREATE DATABASE neobank;`
3. Create user: `CREATE USER neobank WITH PASSWORD 'dev_password';`
4. Grant privileges: `GRANT ALL PRIVILEGES ON DATABASE neobank TO neobank;`

**Setup:**
```powershell
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1  # PowerShell
# OR
venv\Scripts\activate.bat     # CMD

# Install dependencies
pip install -r requirements.txt

# Set database URL
$env:DATABASE_URL="postgresql://neobank:dev_password@localhost:5432/neobank"

# Initialize database
cd ..
python init_db.py

# Run the application
cd backend
python app.py
```

Access at: **http://localhost:5000**

📚 **For complete PostgreSQL setup, migration, and troubleshooting, see [POSTGRESQL_MIGRATION.md](POSTGRESQL_MIGRATION.md)**

## 🏗️ Production Deployment on Kubernetes

### Step 1: Build Container Image

```powershell
# Build the image
docker build -t your-registry.com/neobank:latest -f Containerfile .

# Or with Podman
podman build -t your-registry.com/neobank:latest -f Containerfile .

# Push to registry
docker push your-registry.com/neobank:latest
```

### Step 2: Configure Secrets

```powershell
# Copy the secret template
cp k8s/secret.yaml.template k8s/secret.yaml

# Generate secure keys
python -c "import secrets; print('SECRET_KEY:', secrets.token_urlsafe(32))"
python -c "import secrets; print('POSTGRES_PASSWORD:', secrets.token_urlsafe(24))"

# Edit k8s/secret.yaml and update:
# - SECRET_KEY (for Flask)
# - POSTGRES_PASSWORD (in both postgres-secret and DATABASE_URL)
# Use your favorite editor (notepad, VSCode, etc.)
```

### Step 3: Update Deployment Images

Edit `k8s/deployment.yaml` and `k8s/db-init-job.yaml` to use your registry:

```yaml
image: your-registry.com/neobank:latest  # Your actual registry
```

### Step 4: Deploy to Kubernetes

📚 **See [K8S_DEPLOYMENT_ORDER.md](K8S_DEPLOYMENT_ORDER.md) for detailed step-by-step deployment guide.**

**Quick Deployment:**
```powershell
# 1. Create namespace
kubectl apply -f k8s/namespace.yaml

# 2. Create ConfigMaps
kubectl apply -f k8s/configmap.yaml

# 3. Create Secrets (after configuring!)
kubectl apply -f k8s/secret.yaml

# 4. Deploy PostgreSQL
kubectl apply -f k8s/postgres-deployment.yaml

# 5. Wait for PostgreSQL to be ready
kubectl wait --for=condition=ready pod -l app=postgres -n neotropolis --timeout=180s

# 6. Initialize database
kubectl apply -f k8s/db-init-job.yaml

# 7. Wait for initialization to complete
kubectl wait --for=condition=complete job/neobank-db-init -n neotropolis --timeout=120s

# 8. Deploy application
kubectl apply -f k8s/deployment.yaml

# 9. Create Service
kubectl apply -f k8s/service.yaml

# 10. Create Ingress (optional, for external access)
kubectl apply -f k8s/ingress.yaml
```

### Step 5: Verify Deployment

```powershell
# Check all resources
kubectl get all -n neotropolis

# Check pod status
kubectl get pods -n neotropolis

# Check PostgreSQL
kubectl get pods -n neotropolis -l app=postgres
kubectl exec -n neotropolis deployment/postgres-deployment -- pg_isready -U neobank

# Check application
kubectl get pods -n neotropolis -l app=neobank
kubectl logs -f deployment/neobank-deployment -n neotropolis

# Check services
kubectl get svc -n neotropolis

# Check ingress
kubectl get ingress -n neotropolis

# Test database connectivity
kubectl exec -n neotropolis deployment/neobank-deployment -- python -c "
from backend.app import app, db
with app.app_context():
    db.engine.connect()
    print('✅ Database connected')
"
```

### Step 6: Access Application

**Via Port Forward (for testing):**
```powershell
kubectl port-forward -n neotropolis svc/neobank-service 8080:80
```
Access at: **http://localhost:8080**

**Via Ingress:**
Configure your domain in `k8s/ingress.yaml` and access via your domain.

## 🔧 Configuration

### Environment Variables

All configuration is managed through Kubernetes ConfigMap and Secrets:

- **ConfigMap** (`k8s/configmap.yaml`): Non-sensitive configuration
- **Secret** (`k8s/secret.yaml`): Sensitive data like SECRET_KEY

### Common Configurations

**Adjust replicas** (in `k8s/deployment.yaml`):
```yaml
spec:
  replicas: 3  # Increase for high availability
```

**Adjust resources** (in `k8s/deployment.yaml`):
```yaml
resources:
  requests:
    memory: "512Mi"
    cpu: "500m"
  limits:
    memory: "1Gi"
    cpu: "1000m"
```

**Change domain** (in `k8s/ingress.yaml`):
```yaml
rules:
- host: neobank.your-domain.com
```

## 🔒 Security Checklist

- [ ] Changed default admin password (`admin` / `neotropolis2025`)
- [ ] Generated unique SECRET_KEY
- [ ] Configured HTTPS/TLS in Ingress
- [ ] Set appropriate rate limits
- [ ] Reviewed and adjusted resource limits
- [ ] Configured network policies (optional)
- [ ] Set up backup strategy for database
- [ ] Configured monitoring and alerting

## 📊 Monitoring & Maintenance

### Health Checks

```powershell
# Check application health
curl http://your-domain/health

# Or within the cluster
kubectl exec -n neotropolis <pod-name> -- curl localhost:5000/health
```

### Database Backup

```powershell
# Copy database from pod
kubectl cp neotropolis/<pod-name>:/app/data/neobank.db ./backup-$(Get-Date -Format "yyyyMMdd").db
```

### View Logs

```powershell
# Real-time logs
kubectl logs -n neotropolis -l app=neobank -f

# Logs from specific pod
kubectl logs -n neotropolis <pod-name>

# Previous logs (after restart)
kubectl logs -n neotropolis <pod-name> --previous
```

### Scaling

```powershell
# Scale replicas
kubectl scale deployment/neobank-deployment -n neotropolis --replicas=5

# Or edit deployment
kubectl edit deployment/neobank-deployment -n neotropolis
```

## 🔄 Updates & Rolling Updates

```powershell
# Build new image with version tag
docker build -t your-registry.com/neobank:v1.1.0 -f Containerfile .
docker push your-registry.com/neobank:v1.1.0

# Update deployment
kubectl set image deployment/neobank-deployment -n neotropolis neobank=your-registry.com/neobank:v1.1.0

# Monitor rollout
kubectl rollout status deployment/neobank-deployment -n neotropolis

# Rollback if needed
kubectl rollout undo deployment/neobank-deployment -n neotropolis
```

## 🧪 Testing

### API Testing

```powershell
# Register a user
curl -X POST http://localhost:8080/api/v1/auth/register `
  -H "Content-Type: application/json" `
  -d '{"character_name": "TestRunner", "password": "testpass123"}'

# Login
curl -X POST http://localhost:8080/api/v1/auth/login `
  -H "Content-Type: application/json" `
  -d '{"character_name": "TestRunner", "password": "testpass123"}'
```

## 🆘 Troubleshooting

### Pod won't start

```powershell
# Describe pod to see events
kubectl describe pod -n neotropolis <pod-name>

# Check logs
kubectl logs -n neotropolis <pod-name>
```

### Database issues

```powershell
# Check PVC status
kubectl get pvc -n neotropolis

# Verify volume mount
kubectl exec -n neotropolis <pod-name> -- ls -la /app/data
```

### Connection refused

- Check service configuration
- Verify ingress rules
- Check network policies
- Ensure firewall allows traffic

### Performance issues

- Increase replicas
- Adjust resource limits
- Check database size
- Review rate limiting settings

## 📝 Additional Notes

- The SQLite database is suitable for LARP event scale (100-500 concurrent users)
- For larger scale, consider migrating to PostgreSQL
- Regular database backups are recommended
- Monitor disk usage on PersistentVolume
- JWT tokens expire after 24 hours (configurable)

## 🎉 Event Day Checklist

- [ ] Application deployed and accessible
- [ ] Admin panel tested and working
- [ ] Test transactions successful
- [ ] Casino games functional
- [ ] API keys generated for ESP32 devices
- [ ] Backup strategy in place
- [ ] Contact information for tech support available
- [ ] Mobile accessibility verified
- [ ] Network connectivity stable

---

**Good luck with Neotropolis 2025! 🌃**
