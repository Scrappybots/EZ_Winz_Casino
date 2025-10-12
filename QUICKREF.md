# 📋 Quick Reference Card - NeoBank & Chrome Slots

## 🚀 Quick Start Commands

### Local Development
```powershell
# Docker Compose
docker-compose up --build

# Native Python
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
cd ..
python init_db.py
cd backend
python app.py
```

### Kubernetes Deployment
```powershell
# Initial deployment
kubectl apply -f k8s/

# Initialize database
kubectl exec -n neotropolis <pod-name> -- python init_db.py

# Check status
kubectl get all -n neotropolis
```

---

## 🔐 Default Credentials

| Role  | Username | Password         | Change Required |
|-------|----------|------------------|-----------------|
| Admin | `admin`  | `neotropolis2025`| ✅ YES!         |

---

## 🌐 Endpoints

### User-Facing
- **Main App**: `http://localhost:8080`
- **Health Check**: `http://localhost:8080/health`

### API Endpoints

#### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login

#### Banking
- `GET /api/v1/account` - Get account info
- `POST /api/v1/transactions` - Create transfer
- `GET /api/v1/account/transactions` - Transaction history

#### Casino
- `POST /api/v1/casino/glitch-grid/spin` - Spin Glitch Grid
- `POST /api/v1/casino/starlight-smuggler/spin` - Spin Starlight Smuggler

#### External API (Requires API Key)
- `POST /api/v1/external/transactions` - Create transaction
- `GET /api/v1/external/account/{account}/balance` - Check balance

#### Admin (Requires Admin Role)
- `GET /admin/users/search?q={query}` - Search users
- `POST /admin/users/{account}/adjust-balance` - Adjust balance
- `GET /admin/api-keys` - List API keys
- `POST /admin/api-keys` - Create API key
- `DELETE /admin/api-keys/{id}` - Revoke API key
- `GET /admin/casino/config` - Get casino config
- `PUT /admin/casino/config/{game}` - Update game config

---

## 📊 System Accounts

| Account Number | Name          | Purpose                |
|----------------|---------------|------------------------|
| `NC-SYST-EM00` | SYSTEM        | Admin adjustments      |
| `NC-CASA-0000` | CASINO HOUSE  | Casino bank            |

---

## 🎰 Casino Games

### Glitch Grid (3-Reel)
- **Bet**: Any amount (¤10 recommended)
- **Symbols**: 💀 01 🔌 ㊙️ 🏢 (Wild)
- **Top Prize**: 100x (three wilds)

### Starlight Smuggler (5-Reel, 9 Paylines)
- **Bet per Line**: Any amount (¤5 recommended)
- **Total Bet**: Bet × 9 lines
- **Symbols**: 🚀 🗺️ 🔫 💎 ⭐ 🌀 (Scatter)
- **Top Prize**: 250x (five gems)
- **Bonus**: 3+ scatters = 5 free spins

---

## 🔧 Configuration

### Environment Variables
```env
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///neobank.db
JWT_EXPIRY_HOURS=24
RATE_LIMIT_PER_MINUTE=60
FLASK_DEBUG=False
```

### Kubernetes ConfigMap
Edit `k8s/configmap.yaml` for non-sensitive config

### Kubernetes Secret
Edit `k8s/secret.yaml` for sensitive data

---

## 🛠️ Troubleshooting

### Problem: Can't login
```powershell
# Check database exists
ls backend/neobank.db

# Reinitialize database
python init_db.py
```

### Problem: Pod won't start
```powershell
# Check pod status
kubectl describe pod -n neotropolis <pod-name>

# Check logs
kubectl logs -n neotropolis <pod-name>
```

### Problem: 401 Unauthorized
- Check JWT token is included in Authorization header
- Token format: `Bearer <token>`
- Tokens expire after 24 hours (default)

### Problem: API key not working
- Verify key is active in admin panel
- Check header: `X-API-Key: <key>`
- Rate limit: 100 requests/minute

---

## 📦 Database Backup

```powershell
# Get pod name
kubectl get pods -n neotropolis

# Copy database
kubectl cp neotropolis/<pod-name>:/app/data/neobank.db backup.db
```

---

## 🔄 Update Deployment

```powershell
# Build new image
docker build -t your-registry.com/neobank:v1.1.0 -f Containerfile .
docker push your-registry.com/neobank:v1.1.0

# Update deployment
kubectl set image deployment/neobank-deployment -n neotropolis neobank=your-registry.com/neobank:v1.1.0

# Monitor rollout
kubectl rollout status deployment/neobank-deployment -n neotropolis
```

---

## 📝 Common Tasks

### Create API Key
1. Login as admin
2. Navigate to Admin Panel
3. Click "GENERATE NEW KEY"
4. Enter description
5. Copy key immediately (won't be shown again)

### Adjust User Balance
1. Login as admin
2. Search for user
3. Click "ADJUST"
4. Enter amount (+ credit, - debit)
5. Provide reason
6. Confirm

### Disable Casino Game
1. Login as admin
2. Navigate to Casino Controls
3. Uncheck "Enabled" for game
4. Game immediately unavailable to players

### Change Payout Percentage
1. Login as admin
2. Navigate to Casino Controls
3. Adjust "Payout %" slider (50-99%)
4. Changes apply to next spin

---

## 🧪 Testing

### Manual Test Flow
1. Register a test user
2. Fund account (via admin panel)
3. Create a transfer to another user
4. Play casino games
5. Verify transactions in history

### Run Test Suite
```powershell
# Install test dependencies
pip install -r requirements-dev.txt

# Run tests
pytest test_suite.py -v
```

---

## 📞 Support Contacts

| Issue Type        | Contact Method      |
|-------------------|---------------------|
| During Event      | In-game radio       |
| Pre-Event Setup   | Discord server      |
| Critical Outage   | Emergency phone     |

---

## 🎭 Event Day Checklist

- [ ] Application deployed and accessible
- [ ] Admin password changed
- [ ] Test user can register/login
- [ ] Transfers work correctly
- [ ] Casino games functional
- [ ] API keys generated for external systems
- [ ] Database backup configured
- [ ] Mobile access verified
- [ ] Admin panel accessible
- [ ] Emergency contacts available

---

## 🚨 Emergency Commands

### Restart all pods
```powershell
kubectl rollout restart deployment/neobank-deployment -n neotropolis
```

### Scale to zero (emergency shutdown)
```powershell
kubectl scale deployment/neobank-deployment -n neotropolis --replicas=0
```

### Scale back up
```powershell
kubectl scale deployment/neobank-deployment -n neotropolis --replicas=2
```

### View recent logs
```powershell
kubectl logs -n neotropolis -l app=neobank --tail=100
```

---

**Keep this card handy during the Neotropolis event! 🌃**
