# 🔑 Task Pulse - Admin Setup Guide

This guide explains how to create your first admin user in the Task Pulse system. You have **three different methods** to choose from.

## 🚀 Quick Start

### Method 1: Simple Setup Script (Recommended for first-time setup)

```bash
# Navigate to backend directory
cd backend

# Activate virtual environment
source ../env1/bin/activate

# Run the simple setup script
python setup_admin.py
```

This script will:
- ✅ Check if admin already exists
- 📝 Prompt for admin details (email, password, name)
- 🔐 Create the admin user
- 📊 Show confirmation and next steps

### Method 2: CLI Management Tool (Full-featured)

```bash
# Navigate to backend directory
cd backend

# Activate virtual environment
source ../env1/bin/activate

# Create admin using CLI
python manage.py create-admin
```

### Method 3: API Endpoint (After server is running)

```bash
# Start the backend server first
cd backend
source ../env1/bin/activate
python main.py

# Then use the API endpoint
curl -X POST "http://localhost:8000/api/v1/admin/setup?setup_token=TASK_PULSE_SETUP_2024" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "AdminPass123",
    "first_name": "Admin",
    "last_name": "User"
  }'
```

## 📚 Complete CLI Management Commands

The `manage.py` script provides comprehensive system management:

### 🔐 User Management
```bash
# Create admin user
python manage.py create-admin

# Create regular user
python manage.py create-user

# Promote user to admin/manager
python manage.py promote-user

# List all users
python manage.py list-users

# Deactivate user
python manage.py deactivate-user

# Reset user password
python manage.py reset-password
```

### 📊 System Information
```bash
# Check system status
python manage.py system-info

# Check database health
python manage.py check-db

# Create demo data for testing
python manage.py seed-demo-data
```

### 🆘 Help
```bash
# Show all available commands
python manage.py --help

# Show help for specific command
python manage.py create-admin --help
```

## 🎯 Step-by-Step Setup Process

### 1. **Prerequisites**
```bash
# Make sure you have:
# ✅ Docker and Docker Compose running
# ✅ Virtual environment activated
# ✅ Dependencies installed
# ✅ Database running and migrated
```

### 2. **Create First Admin**
```bash
cd backend
source ../env1/bin/activate

# Choose your preferred method:
python setup_admin.py                    # Simple setup
# OR
python manage.py create-admin            # CLI tool
```

### 3. **Verify Setup**
```bash
# Check system status
python manage.py system-info

# Should show:
# ✅ Database: Connected
# 👥 Total Users: 1
# 👑 Admins: 1
# ✅ System properly configured with admin access
```

### 4. **Start Services**
```bash
# Start backend
python main.py

# In another terminal, start frontend
cd task-management-frontend
npm start
```

### 5. **Login as Admin**
- Open browser to `http://localhost:3000`
- Login with your admin credentials
- You'll be redirected to `/admin/dashboard`

## 🔧 Troubleshooting

### Common Issues

#### ❌ "Database connection failed"
```bash
# Check if Docker services are running
docker-compose ps

# Start services if needed
docker-compose up -d postgres redis

# Wait for database to be ready
sleep 10
```

#### ❌ "Module not found" errors
```bash
# Make sure virtual environment is activated
source env1/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### ❌ "Admin user already exists"
```bash
# Check existing users
python manage.py list-users

# Use --force flag to create another admin
python manage.py create-admin --force
```

#### ❌ "Permission denied" on manage.py
```bash
# Make script executable
chmod +x manage.py
chmod +x setup_admin.py
```

### Database Issues

#### Reset Database (⚠️ **WARNING: This will delete all data**)
```bash
# Stop services
docker-compose down

# Remove database volume
docker volume rm task_pulse_postgres_data

# Start fresh
docker-compose up -d postgres redis
sleep 10

# Run migrations
cd backend
source ../env1/bin/activate
alembic upgrade head

# Create admin
python setup_admin.py
```

## 🎉 Success Indicators

After successful setup, you should see:

```
🎉 Admin user created successfully!
========================================
   ID: 1
   Email: admin@example.com
   Name: Admin User
   Role: admin
   Created: 2024-01-XX XX:XX:XX
========================================

✅ Setup complete! You can now:
   1. Start the backend server: python main.py
   2. Login to the admin dashboard
   3. Create additional users through the web interface
```

## 🔐 Security Notes

- **First Admin**: The first admin created becomes the "Super Admin" with full privileges
- **Password Security**: Use strong passwords in production
- **Environment Variables**: Store sensitive tokens in `.env` file
- **Access Control**: Only promote trusted users to admin roles

## 📞 Need Help?

If you encounter issues:

1. **Check the logs**: Look for error messages in the terminal
2. **Verify prerequisites**: Ensure Docker, Python, and dependencies are properly installed
3. **Database status**: Use `python manage.py check-db` to verify database connection
4. **System info**: Use `python manage.py system-info` to see current system status

## 🚀 Next Steps

After creating your admin user:

1. **Explore the Admin Dashboard**: Access system overview and user management
2. **Create Demo Data**: Use `python manage.py seed-demo-data` for testing
3. **Invite Team Members**: Create additional users through the web interface
4. **Configure System**: Set up tasks, projects, and workflows

---

**Happy Task Managing! 🎯✨** 