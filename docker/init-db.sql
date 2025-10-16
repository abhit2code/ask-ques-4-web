-- PostgreSQL Database Initialization Script
-- Creates single database with separate schemas for dev/prod environments

-- Create main database
CREATE DATABASE rag_engine;

-- Connect to the database and create schemas
\c rag_engine;

-- Development schema
CREATE SCHEMA IF NOT EXISTS dev;

-- Production schema  
CREATE SCHEMA IF NOT EXISTS prod;

-- Grant permissions
GRANT ALL PRIVILEGES ON SCHEMA dev TO postgres;
GRANT ALL PRIVILEGES ON SCHEMA prod TO postgres;
