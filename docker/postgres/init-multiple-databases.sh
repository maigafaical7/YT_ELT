#!/bin/bash

set -e

# Debug: print env vars
echo "DEBUG: METADATA_DATABASE_NAME='$METADATA_DATABASE_NAME'"
echo "DEBUG: METADATA_DATABASE_USERNAME='$METADATA_DATABASE_USERNAME'"
echo "DEBUG: METADATA_DATABASE_PASSWORD='$METADATA_DATABASE_PASSWORD'"
echo "DEBUG: CELERY_BACKEND_NAME='$CELERY_BACKEND_NAME'"
echo "DEBUG: ELT_DATABASE_NAME='$ELT_DATABASE_NAME'"

# Only proceed if variables are set
if [ -z "$METADATA_DATABASE_NAME" ] || [ -z "$METADATA_DATABASE_USERNAME" ]; then
    echo "ERROR: Required environment variables not set. Exiting."
    exit 1
fi

set -u

function create_user_and_database() {
    local database=$1
    local username=$2
    local password=$3
    echo "Creating user '$username' and database '$database'"
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
        CREATE USER "$username" WITH PASSWORD '$password';
        CREATE DATABASE "$database";
        GRANT ALL PRIVILEGES ON DATABASE "$database" TO "$username";
EOSQL
    echo "  User '$username' and database '$database' created successfully"
}

# Metadata database
create_user_and_database $METADATA_DATABASE_NAME $METADATA_DATABASE_USERNAME $METADATA_DATABASE_PASSWORD

# Celery result backend database
create_user_and_database $CELERY_BACKEND_NAME $CELERY_BACKEND_USERNAME $CELERY_BACKEND_PASSWORD

# ELT database
create_user_and_database $ELT_DATABASE_NAME $ELT_DATABASE_USERNAME $ELT_DATABASE_PASSWORD

echo "All databases and users created successfully"