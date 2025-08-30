# TaskPulse - Local Development Guide

## 🚀 Quick Start

1. **Run the setup script:**
   ```bash
   chmod +x start_local.sh
   ./start_local.sh
   ```

2. **Set up PostgreSQL database manually:**
   ```sql
   -- Connect to PostgreSQL as superuser
   sudo -u postgres psql
   
   -- Create database and user
   CREATE DATABASE task_pulse_db;
   CREATE USER task_user WITH PASSWORD 'task_password_123';
   GRANT ALL PRIVILEGES ON DATABASE task_pulse_db TO task_user;
   \q
   ```

3. **Start the backend:**
   ```bash
   cd backend
   source ../env1/bin/activate
   python main.py
   ```

4. **Start the frontend (in a new terminal):**
   ```bash
   cd task-management-frontend
   npm start
   ```

## 📋 Prerequisites

### System Requirements
- **Python 3.8+** (3.11+ recommended)
- **PostgreSQL 12+**
- **Node.js 16+** (18+ recommended)
- **npm** or **yarn**

### Install Dependencies

#### Ubuntu/Debian
```bash
# Update package list
sudo apt update

# Install Python and pip
sudo apt install python3 python3-pip python3-venv

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# Install Node.js (using NodeSource repository)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs

# Start PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### macOS
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python

# Install PostgreSQL
brew install postgresql
brew services start postgresql

# Install Node.js
brew install node
```

#### Windows
- **Python**: Download from [python.org](https://python.org)
- **PostgreSQL**: Download from [postgresql.org](https://postgresql.org/download/windows/)
- **Node.js**: Download from [nodejs.org](https://nodejs.org)

## 🔧 Configuration

### Environment Variables
The `.env` file contains all necessary configuration:

```bash
# Database Configuration
POSTGRES_USER=task_user
POSTGRES_PASSWORD=task_password_123
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_DB=task_pulse_db

# Security Configuration
SUPER_SECRET=your_super_secret_key_here_make_it_at_least_32_characters_long_2024
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS Configuration
BACKEND_CORS_ORIGINS=["http://localhost:3001","http://localhost:3000"]
```

### Database Setup
1. **Create database:**
   ```sql
   CREATE DATABASE task_pulse_db;
   ```

2. **Create user:**
   ```sql
   CREATE USER task_user WITH PASSWORD 'task_password_123';
   GRANT ALL PRIVILEGES ON DATABASE task_pulse_db TO task_user;
   ```

3. **Run migrations:**
   ```bash
   cd backend
   source ../env1/bin/activate
   alembic upgrade head
   ```

## 🗄️ Database Migrations

### Current Migration Status
Your project has two migrations:
1. **Initial migration** (`c9d62c19aeef`) - Basic user and task tables
2. **Enhanced system** (`enhanced_task_system`) - Advanced features

### Running Migrations
```bash
cd backend
source ../env1/bin/activate

# Check current status
alembic current

# Run all pending migrations
alembic upgrade head

# Rollback to specific migration
alembic downgrade <revision_id>

# Create new migration (if you modify models)
alembic revision --autogenerate -m "Description of changes"
```

### Model Changes
Since you've modified the models, you should:

1. **Review existing migrations** to ensure they match your current models
2. **Create new migrations** for any additional changes:
   ```bash
   alembic revision --autogenerate -m "Add new features"
   alembic upgrade head
   ```

## 👑 Admin User Creation

### Method 1: Setup Endpoint (Recommended)
```bash
curl -X POST "http://localhost:8000/api/v1/admin/setup?setup_token=TASK_PULSE_SETUP_2024" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@taskpulse.com",
    "password": "admin123",
    "first_name": "Admin",
    "last_name": "User"
  }'
```

### Method 2: Direct Registration
```bash
curl -X POST "http://localhost:8000/api/v1/admin/register?admin_registration_code=DIRECT_ADMIN_REG_2024" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@taskpulse.com",
    "password": "admin123",
    "first_name": "Admin",
    "last_name": "User"
  }'
```

### Method 3: Promote Existing User
```bash
curl -X POST "http://localhost:8000/api/v1/admin/promote/1?promotion_code=ADMIN_PROMOTION_2024" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## 🚀 Running the Application

### Backend
```bash
cd backend
source ../env1/bin/activate

# Development mode with auto-reload
python main.py

# Or using uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend
```bash
cd task-management-frontend

# Install dependencies (first time only)
npm install

# Start development server
npm start
```

## 📊 Access Points

- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Frontend**: http://localhost:3001
- **Database**: localhost:5432

## 🔍 Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Check if PostgreSQL is running
   - Verify credentials in `.env`
   - Ensure database exists

2. **Port Already in Use**
   - Backend: Change port in `main.py` or use `--port` flag
   - Frontend: Change port in `package.json` or use `PORT=3002 npm start`

3. **Migration Errors**
   - Check database connection
   - Verify model definitions match migrations
   - Reset database if needed: `alembic downgrade base && alembic upgrade head`

4. **Dependency Issues**
   - Recreate virtual environment: `rm -rf env1 && python3 -m venv env1`
   - Update pip: `pip install --upgrade pip`
   - Clear pip cache: `pip cache purge`

### Logs
- **Backend logs**: Check terminal output
- **Database logs**: `sudo tail -f /var/log/postgresql/postgresql-*.log`
- **Frontend logs**: Check browser console and terminal

## 🧪 Testing

### Backend Tests
```bash
cd backend
source ../env1/bin/activate
pytest
```

### Frontend Tests
```bash
cd task-management-frontend
npm test
```

## 📚 Additional Resources

- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **SQLAlchemy Documentation**: https://docs.sqlalchemy.org/
- **Alembic Documentation**: https://alembic.sqlalchemy.org/
- **React Documentation**: https://reactjs.org/docs/ 