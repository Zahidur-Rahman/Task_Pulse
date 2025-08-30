#!/usr/bin/env python3
"""
Test script to verify all imports are working
"""

import sys
import os

# Add backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

def test_imports():
    """Test all critical imports."""
    try:
        print("🔍 Testing imports...")
        
        # Test core imports
        from core.config import settings
        print("✅ Core config imported successfully")
        
        # Test database imports
        from db.base import Base
        print("✅ Database base imported successfully")
        
        # Test models
        from db.models.user import User
        from db.models.task import Task, Subtask, TimeLog, TaskComment, Organization
        print("✅ Models imported successfully")
        
        # Test schemas
        from schemas.user import UserCreate, UserResponse
        from schemas.task import TaskCreate, TaskResponse
        print("✅ Schemas imported successfully")
        
        # Test repositories
        from db.repository.user import user_repository
        from db.repository.task import create_new_task, retrieve_task
        print("✅ Repositories imported successfully")
        
        # Test APIs
        from apis.base import api_router
        print("✅ API router imported successfully")
        
        # Test main app
        from main import app
        print("✅ Main app imported successfully")
        
        print("\n🎉 All imports successful! Your TaskPulse setup is working.")
        print(f"Database URL: {settings.DATABASE_URL}")
        print(f"Project: {settings.PROJECT_TITLE}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print(f"Error type: {type(e).__name__}")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print(f"Error type: {type(e).__name__}")
        return False

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1) 