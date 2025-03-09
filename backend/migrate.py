#!/usr/bin/env python3
"""
Database migration script for Infinite Alchemist.

This script migrates the database to support language-specific elements.
"""

from app.db.migrate_db import migrate_db

if __name__ == "__main__":
    print("Starting database migration...")
    migrate_db()
    print("Migration completed.") 