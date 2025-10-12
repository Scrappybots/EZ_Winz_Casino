# Architecture Comparison: SQLite vs PostgreSQL

## Before Migration (SQLite)

```
┌─────────────────────────────────────────────────────┐
│               Docker Compose / Kubernetes            │
│                                                       │
│  ┌──────────────────────────────────────────────┐   │
│  │           NeoBank Container                   │   │
│  │                                               │   │
│  │  ┌──────────────┐      ┌─────────────────┐  │   │
│  │  │   Flask App  │──────│  SQLite DB File │  │   │
│  │  │   + Frontend │      │   (neobank.db)  │  │   │
│  │  └──────────────┘      └─────────────────┘  │   │
│  │                                               │   │
│  │  [File-based storage, single container]      │   │
│  └──────────────────────────────────────────────┘   │
│                                                       │
│  Volume: neobank-data (SQLite file)                  │
└─────────────────────────────────────────────────────┘

Issues:
❌ File locking with concurrent access
❌ Can't scale horizontally (single instance only)
❌ Limited backup/restore options
❌ Not ideal for production workloads
❌ Stateful application (requires volume)
```

## After Migration (PostgreSQL)

```
┌──────────────────────────────────────────────────────────────────┐
│                  Docker Compose / Kubernetes                      │
│                                                                    │
│  ┌────────────────────────┐      ┌──────────────────────────┐   │
│  │  NeoBank Container     │      │  PostgreSQL Container     │   │
│  │  (Stateless)           │      │                           │   │
│  │                        │      │  ┌─────────────────────┐  │   │
│  │  ┌──────────────┐      │      │  │  PostgreSQL 16      │  │   │
│  │  │  Flask App   │──────┼──────┼─▶│  (neobank DB)       │  │   │
│  │  │  + Frontend  │      │      │  └─────────────────────┘  │   │
│  │  └──────────────┘      │      │           │               │   │
│  │                        │      │           ▼               │   │
│  │  [Can scale to N]      │      │  ┌─────────────────────┐  │   │
│  └────────────────────────┘      │  │  Persistent Volume  │  │   │
│           │                       │  │  (postgres-data)    │  │   │
│           │                       │  └─────────────────────┘  │   │
│           │                       │                           │   │
│           ▼                       │  [Single instance with    │   │
│  ┌────────────────────────┐      │   persistent storage]     │   │
│  │  NeoBank Container     │      │                           │   │
│  │  (Replica 2)           │      └──────────────────────────┘   │
│  │                        │                                      │
│  │  ┌──────────────┐      │      Network: Internal Service     │
│  │  │  Flask App   │──────┼──────▶ postgres-service:5432       │
│  │  │  + Frontend  │      │                                     │
│  │  └──────────────┘      │                                     │
│  │                        │                                     │
│  └────────────────────────┘                                     │
│                                                                  │
│  [Horizontal scaling enabled]                                   │
└──────────────────────────────────────────────────────────────────┘

Benefits:
✅ Proper client-server architecture
✅ Horizontal scaling (multiple app instances)
✅ Better concurrency handling
✅ Production-ready ACID transactions
✅ Standard backup/restore procedures
✅ Replication support (for HA)
✅ Better performance for complex queries
✅ Stateless application (easy to scale)
```

## Component Breakdown

### Before (SQLite)
| Component | Type | Scaling | State |
|-----------|------|---------|-------|
| Application + Database | Single Container | ❌ Vertical only | Stateful |
| Storage | File on volume | ❌ Single file | Local |
| Connections | File I/O | ❌ Limited | Locked |

### After (PostgreSQL)
| Component | Type | Scaling | State |
|-----------|------|---------|-------|
| Application | Multiple Containers | ✅ Horizontal | Stateless |
| Database | Dedicated Container | ✅ Can add replicas | Stateful |
| Storage | Persistent Volume | ✅ Network-attached | Shared |
| Connections | TCP/IP (port 5432) | ✅ Connection pooling | Concurrent |

## Deployment Comparison

### Docker Compose

**Before:**
```yaml
services:
  neobank:
    volumes:
      - neobank-data:/app/data  # SQLite file here
```

**After:**
```yaml
services:
  postgres:
    volumes:
      - postgres-data:/var/lib/postgresql/data
  
  neobank:
    depends_on:
      postgres:
        condition: service_healthy
    # No volumes needed - stateless!
```

### Kubernetes

**Before:**
```yaml
# Single deployment with PVC for SQLite file
Deployment (neobank) + PVC → Limited to 1 replica
```

**After:**
```yaml
# Separate deployments
Deployment (neobank) → Scales to N replicas
Deployment (postgres) + PVC → Database with persistent storage
Job (db-init) → One-time initialization
```

## Connection Flow

### Before (SQLite)
```
User → Ingress → Service → Pod (App) → SQLite File
                                           ↓
                                        Volume
```

### After (PostgreSQL)
```
User → Ingress → Service → Pod 1 (App) ┐
                        ├─→ Pod 2 (App) ├─→ postgres-service → Postgres Pod → Volume
                        └─→ Pod 3 (App) ┘                        (Database)
```

## Data Flow Changes

### Transaction Before (SQLite)
1. User sends request to application
2. Application opens SQLite file
3. Application writes to file (exclusive lock)
4. File is closed
5. Response sent to user

**Bottleneck:** File locking prevents concurrent writes

### Transaction After (PostgreSQL)
1. User sends request to any application pod
2. Application opens connection from pool
3. PostgreSQL handles concurrent transactions
4. MVCC ensures isolation without blocking reads
5. Response sent to user

**Advantage:** Multiple pods can write simultaneously

## Configuration Changes

### Environment Variables

**Before:**
```bash
DATABASE_URL=sqlite:///app/data/neobank.db
```

**After:**
```bash
DATABASE_URL=postgresql://neobank:password@postgres:5432/neobank
POSTGRES_USER=neobank
POSTGRES_PASSWORD=secure_password
POSTGRES_DB=neobank
```

### Health Checks

**Before:**
```dockerfile
HEALTHCHECK CMD python -c "import requests; requests.get('http://localhost:5000/health')"
```

**After:**
```dockerfile
# Application
HEALTHCHECK CMD curl -f http://localhost:5000/health

# Database (separate)
HEALTHCHECK CMD pg_isready -U neobank
```

## Scalability Comparison

### Before (SQLite)
```
Load: 100 users
├─ Single pod handles all requests
└─ SQLite file becomes bottleneck

Load: 1000 users
├─ Still single pod (can't scale)
├─ File I/O becomes saturated
└─ Performance degrades
```

### After (PostgreSQL)
```
Load: 100 users
├─ 2 pods share the load
└─ PostgreSQL handles concurrent connections

Load: 1000 users
├─ Scale to 10 pods
├─ Each pod connects to PostgreSQL
└─ Database handles pooling and concurrency
```

## Backup Strategy

### Before (SQLite)
```bash
# Copy the file
cp neobank.db neobank-backup.db

# Limitations:
- Must stop application for consistent backup
- No point-in-time recovery
- Manual process
```

### After (PostgreSQL)
```bash
# Online backup (no downtime)
pg_dump -U neobank neobank > backup.sql

# Features:
- Backup while application runs
- Point-in-time recovery (with WAL)
- Automated backup tools available
- Can backup to external storage
```

## Resource Usage

### Before (SQLite)
```
Pod: 256MB RAM, 250m CPU
└─ Application + Database in one process
└─ File I/O overhead
```

### After (PostgreSQL)
```
Application Pods (x N):
└─ 256MB RAM, 250m CPU each
└─ Stateless, can scale

Database Pod (x 1):
└─ 512MB RAM, 500m CPU
└─ Dedicated resources
└─ Better performance

Total: More resources, but better distribution
```

## Summary

| Aspect | SQLite | PostgreSQL | Winner |
|--------|--------|------------|--------|
| **Concurrency** | Limited | Excellent | PostgreSQL ✅ |
| **Scalability** | Vertical only | Horizontal + Vertical | PostgreSQL ✅ |
| **Setup Complexity** | Simple | Moderate | SQLite ✅ |
| **Production Ready** | Small scale | Enterprise grade | PostgreSQL ✅ |
| **Backup/Restore** | Basic | Advanced | PostgreSQL ✅ |
| **Performance** | Good for reads | Great for reads/writes | PostgreSQL ✅ |
| **Resource Usage** | Minimal | Moderate | SQLite ✅ |
| **High Availability** | Not supported | Supported | PostgreSQL ✅ |
| **Data Integrity** | Good | Excellent | PostgreSQL ✅ |

**Conclusion:** PostgreSQL is the clear winner for production deployments, offering better scalability, concurrency, and operational features at the cost of slightly more complexity.
