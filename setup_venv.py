#!/usr/bin/env python3
"""
GPS Spoofing Campaign Manager - Virtual Environment Setup
Automated setup script for creating and configuring the Python virtual environment
"""

import os
import sys
import subprocess
import venv
from pathlib import Path

def run_command(command, cwd=None):
    """Run a command and return success status"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd,
            capture_output=True, 
            text=True,
            check=True
        )
        print(f"✅ {command}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {command}")
        print(f"Error: {e.stderr}")
        return False

def setup_virtual_environment():
    """Create and setup virtual environment"""
    project_root = Path(__file__).parent
    venv_path = project_root / ".venv"
    
    print("🚀 Setting up GPS Spoofing Campaign Manager...")
    print(f"Project root: {project_root}")
    
    # Check if .venv already exists
    if venv_path.exists():
        print("⚠️  Virtual environment already exists")
        response = input("Do you want to recreate it? (y/N): ").lower()
        if response != 'y':
            print("Skipping virtual environment creation")
            return True
        
        # Remove existing venv
        import shutil
        shutil.rmtree(venv_path)
        print("🗑️  Removed existing virtual environment")
    
    # Create virtual environment
    print("📦 Creating virtual environment...")
    try:
        venv.create(venv_path, with_pip=True)
        print("✅ Virtual environment created successfully")
    except Exception as e:
        print(f"❌ Failed to create virtual environment: {e}")
        return False
    
    # Determine activation script and pip path based on OS
    if sys.platform == "win32":
        activate_script = venv_path / "Scripts" / "activate"
        pip_path = venv_path / "Scripts" / "pip"
        python_path = venv_path / "Scripts" / "python"
    else:
        activate_script = venv_path / "bin" / "activate"
        pip_path = venv_path / "bin" / "pip"
        python_path = venv_path / "bin" / "python"
    
    # Upgrade pip
    print("⬆️  Upgrading pip...")
    if not run_command(f'"{python_path}" -m pip install --upgrade pip'):
        return False
    
    # Install requirements
    print("📋 Installing requirements...")
    if not run_command(f'"{pip_path}" install -r requirements.txt'):
        return False
    
    # Create .env file if it doesn't exist
    env_file = project_root / ".env"
    if not env_file.exists():
        print("📝 Creating .env file...")
        env_content = """# GPS Spoofing Campaign Manager - Environment Configuration

# Server Configuration
HOST=0.0.0.0
PORT=5002
DEBUG=False

# Security
SECRET_KEY=your-secret-key-here-change-in-production
JWT_SECRET_KEY=your-jwt-secret-key-here-change-in-production

# CORS Origins (comma-separated)
CORS_ORIGINS=*

# Logging
LOG_LEVEL=INFO

# Database (SQLite)
# DATABASE_PATH is automatically set to campaigns.db in project root

# Android ADB (ensure ADB is in your PATH)
# ADB_PATH=/path/to/adb
"""
        with open(env_file, 'w') as f:
            f.write(env_content)
        print("✅ .env file created")
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print(f"1. Activate virtual environment:")
    if sys.platform == "win32":
        print(f"   {venv_path}\\Scripts\\activate")
    else:
        print(f"   source {venv_path}/bin/activate")
    
    print(f"2. Update {env_file} with your configuration")
    print("3. Run the application:")
    print("   python gps_campaign_manager_v3.py")
    print("   # OR")
    print("   cd gps_campaign_manager && python run.py")
    
    print(f"\n🌐 Access the dashboard at: http://localhost:5002")
    
    return True

def main():
    """Main setup function"""
    print("=" * 60)
    print("GPS Spoofing Campaign Manager - Virtual Environment Setup")
    print("=" * 60)
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    
    print(f"✅ Python version: {sys.version}")
    
    # Run setup
    success = setup_virtual_environment()
    
    if success:
        print("\n🎯 Setup completed successfully!")
        print("📖 See README.md for detailed usage instructions")
    else:
        print("\n❌ Setup failed. Please check the error messages above.")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
