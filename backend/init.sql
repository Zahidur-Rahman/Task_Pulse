-- Task Pulse Database Initialization Script
-- This script sets up the initial database configuration

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create database if it doesn't exist (this will be handled by Docker)
-- CREATE DATABASE task_pulse_db;

-- Set timezone
SET timezone = 'UTC';

-- Create custom types if needed
DO $$
BEGIN
    -- Create task status enum if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'taskstatustype') THEN
        CREATE TYPE taskstatustype AS ENUM ('Pending', 'In Progress', 'Completed');
    END IF;
END$$;

-- Grant necessary permissions
GRANT ALL PRIVILEGES ON DATABASE task_pulse_db TO task_user;
GRANT ALL PRIVILEGES ON SCHEMA public TO task_user;

-- Set search path
ALTER DATABASE task_pulse_db SET search_path TO public;

-- Create indexes for better performance (these will be created by SQLAlchemy models)
-- But we can add some custom ones here if needed

-- Log the initialization
DO $$
BEGIN
    RAISE NOTICE 'Task Pulse database initialized successfully';
    RAISE NOTICE 'Database: %', current_database();
    RAISE NOTICE 'User: %', current_user();
    RAISE NOTICE 'Timezone: %', current_setting('timezone');
END$$; 