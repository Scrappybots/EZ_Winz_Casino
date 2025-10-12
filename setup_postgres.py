#!/usr/bin/env python3
"""
Quick setup script for local PostgreSQL development
"""
import subprocess
import sys
import time

def run_command(cmd, description, check=True):
    """Run a shell command"""
    print(f"\n🔧 {description}...")
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            check=check,
            capture_output=True,
            text=True
        )
        if result.stdout:
            print(result.stdout)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stderr:
            print(e.stderr)
        return False

def main():
    print("🚀 NeoBank PostgreSQL Setup")
    print("=" * 50)
    
    # Check if podman or docker is available
    has_podman = run_command("podman --version", "Checking for Podman", check=False)
    has_docker = run_command("docker --version", "Checking for Docker", check=False)
    
    if not has_podman and not has_docker:
        print("\n❌ Neither Podman nor Docker found. Please install one of them.")
        sys.exit(1)
    
    compose_cmd = "podman compose" if has_podman else "docker-compose"
    print(f"\n✅ Using: {compose_cmd}")
    
    # Stop any existing services
    print("\n🛑 Stopping existing services...")
    run_command(f"{compose_cmd} down", "Stopping services", check=False)
    
    # Build images
    if not run_command(f"{compose_cmd} build", "Building container images"):
        print("\n❌ Build failed!")
        sys.exit(1)
    
    # Start services
    if not run_command(f"{compose_cmd} up -d", "Starting services"):
        print("\n❌ Failed to start services!")
        sys.exit(1)
    
    print("\n⏳ Waiting for services to be ready...")
    time.sleep(5)
    
    # Check service status
    run_command(f"{compose_cmd} ps", "Service status")
    
    print("\n" + "=" * 50)
    print("✅ Setup complete!")
    print("\n📋 Service URLs:")
    print("   • Web UI: http://localhost:8080")
    print("   • API: http://localhost:8080/api/v1/")
    print("   • PostgreSQL: localhost:5432")
    print("\n📝 Default credentials:")
    print("   • Username: admin")
    print("   • Password: neotropolis2025")
    print("\n🔍 View logs:")
    print(f"   {compose_cmd} logs -f")
    print("\n🛑 Stop services:")
    print(f"   {compose_cmd} down")
    print("=" * 50)

if __name__ == '__main__':
    main()
