# 🏗️ System Architecture - NeoBank & Chrome Slots

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         PLAYERS (Mobile Web)                     │
│                    iOS Safari / Android Chrome                   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTPS
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      KUBERNETES CLUSTER                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    Ingress Controller                      │  │
│  │           (nginx-ingress / TLS termination)               │  │
│  └──────────────────────┬───────────────────────────────────┘  │
│                         │                                        │
│                         ▼                                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                 NeoBank Service (ClusterIP)               │  │
│  │                     Load Balancer                         │  │
│  └──────────┬───────────────────────────────┬────────────────┘  │
│             │                               │                    │
│             ▼                               ▼                    │
│  ┌──────────────────┐           ┌──────────────────┐           │
│  │   NeoBank Pod 1  │           │   NeoBank Pod 2  │  (N pods) │
│  │                  │           │                  │           │
│  │ ┌──────────────┐ │           │ ┌──────────────┐ │           │
│  │ │   Flask App  │ │           │ │   Flask App  │ │           │
│  │ │  + Vue.js UI │ │           │ │  + Vue.js UI │ │           │
│  │ │   Gunicorn   │ │           │ │   Gunicorn   │ │           │
│  │ └──────┬───────┘ │           │ └──────┬───────┘ │           │
│  │        │         │           │        │         │           │
│  │        ▼         │           │        ▼         │           │
│  │ ┌──────────────┐ │           │ ┌──────────────┐ │           │
│  │ │SQLite DB File│ │           │ │SQLite DB File│ │           │
│  │ └──────────────┘ │           │ └──────────────┘ │           │
│  └────────┬─────────┘           └─────────┬────────┘           │
│           │                               │                    │
│           └───────────────┬───────────────┘                    │
│                           │                                    │
│                           ▼                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │      Persistent Volume (PVC)                              │  │
│  │      /app/data/neobank.db                                 │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                             │
                             │ External API
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│               EXTERNAL SYSTEMS (ESP32, Terminals)                │
│            API Key Authentication via HTTP/HTTPS                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Component Details

### Frontend Layer (Vue.js SPA)

```
┌─────────────────────────────────────┐
│       Vue.js 3 Application           │
├─────────────────────────────────────┤
│  • index.html                        │
│  • app.js (Main Vue app)             │
│  • cyberpunk.css (Dark theme)        │
├─────────────────────────────────────┤
│  Views:                              │
│  ├─ Authentication (Login/Register)  │
│  ├─ Bank Dashboard                   │
│  │  ├─ Balance Display               │
│  │  ├─ P2P Transfer                  │
│  │  └─ Transaction History           │
│  ├─ Casino                            │
│  │  ├─ Glitch Grid (3-reel)          │
│  │  └─ Starlight Smuggler (5x3)      │
│  └─ Admin Panel (GM only)            │
│     ├─ User Management                │
│     ├─ API Key Management             │
│     └─ Casino Controls                │
└─────────────────────────────────────┘
```

### Backend Layer (Flask API)

```
┌─────────────────────────────────────────────────────┐
│              Flask Application (app.py)              │
├─────────────────────────────────────────────────────┤
│  Routes:                                             │
│  ├─ /api/v1/auth/*           (Authentication)       │
│  ├─ /api/v1/account/*        (User account)         │
│  ├─ /api/v1/transactions     (P2P transfers)        │
│  ├─ /api/v1/casino/*         (Casino games)         │
│  ├─ /api/v1/external/*       (External API)         │
│  └─ /admin/*                 (Admin panel)          │
├─────────────────────────────────────────────────────┤
│  Modules:                                            │
│  ├─ models.py     (Database ORM models)             │
│  ├─ auth.py       (JWT authentication)              │
│  ├─ transactions.py (Transaction engine)            │
│  ├─ casino.py     (Slot machine logic)              │
│  └─ admin.py      (Admin functions)                 │
├─────────────────────────────────────────────────────┤
│  Middleware:                                         │
│  ├─ Flask-CORS    (Cross-origin support)            │
│  ├─ Flask-Limiter (Rate limiting)                   │
│  └─ Flask-JWT     (Token validation)                │
└─────────────────────────────────────────────────────┘
```

### Database Schema

```sql
┌──────────────────────────────────────────────────────────┐
│                     USERS TABLE                           │
├──────────────────────────────────────────────────────────┤
│  id (PK)                                                  │
│  character_name (UNIQUE)                                  │
│  password_hash                                            │
│  account_number (UNIQUE, NC-XXXX-XXXX)                    │
│  faction                                                  │
│  balance                                                  │
│  is_admin                                                 │
│  created_at                                               │
└──────────────────────────────────────────────────────────┘
                         │
                         │ 1:N
                         ▼
┌──────────────────────────────────────────────────────────┐
│                 TRANSACTIONS TABLE                        │
├──────────────────────────────────────────────────────────┤
│  id (PK)                                                  │
│  from_account_id (FK -> users.id)                        │
│  to_account_id (FK -> users.id)                          │
│  amount                                                   │
│  memo                                                     │
│  timestamp                                                │
│  transaction_type (transfer/casino_bet/casino_win/admin) │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│                   API_KEYS TABLE                          │
├──────────────────────────────────────────────────────────┤
│  id (PK)                                                  │
│  key_value (UNIQUE)                                       │
│  description                                              │
│  created_by_user_id (FK -> users.id)                     │
│  is_active                                                │
│  created_at                                               │
│  last_used                                                │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│                  AUDIT_LOGS TABLE                         │
├──────────────────────────────────────────────────────────┤
│  id (PK)                                                  │
│  admin_user_id (FK -> users.id)                          │
│  action                                                   │
│  target_user_id (FK -> users.id)                         │
│  details                                                  │
│  timestamp                                                │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│                 CASINO_CONFIG TABLE                       │
├──────────────────────────────────────────────────────────┤
│  id (PK)                                                  │
│  game_name (glitch_grid / starlight_smuggler)            │
│  is_enabled                                               │
│  payout_percentage                                        │
│  updated_at                                               │
└──────────────────────────────────────────────────────────┘
```

---

## Data Flow

### User Registration Flow

```
Client                Server              Database
  │                     │                    │
  ├─── POST /register ──►                    │
  │     {name, pass}    │                    │
  │                     ├─── Hash password ──┤
  │                     │                    │
  │                     ├─── Generate acct# ─┤
  │                     │                    │
  │                     ├─── INSERT user ────►
  │                     │                    │
  │                     ◄──── Success ───────┤
  │                     │                    │
  ◄──── 201 Created ────┤                    │
  │   {user data}       │                    │
```

### Transaction Flow (Atomic)

```
Client              Server              Database
  │                   │                    │
  ├─── POST /tx ──────►                    │
  │   {to, amt}       │                    │
  │                   ├─── BEGIN TRANSACTION
  │                   │                    │
  │                   ├─── Check balance ──►
  │                   ◄──── balance ───────┤
  │                   │                    │
  │                   ├─── sender.bal -= amt
  │                   ├─── receiver.bal += amt
  │                   ├─── INSERT transaction
  │                   │                    │
  │                   ├─── COMMIT ─────────►
  │                   ◄──── Success ───────┤
  │                   │                    │
  ◄──── 201 ──────────┤                    │
  │   {tx data}       │                    │
```

### Casino Spin Flow

```
Client              Server              Database
  │                   │                    │
  ├─── POST /spin ────►                    │
  │   {bet_amt}       │                    │
  │                   ├─── Transfer bet ───►
  │                   │   (player → house)  │
  │                   │                    │
  │                   ├─── Generate spin ──┤
  │                   │   (server-side RNG)│
  │                   │                    │
  │                   ├─── Calculate win ──┤
  │                   │                    │
  │                   ├─── Transfer win ───►
  │                   │   (house → player)  │
  │                   │                    │
  ◄──── 200 ──────────┤                    │
  │   {reels, win}    │                    │
```

---

## Security Architecture

### Authentication Flow (JWT)

```
1. User Login
   ├─ Client sends credentials
   ├─ Server validates via bcrypt
   ├─ Server generates JWT token
   │  └─ Payload: {user_id, exp}
   └─ Client stores token (localStorage)

2. Authenticated Requests
   ├─ Client includes: Authorization: Bearer <token>
   ├─ Server validates JWT signature
   ├─ Server checks expiration
   └─ Server extracts user_id from payload

3. Token Expiry
   └─ Default: 24 hours (configurable)
```

### API Key Authentication

```
External System
   │
   ├─── HTTP Request
   │    Header: X-API-Key: <key>
   │
   ▼
Server validates:
   ├─ Key exists in database
   ├─ Key is active
   ├─ Update last_used timestamp
   └─ Process request
```

---

## Deployment Patterns

### Development (Docker Compose)

```
Host Machine
  └─ docker-compose.yml
     └─ neobank container
        ├─ Flask app (port 5000)
        ├─ SQLite DB (volume mounted)
        └─ Exposed on host:8080
```

### Production (Kubernetes)

```
Kubernetes Cluster
  └─ Namespace: neotropolis
     ├─ Ingress (external access)
     ├─ Service (load balancing)
     ├─ Deployment (2+ replicas)
     │  └─ Pods
     │     ├─ Container: neobank
     │     └─ Liveness/Readiness probes
     ├─ PersistentVolumeClaim (database)
     ├─ ConfigMap (non-sensitive config)
     └─ Secret (SECRET_KEY)
```

---

## Scaling Considerations

### Horizontal Scaling

- **Pods**: Can run multiple replicas
- **Session Affinity**: Configured on Service
- **Database**: SQLite limitations (read-heavy OK, write-heavy needs PostgreSQL)

### Vertical Scaling

```yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "250m"
  limits:
    memory: "512Mi"    # Increase for high load
    cpu: "500m"        # Increase for high load
```

### Database Migration Path

For >500 concurrent users, consider:
```
SQLite → PostgreSQL
  ├─ Change DATABASE_URL
  ├─ Use CloudNativePG operator
  └─ Update deployment to use external DB
```

---

## Monitoring & Observability

### Health Checks

```
GET /health
Response: {"status": "healthy", "service": "neobank"}
```

### Logs

```
Application logs → stdout
  ├─ Captured by Kubernetes
  └─ Viewable via: kubectl logs
```

### Metrics (Future Enhancement)

- Prometheus integration
- Grafana dashboards
- Alert on high error rates
- Track transaction volume

---

## Backup Strategy

```
┌─────────────────────────────────────┐
│  Automated Backup Schedule          │
├─────────────────────────────────────┤
│  • Daily: 2 AM (kubectl cp)         │
│  • Weekly: Full snapshot            │
│  • Retention: 30 days               │
│  • Location: S3/Azure Blob          │
└─────────────────────────────────────┘
```

---

## Disaster Recovery

1. **Database Corruption**
   - Restore from last backup
   - Replay transaction logs (if available)

2. **Pod Failure**
   - Kubernetes auto-restarts
   - Service routes to healthy pods

3. **Cluster Failure**
   - Backup database file stored externally
   - Redeploy to new cluster
   - Restore database

---

**Architecture designed for reliability, security, and scalability at LARP event scale (100-500 users)** 🌃
