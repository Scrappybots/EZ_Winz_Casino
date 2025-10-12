# PostgreSQL Quick Reference

## Local Development (Docker/Podman Compose)

### Start Services
```bash
# Automated
python setup_postgres.py

# Manual
podman compose up -d --build
```

### View Logs
```bash
# All services
podman compose logs -f

# Application only
podman compose logs -f neobank

# Database only
podman compose logs -f postgres
```

### Access Database
```bash
# Interactive psql
podman exec -it neobank-postgres psql -U neobank -d neobank

# Run single query
podman exec -it neobank-postgres psql -U neobank -d neobank -c "SELECT COUNT(*) FROM users;"
```

### Backup & Restore
```bash
# Backup
podman exec neobank-postgres pg_dump -U neobank neobank > backup.sql

# Restore
podman exec -i neobank-postgres psql -U neobank neobank < backup.sql
```

### Stop Services
```bash
# Stop (keep data)
podman compose down

# Stop and remove data
podman compose down -v
```

---

## Kubernetes

### Deploy (First Time)
```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml  # Configure first!
kubectl apply -f k8s/postgres-deployment.yaml
kubectl wait --for=condition=ready pod -l app=postgres -n neotropolis --timeout=180s
kubectl apply -f k8s/db-init-job.yaml
kubectl wait --for=condition=complete job/neobank-db-init -n neotropolis --timeout=120s
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml  # Optional
```

### Check Status
```bash
# All resources
kubectl get all -n neotropolis

# Pods
kubectl get pods -n neotropolis

# Logs
kubectl logs -f deployment/neobank-deployment -n neotropolis
kubectl logs -f deployment/postgres-deployment -n neotropolis
```

### Access Database
```bash
# Interactive psql
kubectl exec -it deployment/postgres-deployment -n neotropolis -- psql -U neobank -d neobank

# Run query
kubectl exec deployment/postgres-deployment -n neotropolis -- \
  psql -U neobank -d neobank -c "SELECT COUNT(*) FROM users;"
```

### Port Forward
```bash
# Application
kubectl port-forward -n neotropolis svc/neobank-service 8080:80

# Database (for direct access)
kubectl port-forward -n neotropolis svc/postgres-service 5432:5432
```

### Backup & Restore
```bash
# Backup
kubectl exec deployment/postgres-deployment -n neotropolis -- \
  pg_dump -U neobank neobank > backup.sql

# Restore
kubectl exec -i deployment/postgres-deployment -n neotropolis -- \
  psql -U neobank neobank < backup.sql
```

### Scale Application
```bash
# Scale to 3 replicas
kubectl scale deployment neobank-deployment -n neotropolis --replicas=3

# Check scaling
kubectl get pods -n neotropolis -l app=neobank
```

### Update Application
```bash
# Build and push new image
podman build -t your-registry.com/neobank:v1.1.0 -f Containerfile .
podman push your-registry.com/neobank:v1.1.0

# Update deployment
kubectl set image deployment/neobank-deployment neobank=your-registry.com/neobank:v1.1.0 -n neotropolis

# Monitor rollout
kubectl rollout status deployment/neobank-deployment -n neotropolis

# Rollback if needed
kubectl rollout undo deployment/neobank-deployment -n neotropolis
```

### Cleanup
```bash
# Remove everything
kubectl delete namespace neotropolis

# Remove app only (keep database)
kubectl delete deployment neobank-deployment -n neotropolis
kubectl delete svc neobank-service -n neotropolis
```

---

## Useful SQL Queries

```sql
-- List all users
SELECT character_name, account_number, balance FROM users;

-- Check system accounts
SELECT * FROM users WHERE account_number LIKE 'NC-SYST%' OR account_number LIKE 'NC-CASA%';

-- Recent transactions
SELECT * FROM transactions ORDER BY timestamp DESC LIMIT 10;

-- User transaction history
SELECT * FROM transactions 
WHERE from_account_id = (SELECT id FROM users WHERE character_name = 'PlayerName')
   OR to_account_id = (SELECT id FROM users WHERE character_name = 'PlayerName')
ORDER BY timestamp DESC;

-- Total users
SELECT COUNT(*) FROM users;

-- Total transactions
SELECT COUNT(*) FROM transactions;

-- Total money in circulation
SELECT SUM(balance) FROM users WHERE account_number NOT LIKE 'NC-SYST%';

-- Top 10 richest players
SELECT character_name, account_number, balance 
FROM users 
WHERE account_number NOT LIKE 'NC-SYST%' AND account_number NOT LIKE 'NC-CASA%'
ORDER BY balance DESC 
LIMIT 10;

-- Casino statistics
SELECT 
  COUNT(*) as total_bets,
  SUM(CASE WHEN transaction_type = 'casino_bet' THEN amount ELSE 0 END) as total_wagered,
  SUM(CASE WHEN transaction_type = 'casino_win' THEN amount ELSE 0 END) as total_won
FROM transactions;
```

---

## Environment Variables

### Application
- `DATABASE_URL` - PostgreSQL connection string (required)
- `SECRET_KEY` - Flask secret key (required)
- `JWT_EXPIRY_HOURS` - JWT token lifetime (default: 24)
- `RATE_LIMIT_PER_MINUTE` - API rate limit (default: 60)
- `FLASK_DEBUG` - Debug mode (default: False)

### PostgreSQL
- `POSTGRES_USER` - Database user (default: neobank)
- `POSTGRES_PASSWORD` - Database password (required)
- `POSTGRES_DB` - Database name (default: neobank)

---

## Connection Strings

### Docker Compose
```
postgresql://neobank:neobank_dev_password@postgres:5432/neobank
```

### Kubernetes
```
postgresql://neobank:YOUR-PASSWORD@postgres-service:5432/neobank
```

### Local (external PostgreSQL)
```
postgresql://neobank:YOUR-PASSWORD@localhost:5432/neobank
```

---

## Troubleshooting

### Can't connect to database
```bash
# Check PostgreSQL is running
podman compose ps postgres  # Docker Compose
kubectl get pods -l app=postgres -n neotropolis  # Kubernetes

# Check PostgreSQL logs
podman compose logs postgres
kubectl logs -l app=postgres -n neotropolis

# Test connectivity
podman exec neobank-postgres pg_isready -U neobank
kubectl exec deployment/postgres-deployment -n neotropolis -- pg_isready -U neobank
```

### Application crashes on startup
```bash
# Check application logs
podman compose logs neobank
kubectl logs -f deployment/neobank-deployment -n neotropolis

# Verify DATABASE_URL is correct
echo $DATABASE_URL  # Local
kubectl get secret neobank-secret -n neotropolis -o jsonpath='{.data.DATABASE_URL}' | base64 -d
```

### Database initialization failed
```bash
# Re-run initialization
podman compose restart neobank  # Docker Compose
kubectl delete job neobank-db-init -n neotropolis && kubectl apply -f k8s/db-init-job.yaml

# Check init logs
kubectl logs job/neobank-db-init -n neotropolis
```

---

## Health Checks

### Application
```bash
curl http://localhost:8080/health
```

### PostgreSQL
```bash
pg_isready -h localhost -U neobank
```

---

## Generate Secure Secrets

```bash
# Flask SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# PostgreSQL password
python -c "import secrets; print(secrets.token_urlsafe(24))"
```
