# 🎬 Getting Started - Your First 5 Minutes

Welcome to NeoBank & Chrome Slots! This guide will get you up and running in 5 minutes.

## Option 1: Quick Start with Docker (Recommended)

### Step 1: Start the Application
```powershell
# From the project root
docker-compose up --build
```

### Step 2: Wait for Startup
Look for this message:
```
neobank-app  | ✅ Database initialized successfully
neobank-app  | [INFO] Listening at: http://0.0.0.0:5000
```

### Step 3: Open Your Browser
Navigate to: **http://localhost:8080**

### Step 4: Create Your First Account
1. Click **REGISTER**
2. Enter a character name (e.g., "RunnerAlice")
3. Enter a password (min 6 characters)
4. Select a faction (optional)
5. Click **CREATE ACCOUNT**

### Step 5: Login
1. Click **LOGIN**
2. Enter your credentials
3. Click **ACCESS SYSTEM**

### 🎉 You're In!
- Your account number is displayed (e.g., NC-8A6F-4E2B)
- Your balance starts at ¤0.00
- Click **CASINO** to try the slot machines (you'll need funds first!)

---

## Option 2: Native Python (For Development)

### Step 1: Setup Environment
```powershell
# Install Python 3.11+ first from python.org

# Create virtual environment
cd backend
python -m venv venv

# Activate it
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Initialize Database
```powershell
cd ..
python init_db.py
```

### Step 3: Start Server
```powershell
cd backend
python app.py
```

### Step 4: Open Browser
Navigate to: **http://localhost:5000**

---

## 🎮 What to Try First

### 1. Fund Your Account (Admin Panel)
Since you start with ¤0, you'll need to add funds:

1. Login with admin credentials:
   - Username: `admin`
   - Password: `neotropolis2025`
2. Click **ADMIN** in the navigation
3. Search for your username
4. Click **ADJUST**
5. Enter amount: `1000`
6. Enter reason: "Initial funding"
7. Click **CONFIRM**

### 2. Make a Transfer
1. Register a second test account (or use existing)
2. Login as your first account
3. Go to **BANK** section
4. Enter recipient account number
5. Enter amount (e.g., `100`)
6. Add a memo (e.g., "Test payment")
7. Click **SEND CREDITS**

### 3. Play Glitch Grid
1. Go to **CASINO** section
2. Select **GLITCH GRID**
3. Adjust your bet using +/- buttons
4. Click **SPIN**
5. Watch the reels spin!
6. Win animations appear if you match symbols

### 4. Try Starlight Smuggler
1. Select **STARLIGHT SMUGGLER**
2. Adjust bet per line
3. Click **SPIN**
4. Check for winning paylines
5. Look for scatter bonus (🌀)

---

## 📱 Mobile Testing

1. Find your local IP:
   ```powershell
   ipconfig
   ```
2. Open on your phone: `http://YOUR_IP:8080`
3. Test touch controls and responsiveness

---

## 🔧 If Something Goes Wrong

### Database Issues
```powershell
# Reinitialize database
python init_db.py
```

### Port Already in Use
```powershell
# Change port in docker-compose.yml
ports:
  - "8081:5000"  # Use 8081 instead
```

### Container Won't Start
```powershell
# Check logs
docker-compose logs -f

# Restart from scratch
docker-compose down -v
docker-compose up --build
```

---

## 🎯 Understanding the Interface

### Bank View
```
┌─────────────────────────────┐
│    ACCOUNT BALANCE          │
│    ¤1,000.00                │ ← Your current balance
└─────────────────────────────┘

┌─────────────────────────────┐
│  CITIZEN REGISTRY           │
│  Name: RunnerAlice          │ ← Your character
│  Account: NC-8A6F-4E2B      │ ← Your account number (copy this!)
│  Faction: Runners           │
└─────────────────────────────┘

┌─────────────────────────────┐
│  TRANSFER FUNDS             │
│  Recipient: [NC-XXXX-XXXX]  │ ← Paste recipient account
│  Amount: [100.00]           │
│  Memo: [Optional note]      │
│  [SEND CREDITS]             │
└─────────────────────────────┘

┌─────────────────────────────┐
│  TRANSACTION LOG            │
│  ↓ INCOMING +¤500.00        │ ← Green = received money
│  From: Admin                │
│                             │
│  ↑ OUTGOING -¤100.00        │ ← Red = sent money
│  To: VendorBob              │
└─────────────────────────────┘
```

### Casino View
```
┌─────────────────────────────┐
│    GLITCH GRID              │
│    ┌───┐ ┌───┐ ┌───┐       │
│    │💀 │ │01 │ │🔌│       │ ← Reels
│    └───┘ └───┘ └───┘       │
│    [−] BET: ¤10 [+]         │ ← Adjust bet
│    [   S P I N   ]          │ ← Big spin button
│    WIN! 30x = ¤300.00       │ ← Win display
└─────────────────────────────┘
```

---

## 🚨 Important Notes

1. **Admin Password**: Change `neotropolis2025` immediately!
2. **Account Numbers**: Always copy/paste to avoid typos
3. **Balance**: Starts at ¤0, needs admin funding
4. **Casino**: Needs funds in account to play
5. **Memos**: Optional but helpful for tracking

---

## 📚 Next Steps

Once you're comfortable:

1. **Read API_DOCS.md** - For external integrations
2. **Read DEPLOYMENT.md** - For production deployment
3. **Read QUICKREF.md** - For quick command reference
4. **Run Tests** - `pytest test_suite.py -v`
5. **Deploy to Kubernetes** - Follow DEPLOYMENT.md

---

## 🆘 Need Help?

- Check **QUICKREF.md** for common commands
- Check **DEPLOYMENT.md** for troubleshooting
- Check logs: `docker-compose logs -f`
- Restart everything: `docker-compose down && docker-compose up --build`

---

**Welcome to Neotropolis! Your adventure in the neon-lit future starts now. 🌃**
