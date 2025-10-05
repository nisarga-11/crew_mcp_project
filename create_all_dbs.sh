#!/bin/bash

# --- PostgreSQL superuser ---
PGUSER="postgres"
export PGPASSWORD=""

# --- PostgreSQL cluster data directories ---
PG1_DATA="/var/lib/postgresql/17/pg1_17"
PG2_DATA="/var/lib/postgresql/17/pg2_17"

# --- Helper function to execute queries ---
exec_query() {
    local DB=$1
    local PORT=$2
    local QUERY=$3
    psql -h 127.0.0.1 -p $PORT -U $PGUSER -d $DB -c "$QUERY"
}

# --- Helper function to create database if it doesn't exist ---
create_db() {
    local DBNAME=$1
    local PORT=$2
    local EXISTS=$(psql -h 127.0.0.1 -p $PORT -U $PGUSER -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='$DBNAME';" 2>/dev/null)
    if [[ -z "$EXISTS" ]]; then
        exec_query "postgres" $PORT "CREATE DATABASE $DBNAME;"
        echo "Database $DBNAME created on port $PORT."
    else
        echo "Database $DBNAME already exists on port $PORT. Skipping."
    fi
}

# --- Helper function to check if a port is open ---
is_port_open() {
    local PORT=$1
    nc -z 127.0.0.1 $PORT &>/dev/null
    return $?
}

# --- Start PostgreSQL clusters if not running ---
start_cluster() {
    local DATA_DIR=$1
    local PORT=$2
    if ! is_port_open $PORT; then
        echo "Starting PostgreSQL cluster on port $PORT..."
        sudo pg_ctlcluster 17 $(basename $DATA_DIR) start
        sleep 3
    else
        echo "PostgreSQL cluster already running on port $PORT."
    fi
}

# --- Start clusters ---
start_cluster $PG1_DATA 5433
start_cluster $PG2_DATA 5434

# --- Create databases ---
create_db "db1" 5433
create_db "db2" 5433
create_db "db3" 5434
create_db "db4" 5434

# --- Create tables and insert sample data ---

# db1
exec_query "db1" 5433 "
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50),
    email VARCHAR(50) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
INSERT INTO users (name, email) VALUES
('Alice', 'alice@example.com'),
('Bob', 'bob@example.com')
ON CONFLICT DO NOTHING;
"

# db2
exec_query "db2" 5433 "
CREATE TABLE IF NOT EXISTS customers (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(100),
    email VARCHAR(50) UNIQUE,
    joined_on DATE DEFAULT CURRENT_DATE
);
INSERT INTO customers (full_name, email) VALUES
('Charlie Brown', 'charlie@example.com'),
('Diana Prince', 'diana@example.com')
ON CONFLICT DO NOTHING;
"

# db3
exec_query "db3" 5434 "
CREATE TABLE IF NOT EXISTS employees (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50),
    department VARCHAR(50),
    hired_on DATE DEFAULT CURRENT_DATE
);
INSERT INTO employees (name, department) VALUES
('Eve Adams', 'HR'),
('Frank Miller', 'IT')
ON CONFLICT DO NOTHING;
"

# db4
exec_query "db4" 5434 "
CREATE TABLE IF NOT EXISTS projects (
    id SERIAL PRIMARY KEY,
    project_name VARCHAR(100),
    start_date DATE DEFAULT CURRENT_DATE,
    end_date DATE
);
INSERT INTO projects (project_name, start_date, end_date) VALUES
('Website Redesign', '2025-09-01', '2025-12-01'),
('Mobile App', '2025-08-15', '2025-11-15')
ON CONFLICT DO NOTHING;
"

echo "✅ All databases, tables, and sample data are ready!"
