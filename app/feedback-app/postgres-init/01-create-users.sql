-- PostgreSQL User Setup for Local Development
-- This script runs automatically when PostgreSQL container starts for the first time

-- Create user if not exists
DO
$$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles
      WHERE rolname = 'feedback_user') THEN
      CREATE USER feedback_user WITH PASSWORD '';
   END IF;
END
$$;


-- Create database if not exists
DO
$$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_database
      WHERE datname = 'feedback_db') THEN
      CREATE DATABASE feedback_db OWNER feedback_user;
   END IF;
END
$$;

-- Connect to the database
\connect feedback_db;

-- Grant privileges (safe to re-run)
GRANT ALL PRIVILEGES ON DATABASE feedback_db TO feedback_user;


-- Create table if not exists
CREATE TABLE IF NOT EXISTS feedback (
    id SERIAL PRIMARY KEY,
    rating VARCHAR(30) NOT NULL,
    message TEXT NOT NULL,    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- Confirmation message
SELECT 'PostgreSQL setup complete! All users and databases ready.' as status;
