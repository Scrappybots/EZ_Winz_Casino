# Build and Deployment Scripts for NeoBank

## PowerShell Scripts

### Build Container Image

```powershell
# build.ps1
param(
    [string]$Tag = "latest",
    [string]$Registry = ""
)

$ImageName = if ($Registry) { "$Registry/neobank:$Tag" } else { "neobank:$Tag" }

Write-Host "🏗️ Building container image: $ImageName" -ForegroundColor Cyan

docker build -t $ImageName -f Containerfile .

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Build successful!" -ForegroundColor Green
    
    if ($Registry) {
        Write-Host "📤 Pushing to registry..." -ForegroundColor Cyan
        docker push $ImageName
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Push successful!" -ForegroundColor Green
        } else {
            Write-Host "❌ Push failed!" -ForegroundColor Red
            exit 1
        }
    }
} else {
    Write-Host "❌ Build failed!" -ForegroundColor Red
    exit 1
}
```

Save as `build.ps1` and run:
```powershell
.\build.ps1 -Tag "v1.0.0" -Registry "your-registry.com"
```

---

### Deploy to Kubernetes

```powershell
# deploy.ps1
param(
    [switch]$Init
)

Write-Host "🚀 Deploying NeoBank to Kubernetes" -ForegroundColor Cyan

if ($Init) {
    Write-Host "📝 Initializing deployment..." -ForegroundColor Yellow
    
    # Check if secret exists
    if (-not (Test-Path "k8s\secret.yaml")) {
        Write-Host "⚠️  Creating secret from template..." -ForegroundColor Yellow
        Copy-Item "k8s\secret.yaml.template" "k8s\secret.yaml"
        
        # Generate random secret key
        $secretKey = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | ForEach-Object {[char]$_})
        
        Write-Host "🔑 Generated SECRET_KEY: $secretKey" -ForegroundColor Green
        Write-Host "⚠️  Update k8s\secret.yaml with this key!" -ForegroundColor Yellow
        
        Read-Host "Press Enter after updating secret.yaml"
    }
}

# Apply manifests
Write-Host "📦 Applying Kubernetes manifests..." -ForegroundColor Cyan

kubectl apply -f k8s\namespace.yaml
kubectl apply -f k8s\configmap.yaml
kubectl apply -f k8s\secret.yaml
kubectl apply -f k8s\deployment.yaml
kubectl apply -f k8s\service.yaml
kubectl apply -f k8s\ingress.yaml

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Deployment successful!" -ForegroundColor Green
    
    Write-Host "`n📊 Checking status..." -ForegroundColor Cyan
    kubectl get pods -n neotropolis
    kubectl get svc -n neotropolis
    
    if ($Init) {
        Write-Host "`n⚠️  Don't forget to initialize the database!" -ForegroundColor Yellow
        Write-Host "Run: kubectl exec -n neotropolis <pod-name> -- python init_db.py" -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ Deployment failed!" -ForegroundColor Red
    exit 1
}
```

Save as `deploy.ps1` and run:
```powershell
# First time deployment
.\deploy.ps1 -Init

# Subsequent deployments
.\deploy.ps1
```

---

### Database Backup

```powershell
# backup-db.ps1
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$BackupFile = "backup_$Timestamp.db"

Write-Host "💾 Creating database backup: $BackupFile" -ForegroundColor Cyan

# Get first pod name
$PodName = (kubectl get pods -n neotropolis -l app=neobank -o jsonpath='{.items[0].metadata.name}')

if ($PodName) {
    Write-Host "📥 Copying database from pod: $PodName" -ForegroundColor Yellow
    kubectl cp "neotropolis/$PodName`:/app/data/neobank.db" $BackupFile
    
    if ($LASTEXITCODE -eq 0) {
        $Size = (Get-Item $BackupFile).Length / 1KB
        Write-Host "✅ Backup successful! Size: $([math]::Round($Size, 2)) KB" -ForegroundColor Green
    } else {
        Write-Host "❌ Backup failed!" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "❌ No pods found!" -ForegroundColor Red
    exit 1
}
```

Save as `backup-db.ps1` and run:
```powershell
.\backup-db.ps1
```

---

### Local Development Setup

```powershell
# setup-dev.ps1
Write-Host "🛠️ Setting up local development environment" -ForegroundColor Cyan

# Check Python
$PythonVersion = python --version 2>&1
if ($PythonVersion -match "Python 3\.1[1-9]") {
    Write-Host "✅ Python detected: $PythonVersion" -ForegroundColor Green
} else {
    Write-Host "❌ Python 3.11+ required!" -ForegroundColor Red
    exit 1
}

# Create virtual environment
Write-Host "📦 Creating virtual environment..." -ForegroundColor Yellow
python -m venv venv

# Activate and install dependencies
Write-Host "📥 Installing dependencies..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
pip install -r requirements-dev.txt

# Initialize database
Write-Host "💾 Initializing database..." -ForegroundColor Yellow
python init_db.py

Write-Host "`n✅ Development environment ready!" -ForegroundColor Green
Write-Host "`nTo start the server:" -ForegroundColor Cyan
Write-Host "  cd backend" -ForegroundColor White
Write-Host "  python app.py" -ForegroundColor White
```

Save as `setup-dev.ps1` and run:
```powershell
.\setup-dev.ps1
```

---

## Bash Scripts (Linux/Mac)

### Build Container Image

```bash
#!/bin/bash
# build.sh

TAG=${1:-latest}
REGISTRY=${2:-}

if [ -n "$REGISTRY" ]; then
    IMAGE_NAME="$REGISTRY/neobank:$TAG"
else
    IMAGE_NAME="neobank:$TAG"
fi

echo "🏗️ Building container image: $IMAGE_NAME"

docker build -t "$IMAGE_NAME" -f Containerfile .

if [ $? -eq 0 ]; then
    echo "✅ Build successful!"
    
    if [ -n "$REGISTRY" ]; then
        echo "📤 Pushing to registry..."
        docker push "$IMAGE_NAME"
        
        if [ $? -eq 0 ]; then
            echo "✅ Push successful!"
        else
            echo "❌ Push failed!"
            exit 1
        fi
    fi
else
    echo "❌ Build failed!"
    exit 1
fi
```

Make executable and run:
```bash
chmod +x build.sh
./build.sh v1.0.0 your-registry.com
```

---

### Deploy to Kubernetes

```bash
#!/bin/bash
# deploy.sh

INIT=false
if [ "$1" == "--init" ]; then
    INIT=true
fi

echo "🚀 Deploying NeoBank to Kubernetes"

if [ "$INIT" == true ]; then
    echo "📝 Initializing deployment..."
    
    if [ ! -f "k8s/secret.yaml" ]; then
        echo "⚠️  Creating secret from template..."
        cp k8s/secret.yaml.template k8s/secret.yaml
        
        SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
        echo "🔑 Generated SECRET_KEY: $SECRET_KEY"
        echo "⚠️  Update k8s/secret.yaml with this key!"
        
        read -p "Press Enter after updating secret.yaml"
    fi
fi

echo "📦 Applying Kubernetes manifests..."

kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml

if [ $? -eq 0 ]; then
    echo "✅ Deployment successful!"
    
    echo ""
    echo "📊 Checking status..."
    kubectl get pods -n neotropolis
    kubectl get svc -n neotropolis
    
    if [ "$INIT" == true ]; then
        echo ""
        echo "⚠️  Don't forget to initialize the database!"
        echo "Run: kubectl exec -n neotropolis <pod-name> -- python init_db.py"
    fi
else
    echo "❌ Deployment failed!"
    exit 1
fi
```

Make executable and run:
```bash
chmod +x deploy.sh
./deploy.sh --init  # First time
./deploy.sh         # Subsequent deployments
```

---

## Makefile (Universal)

```makefile
# Makefile for NeoBank

.PHONY: help build run stop clean test deploy

help:
	@echo "NeoBank - Available commands:"
	@echo "  make build     - Build container image"
	@echo "  make run       - Run with docker-compose"
	@echo "  make stop      - Stop docker-compose"
	@echo "  make clean     - Remove containers and volumes"
	@echo "  make test      - Run test suite"
	@echo "  make deploy    - Deploy to Kubernetes"

build:
	docker build -t neobank:latest -f Containerfile .

run:
	docker-compose up -d

stop:
	docker-compose down

clean:
	docker-compose down -v
	docker rmi neobank:latest

test:
	pytest test_suite.py -v

deploy:
	kubectl apply -f k8s/
```

Save as `Makefile` and run:
```bash
make help
make build
make run
```
