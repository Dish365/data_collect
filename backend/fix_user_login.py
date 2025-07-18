#!/usr/bin/env python3
"""
Fix User Login Script
====================

This script fixes the login issue by resetting the password for the existing user.
"""

import os
import django
import sys

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_core.settings.development')
django.setup()

from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()

def fix_user_login():
    """Fix login credentials for kwofie user"""
    username = "kwofie"
    email = "manuel.kwofie@mcgill.ca"
    new_password = "SecurePass354!"
    
    print(f"🔧 Fixing login for user: {username}")
    print(f"📧 Email: {email}")
    
    try:
        # Find the user
        user = None
        try:
            user = User.objects.get(username=username)
            print(f"✅ Found user by username: {user.username}")
        except User.DoesNotExist:
            try:
                user = User.objects.get(email=email)
                print(f"✅ Found user by email: {user.email}")
            except User.DoesNotExist:
                print(f"❌ User not found with username '{username}' or email '{email}'")
                return False
        
        # Display current user info
        print(f"👤 Current user info:")
        print(f"   ID: {user.id}")
        print(f"   Username: {user.username}")
        print(f"   Email: {user.email}")
        print(f"   First Name: {user.first_name}")
        print(f"   Last Name: {user.last_name}")
        print(f"   Role: {user.role}")
        print(f"   Institution: {user.institution}")
        print(f"   Is Active: {user.is_active}")
        print(f"   Created: {user.created_at}")
        
        # Reset password
        print(f"🔑 Resetting password...")
        user.set_password(new_password)
        user.save()
        print(f"✅ Password reset successfully!")
        
        # Update user profile to match the setup script
        print(f"📝 Updating user profile...")
        user.first_name = "Emmanuel"
        user.last_name = "Kwofie"
        user.institution = "McGill University"
        user.save()
        print(f"✅ Profile updated successfully!")
        
        print(f"\n🎉 User fix completed!")
        print(f"   Username: {user.username}")
        print(f"   Email: {user.email}")
        print(f"   Password: {new_password}")
        print(f"   You can now run the setup script again.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error fixing user: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Fixing User Login Issue")
    print("=" * 50)
    
    success = fix_user_login()
    
    if success:
        print("\n✅ User login fix completed successfully!")
    else:
        print("\n❌ User login fix failed!") 