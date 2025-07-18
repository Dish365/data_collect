#!/usr/bin/env python3
"""
Setup script to initialize Django database for FastAPI analytics backend.
"""

import os
import sys
import subprocess
from pathlib import Path

def setup_django_database():
    """Setup Django database with proper migrations"""
    print("🗄️  Setting up Django Database")
    print("=" * 40)
    
    # Navigate to backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    print(f"Working in: {os.getcwd()}")
    
    # Set Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_core.settings.development')
    
    try:
        # Check if database exists
        db_file = backend_dir / 'db.sqlite3'
        if db_file.exists():
            print(f"📋 Database file exists: {db_file}")
        else:
            print(f"📋 Database file not found, will create: {db_file}")
        
        # Run migrations
        print("\n🔄 Running Django migrations...")
        result = subprocess.run([
            sys.executable, 'manage.py', 'migrate'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Django migrations completed successfully")
            print(result.stdout)
        else:
            print("❌ Django migrations failed")
            print(result.stderr)
            return False
        
        # Create superuser if needed (optional)
        print("\n👤 Checking for Django superuser...")
        check_superuser = subprocess.run([
            sys.executable, 'manage.py', 'shell', '-c',
            'from django.contrib.auth import get_user_model; User = get_user_model(); print("Superuser exists:", User.objects.filter(is_superuser=True).exists())'
        ], capture_output=True, text=True)
        
        if "Superuser exists: False" in check_superuser.stdout:
            print("ℹ️  No superuser found. You may want to create one later with:")
            print("   python manage.py createsuperuser")
        else:
            print("✅ Superuser exists")
        
        # Test database connection
        print("\n🔌 Testing database connection...")
        test_db = subprocess.run([
            sys.executable, 'manage.py', 'shell', '-c',
            'from django.db import connection; print("Database connection:", connection.ensure_connection() or "OK")'
        ], capture_output=True, text=True)
        
        if test_db.returncode == 0:
            print("✅ Database connection successful")
        else:
            print("❌ Database connection failed")
            print(test_db.stderr)
            return False
        
        # Check for sample data
        print("\n📊 Checking for sample data...")
        check_data = subprocess.run([
            sys.executable, 'manage.py', 'shell', '-c',
            '''
from projects.models import Project
from responses.models import Response
print(f"Projects: {Project.objects.count()}")
print(f"Responses: {Response.objects.count()}")
            '''
        ], capture_output=True, text=True)
        
        if check_data.returncode == 0:
            print("✅ Sample data check completed")
            print(check_data.stdout)
        else:
            print("⚠️  Sample data check failed (this is probably OK)")
            print(check_data.stderr)
        
        return True
        
    except Exception as e:
        print(f"❌ Django database setup failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Django Database Setup for Analytics Backend")
    print("=" * 50)
    
    if setup_django_database():
        print("\n🎉 Django database setup completed successfully!")
        print("You can now run the FastAPI analytics backend with:")
        print("  cd fastapi")
        print("  python start_analytics_backend.py")
        return True
    else:
        print("\n❌ Django database setup failed!")
        print("Please check the error messages above and try again.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 