#!/usr/bin/env python3
"""
Quick Start Script for NeoBank & Chrome Slots
Handles initial setup and provides helpful commands
"""

import os
import sys
import subprocess
import platform

def print_banner():
    banner = """
    ╔═══════════════════════════════════════════════╗
    ║                                               ║
    ║   🌃 NEOTROPOLIS - NEOBANK & CHROME SLOTS    ║
    ║                                               ║
    ╚═══════════════════════════════════════════════╝
    """
    print(banner)

def check_docker():
    """Check if Docker or Podman is available"""
    try:
        subprocess.run(['docker', '--version'], capture_output=True, check=True)
        return 'docker'
    except (subprocess.CalledProcessError, FileNotFoundError):
        try:
            subprocess.run(['podman', '--version'], capture_output=True, check=True)
            return 'podman'
        except (subprocess.CalledProcessError, FileNotFoundError):
            return None

def check_python():
    """Check Python version"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 11:
        return True
    return False

def main():
    print_banner()
    
    print("🔍 Checking prerequisites...\n")
    
    # Check for container runtime
    container_runtime = check_docker()
    if container_runtime:
        print(f"✅ {container_runtime.capitalize()} detected")
    else:
        print("❌ Docker or Podman not found")
    
    # Check Python version
    if check_python():
        print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    else:
        print(f"⚠️  Python 3.11+ recommended (you have {sys.version_info.major}.{sys.version_info.minor})")
    
    print("\n" + "="*50)
    print("🚀 QUICK START OPTIONS")
    print("="*50 + "\n")
    
    print("1️⃣  Run with Docker Compose (Recommended)")
    if platform.system() == "Windows":
        print("    docker-compose up --build")
    else:
        print("    $ docker-compose up --build")
    print("    Access: http://localhost:8080\n")
    
    print("2️⃣  Run with Podman Compose")
    if platform.system() == "Windows":
        print("    podman-compose up --build")
    else:
        print("    $ podman-compose up --build")
    print("    Access: http://localhost:8080\n")
    
    print("3️⃣  Run locally (Development)")
    if platform.system() == "Windows":
        print("    cd backend")
        print("    python -m venv venv")
        print("    .\\venv\\Scripts\\Activate.ps1")
        print("    pip install -r requirements.txt")
        print("    cd ..")
        print("    python init_db.py")
        print("    cd backend")
        print("    python app.py")
    else:
        print("    $ cd backend")
        print("    $ python3 -m venv venv")
        print("    $ source venv/bin/activate")
        print("    $ pip install -r requirements.txt")
        print("    $ cd ..")
        print("    $ python init_db.py")
        print("    $ cd backend")
        print("    $ python app.py")
    print("    Access: http://localhost:5000\n")
    
    print("4️⃣  Deploy to Kubernetes")
    print("    See DEPLOYMENT.md for detailed instructions\n")
    
    print("="*50)
    print("📚 DOCUMENTATION")
    print("="*50 + "\n")
    print("• README.md      - Project overview")
    print("• DEPLOYMENT.md  - Deployment guide")
    print("• API_DOCS.md    - API documentation")
    print()
    
    print("="*50)
    print("🔐 DEFAULT CREDENTIALS")
    print("="*50 + "\n")
    print("Admin Panel:")
    print("  Username: admin")
    print("  Password: neotropolis2025")
    print("  ⚠️  Change immediately in production!\n")
    
    print("="*50)
    print("🆘 NEED HELP?")
    print("="*50 + "\n")
    print("Check the README.md for troubleshooting tips")
    print("or contact the development team.\n")
    
    print("Built with ❤️ for Neotropolis 2025 🌃\n")

if __name__ == '__main__':
    main()
