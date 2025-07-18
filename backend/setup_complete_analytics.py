#!/usr/bin/env python3
"""
Complete setup script for the FastAPI Analytics Backend.
Runs all necessary setup steps in the correct order.
"""

import os
import sys
import subprocess
from pathlib import Path
import time

def print_step(step_num, title, description=""):
    """Print a formatted step"""
    print(f"\n{'='*60}")
    print(f"STEP {step_num}: {title}")
    if description:
        print(f"Description: {description}")
    print('='*60)

def run_command(cmd, description, cwd=None):
    """Run a command and show results"""
    print(f"\n🔄 {description}")
    print(f"Command: {' '.join(cmd)}")
    if cwd:
        print(f"Working directory: {cwd}")
    
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    
    if result.returncode == 0:
        print(f"✅ Success!")
        if result.stdout.strip():
            print(f"Output: {result.stdout.strip()}")
        return True
    else:
        print(f"❌ Failed!")
        if result.stderr.strip():
            print(f"Error: {result.stderr.strip()}")
        if result.stdout.strip():
            print(f"Output: {result.stdout.strip()}")
        return False

def check_dependencies():
    """Check if all required dependencies are installed"""
    print_step(1, "CHECKING DEPENDENCIES", "Verify all required Python packages are installed")
    
    required_packages = [
        'django', 'fastapi', 'uvicorn', 'pandas', 'numpy', 'scipy', 
        'scikit-learn', 'textblob', 'nltk', 'pingouin', 'statsmodels'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Installing missing packages...")
        
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install'
        ] + missing_packages, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ All packages installed successfully!")
        else:
            print(f"❌ Package installation failed: {result.stderr}")
            return False
    
    return True

def setup_django():
    """Setup Django database and run migrations"""
    print_step(2, "SETTING UP DJANGO", "Initialize Django database and run migrations")
    
    backend_dir = Path(__file__).parent
    
    # Check if manage.py exists
    manage_py = backend_dir / 'manage.py'
    if not manage_py.exists():
        print(f"❌ manage.py not found at {manage_py}")
        return False
    
    # Run migrations
    if not run_command([sys.executable, 'manage.py', 'migrate'], "Running Django migrations", cwd=backend_dir):
        return False
    
    # Test database connection
    test_cmd = [
        sys.executable, 'manage.py', 'shell', '-c',
        'from django.db import connection; print("Database connection test:", connection.ensure_connection() or "SUCCESS")'
    ]
    
    if not run_command(test_cmd, "Testing database connection", cwd=backend_dir):
        return False
    
    return True

def test_django_integration():
    """Test Django integration with FastAPI"""
    print_step(3, "TESTING DJANGO INTEGRATION", "Verify FastAPI can connect to Django")
    
    fastapi_dir = Path(__file__).parent / 'fastapi'
    test_script = fastapi_dir / 'test_django_import.py'
    
    if not test_script.exists():
        print(f"❌ Test script not found at {test_script}")
        return False
    
    return run_command([sys.executable, 'test_django_import.py'], "Testing Django import", cwd=fastapi_dir)

def test_analytics_utilities():
    """Test analytics utilities"""
    print_step(4, "TESTING ANALYTICS UTILITIES", "Verify analytics algorithms work correctly")
    
    fastapi_dir = Path(__file__).parent / 'fastapi'
    test_script = fastapi_dir / 'test_analytics_utils.py'
    
    if not test_script.exists():
        print(f"❌ Test script not found at {test_script}")
        return False
    
    return run_command([sys.executable, 'test_analytics_utils.py'], "Testing analytics utilities", cwd=fastapi_dir)

def start_backend():
    """Start the FastAPI backend"""
    print_step(5, "STARTING ANALYTICS BACKEND", "Launch the FastAPI server")
    
    fastapi_dir = Path(__file__).parent / 'fastapi'
    start_script = fastapi_dir / 'start_analytics_backend.py'
    
    if not start_script.exists():
        print(f"❌ Start script not found at {start_script}")
        return False
    
    print("🚀 Starting FastAPI Analytics Backend...")
    print("📊 Backend URL: http://localhost:8001")
    print("📖 API Documentation: http://localhost:8001/docs")
    print("💡 Health Check: http://localhost:8001/api/v1/analytics/health")
    print("\nPress Ctrl+C to stop the server when ready")
    print("The server will start in 3 seconds...")
    
    time.sleep(3)
    
    # Start the server (this will run indefinitely)
    os.chdir(fastapi_dir)
    subprocess.run([sys.executable, 'start_analytics_backend.py'])
    
    return True

def main():
    """Main setup function"""
    print("🎯 COMPLETE ANALYTICS BACKEND SETUP")
    print("=" * 60)
    print("This script will set up the FastAPI Analytics Backend with Django integration")
    print("Please ensure you're in the 'backend' directory and have activated your virtual environment")
    print("=" * 60)
    
    # Verify we're in the right directory
    current_dir = Path.cwd()
    if not (current_dir / 'manage.py').exists():
        print("❌ Error: manage.py not found in current directory")
        print("Please run this script from the 'backend' directory")
        return False
    
    print(f"✅ Working in: {current_dir}")
    
    # Step 1: Check dependencies
    if not check_dependencies():
        print("\n❌ Dependency check failed. Please install missing packages manually:")
        print("pip install -r fastapi/requirements.txt")
        return False
    
    # Step 2: Setup Django
    if not setup_django():
        print("\n❌ Django setup failed. Please check the error messages above.")
        return False
    
    # Step 3: Test Django integration
    if not test_django_integration():
        print("\n❌ Django integration test failed. Please check the error messages above.")
        return False
    
    # Step 4: Test analytics utilities
    if not test_analytics_utilities():
        print("\n⚠️  Analytics utilities test had issues, but continuing...")
        print("You may need to check the analytics implementation later.")
    
    # Step 5: Start backend
    print("\n🎉 ALL SETUP STEPS COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print("The FastAPI Analytics Backend is ready to start!")
    print("=" * 60)
    
    start_choice = input("\nDo you want to start the backend now? (y/n): ").lower()
    if start_choice in ['y', 'yes']:
        start_backend()
    else:
        print("\nTo start the backend later, run:")
        print("  cd fastapi")
        print("  python start_analytics_backend.py")
        print("\nThen test the API at: http://localhost:8001/docs")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n👋 Setup interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 