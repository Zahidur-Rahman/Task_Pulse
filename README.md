# Task Pulse 📋

A modern, full-stack task management system built with FastAPI, React, and PostgreSQL. Task Pulse provides a comprehensive solution for team task management with advanced features like multiple assignees, priority tracking, and admin controls.

![Task Pulse](https://img.shields.io/badge/Status-Active-brightgreen)
![Version](https://img.shields.io/badge/Version-1.0.0-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

## ✨ Features

### 🎯 Core Functionality
- **Task Management**: Create, update, delete, and organize tasks
- **Multiple Assignees**: Assign tasks to primary and additional team members
- **Priority System**: High, Medium, Low priority levels with visual indicators
- **Task Types**: Categorize tasks by type for better organization
- **Due Date Tracking**: Set deadlines and track overdue tasks
- **Task Visibility**: Public and private task options

### 🔐 Authentication & Security
- **JWT Authentication**: Secure HttpOnly cookie-based authentication
- **Role-Based Access**: User and Admin role management
- **CORS Protection**: Configurable cross-origin resource sharing
- **Password Security**: Bcrypt hashing for password protection

### 👥 User Management
- **User Registration**: Easy account creation process
- **Admin Dashboard**: Administrative controls and user management
- **Profile Management**: User profile updates and preferences

### 🎨 Modern UI/UX
- **Responsive Design**: Mobile-first responsive interface
- **Modern Styling**: Gradient designs, animations, and hover effects
- **Bootstrap Integration**: Professional UI components
- **Interactive Modals**: Beautiful task creation and editing modals
- **Visual Feedback**: Priority indicators, loading states, and notifications

## 🏗️ Architecture

### Backend (FastAPI)
```
backend/
├── apis/v1/              # API routes
├── core/                 # Configuration and utilities
├── db/                   # Database models and repositories
├── schemas/              # Pydantic schemas
└── alembic/              # Database migrations
```

### Frontend (React)
```
task-management-frontend/
├── src/
│   ├── components/       # Reusable UI components
│   ├── pages/           # Application pages
│   ├── context/         # React context providers
│   └── services/        # API service layer
└── public/              # Static assets
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.9+ (for local backend development)

### 🐳 Docker Setup (Recommended)

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd Task_Pulse
```

2. **Start all services**
```bash
docker-compose up -d
```

3. **Access the application**
- Frontend: http://localhost:3001
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### 🛠️ Local Development Setup

#### Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run database migrations
alembic upgrade head

# Start the server
uvicorn main:app --host 0.0.0.0 --port 7000 --reload
```

#### Frontend Setup
```bash
cd task-management-frontend

# Install dependencies
npm install

# Start development server
npm start
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
# Database
POSTGRES_USER=task_user
POSTGRES_PASSWORD=task_password_123
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_DB=task_pulse_db

# Security
SUPER_SECRET=your_super_secret_key_here_make_it_at_least_32_characters_long
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Cookie Configuration
COOKIE_SECURE=false
COOKIE_SAMESITE=lax

# Redis (Optional)
REDIS_URL=redis://localhost:6379

# Admin Setup
SETUP_TOKEN=TASK_PULSE_SETUP_2024
ADMIN_PROMOTION_CODE=ADMIN_PROMOTION_2024
DIRECT_ADMIN_REG_CODE=DIRECT_ADMIN_REG_2024
```

### Docker Configuration

The `docker-compose.yml` includes:
- **PostgreSQL 15**: Primary database
- **Redis 7**: Caching and session storage
- **Backend**: FastAPI application
- **Frontend**: React application (optional)

## 📊 Database Schema

### Key Models
- **User**: User accounts with role management
- **Task**: Core task entity with multiple assignees
- **UserTask**: Many-to-many relationship for task assignments

### Relationships
- Users can have multiple assigned tasks
- Tasks can have multiple assignees (primary + additional)
- Admin users can create tasks for any user

## 🔌 API Endpoints

### Authentication
- `POST /api/v1/login` - User login
- `POST /api/v1/logout` - User logout
- `POST /api/v1/user/` - User registration

### Tasks
- `GET /api/v1/task/` - Get user tasks
- `POST /api/v1/task/` - Create task
- `PUT /api/v1/task/{id}` - Update task
- `DELETE /api/v1/task/{id}` - Delete task
- `GET /api/v1/task/assignee/tasks` - Get assigned tasks

### Admin
- `POST /api/v1/admin/task` - Admin task creation
- `GET /api/v1/admin/users` - User management

## 🎨 UI Components

### Key Features
- **Dashboard**: Overview of tasks with statistics
- **Task Creation Modal**: Multi-step form with assignee selection
- **Task Cards**: Priority-coded task display
- **User Management**: Admin controls for user operations

### Styling
- Custom CSS variables for consistent theming
- Gradient backgrounds and hover animations
- Bootstrap 5 integration
- Mobile-responsive design

## 🧪 Testing

### Backend Testing
```bash
cd backend
pytest
```

### Frontend Testing
```bash
cd task-management-frontend
npm test
```

## 📈 Performance Features

- **Database Indexing**: Optimized queries for task retrieval
- **Redis Caching**: Session and data caching
- **Async Operations**: Non-blocking database operations
- **Connection Pooling**: Efficient database connections

## 🔒 Security Features

- **HttpOnly Cookies**: XSS protection for JWT tokens
- **CORS Configuration**: Controlled cross-origin access
- **Password Hashing**: Bcrypt for secure password storage
- **Input Validation**: Pydantic schemas for data validation
- **SQL Injection Protection**: SQLAlchemy ORM protection

## 🚀 Deployment

### Production Checklist
- [ ] Set `COOKIE_SECURE=true` for HTTPS
- [ ] Configure proper `COOKIE_DOMAIN`
- [ ] Update `BACKEND_CORS_ORIGINS` for production domains
- [ ] Set strong `SUPER_SECRET` key
- [ ] Configure production database
- [ ] Set up SSL certificates
- [ ] Configure reverse proxy (nginx)

### Docker Production
```bash
# Build and deploy
docker-compose -f docker-compose.prod.yml up -d
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check the `/docs` endpoint for API documentation
- **Issues**: Report bugs via GitHub Issues
- **Admin Setup**: See `ADMIN_SETUP.md` for admin configuration

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- React team for the frontend library
- PostgreSQL for reliable data storage
- Bootstrap for UI components

---

**Task Pulse** - Streamline your team's productivity with modern task management! 🚀
