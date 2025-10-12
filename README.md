# 🌃 NeoBank & Chrome Slots - Neotropolis LARP Banking & Casino System

## 🎯 Overview

A self-contained, cyberpunk-themed banking and casino application for the Neotropolis LARP event. Operates with in-game currency, providing both player-facing and Game Master administrative functionalities.

## 🏗️ Architecture

- **Backend**: Python 3.11 + Flask
- **Frontend**: Vue.js 3 (mobile-first, cyberpunk UI)
- **Database**: PostgreSQL 16 (production-ready, scalable)
- **Authentication**: JWT tokens
- **API**: RESTful with API key authentication

## 🚀 Quick Start

### Local Development (Docker Compose / Podman Compose)

**Automated Setup:**
```bash
python setup_postgres.py
```

**Manual Setup:**
```bash
# Build and run
docker-compose up --build

# Or with Podman
podman-compose up --build
```

Access:
- **NeoBank**: http://localhost:8080
- **Chrome Slots**: http://localhost:8080/casino
- **Admin Panel**: http://localhost:8080/admin
- **PostgreSQL**: localhost:5432 (user: neobank, pass: neobank_dev_password)

Default GM credentials:
- Username: `admin`
- Password: `neotropolis2025` (⚠️ Change immediately!)

**📚 See [POSTGRESQL_MIGRATION.md](POSTGRESQL_MIGRATION.md) for complete PostgreSQL setup and migration guide.**

### Kubernetes Deployment

```bash
# Apply all manifests
kubectl apply -f k8s/

# Check status
kubectl get pods -n neotropolis
kubectl get svc -n neotropolis
kubectl get ingress -n neotropolis
```

## 📁 Project Structure

```
EZ_Winz_Casino/
├── backend/
│   ├── app.py              # Main Flask application
│   ├── models.py           # Database models
│   ├── auth.py             # Authentication logic
│   ├── transactions.py     # Transaction engine
│   ├── casino.py           # Slot machine logic
│   ├── admin.py            # Admin panel routes
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── index.html          # Main entry point
│   ├── js/
│   │   ├── app.js          # Vue.js main app
│   │   ├── neobank.js      # Banking components
│   │   ├── casino.js       # Casino components
│   │   └── admin.js        # Admin panel
│   └── css/
│       └── cyberpunk.css   # Cyberpunk theme
├── Containerfile           # OCI-compliant container image
├── docker-compose.yml      # Local development orchestration
├── k8s/                    # Kubernetes manifests
│   ├── namespace.yaml
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   ├── configmap.yaml
│   └── secret.yaml.template
└── init_db.py              # Database initialization script
```

## 🔐 Security Features

- Bcrypt password hashing
- JWT session management
- API key authentication for external systems
- Rate limiting on sensitive endpoints
- SQL injection protection (ORM)
- CORS configuration

## 🎰 Game Systems

### NeoBank Features
- Unique account numbers (NC-XXXX-XXXX format)
- Atomic P2P transfers
- Transaction history & search
- External API for integrations

### Chrome Slots Games

**Glitch Grid** (3-Reel Classic)
- Theme: Digital rain, glitch effects
- Symbols: Skulls, binary, network jacks, kanji
- Single payline, Wild symbols

**Starlight Smuggler** (5-Reel Multi-line)
- Theme: Gritty sci-fi, spaceships
- Symbols: Freighters, blasters, alien gems
- 9 paylines, Scatter bonus (5 free spins)

## 🛠️ Configuration

Environment variables (via ConfigMap/Secrets in K8s):

```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///neobank.db
CASINO_HOUSE_ACCOUNT=NC-CASA-0000
JWT_EXPIRY_HOURS=24
RATE_LIMIT_PER_MINUTE=60
```

## 📊 API Documentation

### External Transaction API

**Create Transaction**
```http
POST /api/v1/transactions
Content-Type: application/json
X-API-Key: your_api_key

{
  "from_account": "NC-8A6F-4E2B",
  "to_account": "NC-1B2C-3D4E",
  "amount": 100.50,
  "memo": "Payment for services"
}
```

**Check Balance**
```http
GET /api/v1/account/NC-8A6F-4E2B/balance
X-API-Key: your_api_key
```

## 🎮 Admin Panel Features

- User lookup & management
- Password resets
- Manual account adjustments (with audit log)
- Global transaction viewer
- API key management
- Casino payout controls
- Game enable/disable toggles

## 📱 Mobile Optimization

- Responsive design (mobile-first)
- Touch-optimized controls
- Lightweight assets
- Works on spotty cellular connections
- PWA-ready (optional offline support)

## 🎨 Theming

Dark mode cyberpunk aesthetic:
- Electric blue (#00F0FF)
- Magenta (#FF00FF)
- Dark purple (#1A0033)
- Chrome/silver accents
- Glitch effects & animations

## 🧪 Testing

```bash
# Run backend tests
cd backend
pytest

# Run integration tests
python test_suite.py
```

## 📝 License

Custom license for Neotropolis LARP event. Not for commercial use.

## 🆘 Support

For issues during the event, contact the Tech Team via in-game radio or Discord.

---

**Built with ❤️ for Neotropolis 2025**
