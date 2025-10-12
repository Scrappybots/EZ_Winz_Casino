# PostgreSQL Migration Guide

## Overview
The NeoBank application has been migrated from SQLite to PostgreSQL for improved scalability, concurrent access, and production readiness.

## Architecture Changes

### Docker Compose (Local Development)
- **postgres** container: PostgreSQL 16 database
- **neobank** container: Flask application (now depends on postgres)

### Kubernetes (Production)
- **postgres-deployment**: PostgreSQL database with persistent storage
- **neobank-deployment**: Application pods (now stateless, multiple replicas supported)
- **db-init-job**: One-time database initialization job

## Local Development with Docker Compose

### Prerequisites
- Docker or Podman installed
- docker-compose or podman-compose

### Quick Start

1. **Build and start all services:**
   ```bash
   podman compose up --build -d
   ```

2. **Check logs:**
   ```bash
   # All services
   podman compose logs -f
   
   # Just the app
   podman compose logs -f neobank
   
   # Just the database
   podman compose logs -f postgres
   ```

3. **Access the application:**
   - Web UI: http://localhost:8080
   - API: http://localhost:8080/api/v1/

4. **Stop services:**
   ```bash
   podman compose down
   ```

5. **Stop and remove all data:**
   ```bash
   podman compose down -v
   ```

### Database Access

Connect to PostgreSQL directly:
```bash
podman exec -it neobank-postgres psql -U neobank -d neobank
```

Common queries:
```sql
-- List all users
SELECT character_name, account_number, balance FROM users;

-- View recent transactions
SELECT * FROM transactions ORDER BY timestamp DESC LIMIT 10;

-- Check system accounts
SELECT * FROM users WHERE account_number LIKE 'NC-SYST%' OR account_number LIKE 'NC-CASA%';
```

## Kubernetes Deployment

### Prerequisites
- Kubernetes cluster (1.24+)
- kubectl configured
- Container registry for your images

### Step 1: Create Namespace
```bash
kubectl apply -f k8s/namespace.yaml
```

### Step 2: Configure Secrets
1. Copy the secret template:
   ```bash
   cp k8s/secret.yaml.template k8s/secret.yaml
   ```

2. Generate secure secrets:
   ```bash
   # Generate SECRET_KEY
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   
   # Generate POSTGRES_PASSWORD
   python -c "import secrets; print(secrets.token_urlsafe(24))"
   ```

3. Edit `k8s/secret.yaml` and replace:
   - `SECRET_KEY`: Use generated key
   - `POSTGRES_PASSWORD`: Use generated password (in both secrets)
   - Update the password in `DATABASE_URL` to match

4. Apply secrets:
   ```bash
   kubectl apply -f k8s/secret.yaml
   ```

### Step 3: Deploy ConfigMaps
```bash
kubectl apply -f k8s/configmap.yaml
```

### Step 4: Deploy PostgreSQL
```bash
kubectl apply -f k8s/postgres-deployment.yaml
```

Wait for PostgreSQL to be ready:
```bash
kubectl wait --for=condition=ready pod -l app=postgres -n neotropolis --timeout=120s
```

### Step 5: Build and Push Application Image
```bash
# Build the image
podman build -t your-registry.com/neobank:latest -f Containerfile .

# Push to registry
podman push your-registry.com/neobank:latest
```

Update `k8s/deployment.yaml` and `k8s/db-init-job.yaml` with your image registry.

### Step 6: Initialize Database
```bash
kubectl apply -f k8s/db-init-job.yaml
```

Check initialization logs:
```bash
kubectl logs -f job/neobank-db-init -n neotropolis
```

### Step 7: Deploy Application
```bash
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

### Step 8: Configure Ingress (Optional)
```bash
kubectl apply -f k8s/ingress.yaml
```

### Verify Deployment
```bash
# Check all resources
kubectl get all -n neotropolis

# Check pod status
kubectl get pods -n neotropolis

# View application logs
kubectl logs -f deployment/neobank-deployment -n neotropolis

# Check database connectivity
kubectl exec -it deployment/neobank-deployment -n neotropolis -- python -c "
from backend.app import app, db
with app.app_context():
    print('Database connection successful!')
    from backend.models import User
    print(f'Total users: {User.query.count()}')
"
```

## Database Initialization

The database is automatically initialized with:
- **SYSTEM** account (NC-SYST-EM00): Unlimited funds for system operations
- **CASINO HOUSE** account (NC-CASA-0000): Casino bank
- **admin** account: Default admin user (password: neotropolis2025)

**⚠️ IMPORTANT:** Change the admin password immediately in production!

## Connection Strings

### Local Development (Docker Compose)
```
postgresql://neobank:neobank_dev_password@postgres:5432/neobank
```

### Kubernetes
```
postgresql://neobank:YOUR-PASSWORD@postgres-service:5432/neobank
```

### External Connection (if exposed)
```
postgresql://neobank:YOUR-PASSWORD@your-host:5432/neobank
```

## Backup and Restore

### Docker Compose Backup
```bash
# Create backup
podman exec neobank-postgres pg_dump -U neobank neobank > backup.sql

# Restore backup
podman exec -i neobank-postgres psql -U neobank neobank < backup.sql
```

### Kubernetes Backup
```bash
# Create backup
kubectl exec -n neotropolis deployment/postgres-deployment -- \
  pg_dump -U neobank neobank > backup.sql

# Restore backup
kubectl exec -i -n neotropolis deployment/postgres-deployment -- \
  psql -U neobank neobank < backup.sql
```

## Troubleshooting

### Application can't connect to database

1. Check PostgreSQL is running:
   ```bash
   # Docker Compose
   podman compose ps postgres
   
   # Kubernetes
   kubectl get pods -l app=postgres -n neotropolis
   ```

2. Check database logs:
   ```bash
   # Docker Compose
   podman compose logs postgres
   
   # Kubernetes
   kubectl logs -l app=postgres -n neotropolis
   ```

3. Verify connection string is correct in secrets/environment

### Database initialization fails

1. Check if database is ready:
   ```bash
   # Docker Compose
   podman exec neobank-postgres pg_isready -U neobank
   
   # Kubernetes
   kubectl exec deployment/postgres-deployment -n neotropolis -- pg_isready -U neobank
   ```

2. Check init logs:
   ```bash
   # Docker Compose
   podman compose logs neobank
   
   # Kubernetes
   kubectl logs job/neobank-db-init -n neotropolis
   ```

### Slow performance

1. Check PostgreSQL resource usage:
   ```bash
   # Kubernetes
   kubectl top pod -l app=postgres -n neotropolis
   ```

2. Consider increasing resources in deployment.yaml
3. Add database indexes if needed (already included for common queries)

## Migration from SQLite

If you have existing SQLite data to migrate:

1. Export from SQLite:
   ```bash
   sqlite3 neobank.db .dump > sqlite_dump.sql
   ```

2. Convert SQLite SQL to PostgreSQL (manual adjustments may be needed):
   - Replace `AUTOINCREMENT` with `SERIAL`
   - Replace `REAL` with `DOUBLE PRECISION`
   - Adjust datetime handling

3. Import to PostgreSQL:
   ```bash
   psql -U neobank -d neobank -f converted_dump.sql
   ```

## Environment Variables

### Application
- `DATABASE_URL`: PostgreSQL connection string (required)
- `SECRET_KEY`: Flask secret key (required)
- `JWT_EXPIRY_HOURS`: JWT token expiry (default: 24)
- `RATE_LIMIT_PER_MINUTE`: API rate limit (default: 60)
- `FLASK_DEBUG`: Debug mode (default: False)

### PostgreSQL
- `POSTGRES_USER`: Database user (default: neobank)
- `POSTGRES_PASSWORD`: Database password (required)
- `POSTGRES_DB`: Database name (default: neobank)

## Security Considerations

1. **Always use strong passwords** in production
2. **Change default admin credentials** immediately
3. **Use secrets management** (not plain text) in Kubernetes
4. **Enable TLS** for PostgreSQL connections in production
5. **Restrict database access** to application pods only
6. **Regular backups** are essential
7. **Monitor logs** for suspicious activity

## Performance Tuning

### PostgreSQL Configuration
For production, consider tuning these PostgreSQL parameters:
- `shared_buffers`: 25% of system RAM
- `effective_cache_size`: 50-75% of system RAM
- `max_connections`: Based on expected concurrent users
- `work_mem`: For complex queries

### Application Scaling
- Increase `replicas` in deployment.yaml for more app instances
- Use connection pooling (already configured with SQLAlchemy)
- Consider read replicas for heavy read workloads

## Monitoring

### Health Checks
- Application: http://your-app/health
- PostgreSQL: `pg_isready` command

### Metrics to Monitor
- Database connections (current/max)
- Query performance (slow queries)
- Disk usage (PostgreSQL data volume)
- Application response times
- Error rates in logs
