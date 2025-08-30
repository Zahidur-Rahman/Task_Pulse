#!/usr/bin/env python3
"""
Simple Admin Setup Script for Task Pulse
This script creates the first admin user for the system.
"""

import asyncio
import sys
from pathlib import Path

# Add the backend directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from db.session import init_db, get_db
from db.repository.user import user_repository
from schemas.user import UserCreate
from db.models.user import UserRole
from sqlalchemy import select, func
from db.models.user import User


async def setup_first_admin():
    """Setup the first admin user for the system."""
    
    print("🚀 Task Pulse - First Admin Setup")
    print("=" * 40)
    
    try:
        # Initialize database
        print("📊 Initializing database...")
        await init_db()
        
        # Check if admin already exists
        async for db in get_db():
            admin_count = await db.execute(
                select(func.count(User.id)).filter(User.role == UserRole.admin)
            )
            total_admins = admin_count.scalar()
            
            if total_admins > 0:
                print("❌ Admin user already exists!")
                print(f"   Found {total_admins} admin user(s)")
                return
            
            print("✅ No admin users found. Proceeding with setup...")
            
            # Get admin details
            print("\n📝 Please provide admin details:")
            email = input("Email: ").strip()
            password = input("Password: ").strip()
            first_name = input("First Name: ").strip()
            last_name = input("Last Name: ").strip()
            
            if not all([email, password, first_name, last_name]):
                print("❌ All fields are required!")
                return
            
            # Confirm details
            print(f"\n📋 Admin Details:")
            print(f"   Email: {email}")
            print(f"   Name: {first_name} {last_name}")
            print(f"   Role: Admin")
            
            confirm = input("\n🤔 Proceed with creating admin? (y/N): ").strip().lower()
            if confirm not in ['y', 'yes']:
                print("❌ Setup cancelled.")
                return
            
            # Create admin user
            print("\n🔐 Creating admin user...")
            admin_data = UserCreate(
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role=UserRole.admin
            )
            
            admin = await user_repository.create_new_user(admin_data, db)
            
            print("\n🎉 Admin user created successfully!")
            print("=" * 40)
            print(f"   ID: {admin.id}")
            print(f"   Email: {admin.email}")
            print(f"   Name: {admin.first_name} {admin.last_name}")
            print(f"   Role: {admin.role}")
            print(f"   Created: {admin.created_at}")
            print("=" * 40)
            
            print("\n✅ Setup complete! You can now:")
            print("   1. Start the backend server: python main.py")
            print("   2. Login to the admin dashboard")
            print("   3. Create additional users through the web interface")
            
    except Exception as e:
        print(f"❌ Error during setup: {str(e)}")
        print("\n💡 Troubleshooting:")
        print("   1. Make sure the database is running")
        print("   2. Check your .env file configuration")
        print("   3. Ensure all dependencies are installed")
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(setup_first_admin()) 