#!/usr/bin/env python3
"""
Task Pulse Management CLI
A comprehensive command-line interface for managing the Task Pulse system.
"""

import asyncio
import click
import os
import sys
from pathlib import Path
from typing import Optional
import json

# Add the backend directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from db.session import get_db, init_db, check_db_connection
from db.repository.user import user_repository
from schemas.user import UserCreate
from core.hashing import Hasher
from db.models.user import UserRole
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from db.models.user import User


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """Task Pulse Management CLI - Manage your Task Pulse system from the command line."""
    pass


@cli.command()
@click.option('--email', prompt='Admin email', help='Email address for the admin user')
@click.option('--password', prompt='Admin password', hide_input=True, confirmation_prompt=True, help='Password for the admin user')
@click.option('--first-name', prompt='First name', help='First name of the admin user')
@click.option('--last-name', prompt='Last name', help='Last name of the admin user')
@click.option('--force', is_flag=True, help='Force creation even if admin exists')
def create_admin(email: str, password: str, first_name: str, last_name: str, force: bool):
    """Create the first admin user for the system."""
    
    async def _create_admin():
        try:
            # Initialize database
            await init_db()
            
            # Check if admin already exists
            async for db in get_db():
                admin_count = await db.execute(
                    select(func.count(User.id)).filter(User.role == UserRole.admin)
                )
                total_admins = admin_count.scalar()
                
                if total_admins > 0 and not force:
                    click.echo("❌ Admin user already exists! Use --force to create another admin.")
                    return
                
                # Create admin user
                admin_data = UserCreate(
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    role=UserRole.admin
                )
                
                admin = await user_repository.create_new_user(admin_data, db)
                
                click.echo("✅ Admin user created successfully!")
                click.echo(f"   Email: {admin.email}")
                click.echo(f"   Name: {admin.first_name} {admin.last_name}")
                click.echo(f"   Role: {admin.role}")
                click.echo(f"   ID: {admin.id}")
                
                if total_admins == 0:
                    click.echo("\n🎉 This is the first admin user (Super Admin)!")
                    click.echo("   You can now promote other users to admin using the promotion system.")
                
        except Exception as e:
            click.echo(f"❌ Error creating admin: {str(e)}")
            sys.exit(1)
    
    asyncio.run(_create_admin())


@cli.command()
@click.option('--email', prompt='User email', help='Email address for the user')
@click.option('--password', prompt='User password', hide_input=True, confirmation_prompt=True, help='Password for the user')
@click.option('--first-name', prompt='First name', help='First name of the user')
@click.option('--last-name', prompt='Last name', help='Last name of the user')
@click.option('--role', type=click.Choice(['user', 'manager', 'admin']), default='user', help='Role for the user')
def create_user(email: str, password: str, first_name: str, last_name: str, role: str):
    """Create a new user in the system."""
    
    async def _create_user():
        try:
            await init_db()
            
            async for db in get_db():
                # Check if user already exists
                existing_user = await user_repository.get_user_by_email(email, db)
                if existing_user:
                    click.echo(f"❌ User with email {email} already exists!")
                    return
                
                # Create user
                user_data = UserCreate(
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                    role=UserRole(role)
                )
                
                user = await user_repository.create_new_user(user_data, db)
                
                click.echo("✅ User created successfully!")
                click.echo(f"   Email: {user.email}")
                click.echo(f"   Name: {user.first_name} {user.last_name}")
                click.echo(f"   Role: {user.role}")
                click.echo(f"   ID: {user.id}")
                
        except Exception as e:
            click.echo(f"❌ Error creating user: {str(e)}")
            sys.exit(1)
    
    asyncio.run(_create_user())


@cli.command()
@click.option('--email', prompt='User email', help='Email of the user to promote')
@click.option('--new-role', type=click.Choice(['manager', 'admin']), prompt='New role', help='New role for the user')
def promote_user(email: str, new_role: str):
    """Promote a user to a higher role."""
    
    async def _promote_user():
        try:
            await init_db()
            
            async for db in get_db():
                # Find user
                user = await user_repository.get_user_by_email(email, db)
                if not user:
                    click.echo(f"❌ User with email {email} not found!")
                    return
                
                if user.role == UserRole(new_role):
                    click.echo(f"❌ User {email} is already a {new_role}!")
                    return
                
                # Update user role
                update_data = {"role": UserRole(new_role)}
                updated_user = await user_repository.update_user(user.id, update_data, db)
                
                click.echo("✅ User promoted successfully!")
                click.echo(f"   Email: {updated_user.email}")
                click.echo(f"   New Role: {updated_user.role}")
                
        except Exception as e:
            click.echo(f"❌ Error promoting user: {str(e)}")
            sys.exit(1)
    
    asyncio.run(_promote_user())


@cli.command()
@click.option('--email', help='Filter by email (partial match)')
@click.option('--role', type=click.Choice(['user', 'manager', 'admin']), help='Filter by role')
@click.option('--active', type=click.Choice(['true', 'false']), help='Filter by active status')
def list_users(email: Optional[str], role: Optional[str], active: Optional[str]):
    """List all users in the system with optional filtering."""
    
    async def _list_users():
        try:
            await init_db()
            
            async for db in get_db():
                # Build filters
                filters = {}
                if email:
                    filters['email'] = email
                if role:
                    filters['role'] = UserRole(role)
                if active is not None:
                    filters['is_active'] = active.lower() == 'true'
                
                # Get users
                users = await user_repository.get_all_users_with_filters(
                    db, skip=0, limit=1000, **filters
                )
                
                if not users:
                    click.echo("No users found matching the criteria.")
                    return
                
                click.echo(f"Found {len(users)} user(s):")
                click.echo("-" * 80)
                
                for user in users:
                    status = "🟢 Active" if user.is_active else "🔴 Inactive"
                    click.echo(f"ID: {user.id}")
                    click.echo(f"Name: {user.first_name} {user.last_name}")
                    click.echo(f"Email: {user.email}")
                    click.echo(f"Role: {user.role}")
                    click.echo(f"Status: {status}")
                    click.echo(f"Created: {user.created_at}")
                    click.echo("-" * 80)
                
        except Exception as e:
            click.echo(f"❌ Error listing users: {str(e)}")
            sys.exit(1)
    
    asyncio.run(_list_users())


@cli.command()
@click.option('--email', prompt='User email', help='Email of the user to deactivate')
@click.option('--confirm', is_flag=True, help='Skip confirmation prompt')
def deactivate_user(email: str, confirm: bool):
    """Deactivate a user account."""
    
    if not confirm:
        if not click.confirm(f"Are you sure you want to deactivate user {email}?"):
            click.echo("Operation cancelled.")
            return
    
    async def _deactivate_user():
        try:
            await init_db()
            
            async for db in get_db():
                # Find user
                user = await user_repository.get_user_by_email(email, db)
                if not user:
                    click.echo(f"❌ User with email {email} not found!")
                    return
                
                if not user.is_active:
                    click.echo(f"❌ User {email} is already deactivated!")
                    return
                
                # Deactivate user
                success = await user_repository.deactivate_user(user.id, db)
                
                if success:
                    click.echo(f"✅ User {email} has been deactivated successfully!")
                else:
                    click.echo(f"❌ Failed to deactivate user {email}")
                
        except Exception as e:
            click.echo(f"❌ Error deactivating user: {str(e)}")
            sys.exit(1)
    
    asyncio.run(_deactivate_user())


@cli.command()
def check_db():
    """Check database connection and health."""
    
    async def _check_db():
        try:
            await init_db()
            
            if await check_db_connection():
                click.echo("✅ Database connection successful!")
                
                # Get some basic stats
                async for db in get_db():
                    # Count users
                    user_count = await db.execute(select(func.count(User.id)))
                    total_users = user_count.scalar()
                    
                    # Count admins
                    admin_count = await db.execute(
                        select(func.count(User.id)).filter(User.role == UserRole.admin)
                    )
                    total_admins = admin_count.scalar()
                    
                    click.echo(f"   Total Users: {total_users}")
                    click.echo(f"   Total Admins: {total_admins}")
                    
            else:
                click.echo("❌ Database connection failed!")
                sys.exit(1)
                
        except Exception as e:
            click.echo(f"❌ Database check error: {str(e)}")
            sys.exit(1)
    
    asyncio.run(_check_db())


@cli.command()
@click.option('--count', default=5, help='Number of demo users to create')
def seed_demo_data(count: int):
    """Create demo data for testing purposes."""
    
    async def _seed_demo_data():
        try:
            await init_db()
            
            async for db in get_db():
                # Check if demo data already exists
                existing_users = await db.execute(select(func.count(User.id)))
                if existing_users.scalar() > 0:
                    if not click.confirm("Demo data already exists. Continue anyway?"):
                        return
                
                # Create demo users
                demo_users = [
                    {
                        "email": "john.doe@example.com",
                        "password": "DemoPass123",
                        "first_name": "John",
                        "last_name": "Doe",
                        "role": UserRole.user
                    },
                    {
                        "email": "jane.smith@example.com",
                        "password": "DemoPass123",
                        "first_name": "Jane",
                        "last_name": "Smith",
                        "role": UserRole.manager
                    },
                    {
                        "email": "bob.wilson@example.com",
                        "password": "DemoPass123",
                        "first_name": "Bob",
                        "last_name": "Wilson",
                        "role": UserRole.user
                    },
                    {
                        "email": "alice.johnson@example.com",
                        "password": "DemoPass123",
                        "first_name": "Alice",
                        "last_name": "Johnson",
                        "role": UserRole.user
                    },
                    {
                        "email": "charlie.brown@example.com",
                        "password": "DemoPass123",
                        "first_name": "Charlie",
                        "last_name": "Brown",
                        "role": UserRole.manager
                    }
                ]
                
                created_count = 0
                for user_data in demo_users[:count]:
                    try:
                        user = await user_repository.create_new_user(
                            UserCreate(**user_data), db
                        )
                        created_count += 1
                        click.echo(f"✅ Created demo user: {user.email}")
                    except Exception as e:
                        click.echo(f"⚠️  Skipped {user_data['email']}: {str(e)}")
                
                click.echo(f"\n🎉 Successfully created {created_count} demo users!")
                click.echo("   Default password for all demo users: DemoPass123")
                
        except Exception as e:
            click.echo(f"❌ Error seeding demo data: {str(e)}")
            sys.exit(1)
    
    asyncio.run(_seed_demo_data())


@cli.command()
def system_info():
    """Display system information and status."""
    
    async def _system_info():
        try:
            await init_db()
            
            click.echo("🔍 Task Pulse System Information")
            click.echo("=" * 50)
            
            # Database status
            if await check_db_connection():
                click.echo("✅ Database: Connected")
            else:
                click.echo("❌ Database: Disconnected")
                return
            
            # System stats
            async for db in get_db():
                # User statistics
                total_users = await db.execute(select(func.count(User.id)))
                total_users = total_users.scalar()
                
                admin_users = await db.execute(
                    select(func.count(User.id)).filter(User.role == UserRole.admin)
                )
                admin_users = admin_users.scalar()
                
                manager_users = await db.execute(
                    select(func.count(User.id)).filter(User.role == UserRole.manager)
                )
                manager_users = manager_users.scalar()
                
                regular_users = await db.execute(
                    select(func.count(User.id)).filter(User.role == UserRole.user)
                )
                regular_users = regular_users.scalar()
                
                active_users = await db.execute(
                    select(func.count(User.id)).filter(User.is_active == True)
                )
                active_users = active_users.scalar()
                
                click.echo(f"👥 Total Users: {total_users}")
                click.echo(f"   🟢 Active: {active_users}")
                click.echo(f"   🔴 Inactive: {total_users - active_users}")
                click.echo(f"   👑 Admins: {admin_users}")
                click.echo(f"   👨‍💼 Managers: {manager_users}")
                click.echo(f"   👤 Regular Users: {regular_users}")
                
                # Check if system is properly set up
                if admin_users == 0:
                    click.echo("\n⚠️  WARNING: No admin users found!")
                    click.echo("   Run 'python manage.py create-admin' to create the first admin.")
                elif admin_users == 1:
                    click.echo("\n✅ System properly configured with admin access.")
                else:
                    click.echo(f"\n✅ System has {admin_users} admin users.")
                
        except Exception as e:
            click.echo(f"❌ Error getting system info: {str(e)}")
            sys.exit(1)
    
    asyncio.run(_system_info())


@cli.command()
@click.option('--email', prompt='User email', help='Email of the user to reset password')
@click.option('--new-password', prompt='New password', hide_input=True, confirmation_prompt=True, help='New password for the user')
def reset_password(email: str, new_password: str):
    """Reset a user's password."""
    
    async def _reset_password():
        try:
            await init_db()
            
            async for db in get_db():
                # Find user
                user = await user_repository.get_user_by_email(email, db)
                if not user:
                    click.echo(f"❌ User with email {email} not found!")
                    return
                
                # Hash new password
                hashed_password = Hasher.hash_password(new_password)
                
                # Update password
                update_data = {"password": hashed_password}
                updated_user = await user_repository.update_user(user.id, update_data, db)
                
                click.echo(f"✅ Password for user {email} has been reset successfully!")
                
        except Exception as e:
            click.echo(f"❌ Error resetting password: {str(e)}")
            sys.exit(1)
    
    asyncio.run(_reset_password())


if __name__ == '__main__':
    cli() 