#!/usr/bin/env python3
""" db_migrate.py
Database migration script:
- Initializes Users, Sections, and UserSections tables.
- Imports data from the old database to the new database.
Usage:
    > cd scripts; ./db_migrate.py
    OR
    > scripts/db_migrate.py
"""
import shutil
import sys
import os
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import inspect

# Add the directory containing main.py to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import application object
from main import app, db, generate_data

# Backup the old database
def backup_database(db_uri, backup_uri):
    """Backup the current database."""
    if backup_uri:
        db_path = db_uri.replace('sqlite:///', 'instance/')
        backup_path = backup_uri.replace('sqlite:///', 'instance/')
        try:
            shutil.copyfile(db_path, backup_path)
            print(f"Database backed up to {backup_path}")
        except Exception as e:
            print(f"Error during database backup: {e}")
    else:
        print("Backup not supported for production database.")

# Main extraction and loading process
def main():
    """Main function to migrate database."""
    with app.app_context():
        try:
            # Check if database has tables
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()

            if tables:
                print("Warning: This will erase all data in the database!")
                response = input("Do you want to continue? (y/n): ").strip().lower()
                if response != 'y':
                    print("Operation cancelled.")
                    sys.exit(0)

                # Backup the old database
                backup_database(
                    app.config['SQLALCHEMY_DATABASE_URI'], 
                    app.config.get('SQLALCHEMY_BACKUP_URI')
                )

                # Drop all tables
                db.drop_all()
                print("All tables dropped.")

            # Step 2: Rebuild the database schema and generate initial data
            print("Generating data...")
            db.create_all()  # Explicitly create tables before inserting data

            # Ensure the session is clean before generating data
            db.session.commit()

            # Generate data
            generate_data()

            # Explicitly commit again after data generation
            db.session.commit()
            print("Database initialized successfully!")

        except SQLAlchemyError as db_error:
            print(f"SQLAlchemy error: {db_error}")
            db.session.rollback()
            sys.exit(1)
        except Exception as e:
            print(f"Unexpected error: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()