#!/bin/bash
set -e

echo "Starting Airflow initialization..."

# Migrate database
echo "Running database migrations..."
airflow db migrate

# Create user with custom credentials using the correct approach for Airflow 3.x
echo "Creating Airflow admin user with custom credentials..."
python3 << 'PYEOF'
import os
import sys
from werkzeug.security import generate_password_hash
from airflow import settings
from sqlalchemy.orm import sessionmaker

engine = settings.engine
Session = sessionmaker(bind=engine)
session = Session()

try:
    from flask_appbuilder.security.sqla.models import User, Role
    
    # Get credentials from environment
    username = os.getenv('_AIRFLOW_WWW_USER_USERNAME', 'airflow')
    password = os.getenv('_AIRFLOW_WWW_USER_PASSWORD', 'airflow1234')
    
    print(f"Creating user: {username}")
    
    # First, delete admin user if it exists (created by Airflow during migration)
    admin_user = session.query(User).filter(User.username == 'admin').first()
    if admin_user:
        print("Deleting default 'admin' user...")
        session.delete(admin_user)
        session.commit()
    
    # Check if desired user already exists
    user = session.query(User).filter(User.username == username).first()
    if user:
        print(f"User {username} already exists, updating password...")
        hashed_pwd = generate_password_hash(password)
        user.password = hashed_pwd
        session.commit()
        print(f"Password updated for user {username}")
    else:
        # Get admin role
        admin_role = session.query(Role).filter(Role.name == 'Admin').first()
        if not admin_role:
            print("ERROR: Admin role not found!")
            roles = session.query(Role).all()
            print(f"Available roles: {[r.name for r in roles]}")
            exit(1)
        
        # Create user
        hashed_pwd = generate_password_hash(password)
        new_user = User(
            username=username,
            email="airflow@airflow.com",
            first_name="Airflow",
            last_name="Admin",
            password=hashed_pwd,
            active=True,
            roles=[admin_role]
        )
        session.add(new_user)
        session.commit()
        print(f"User {username} created successfully with Admin role and password {password}")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
finally:
    session.close()
PYEOF

echo "Airflow initialization complete!"
