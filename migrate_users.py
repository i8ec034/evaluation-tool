#!/usr/bin/env python3
"""
Migration script to move users from Excel to Database
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pandas as pd
from app.config.settings import EXCEL_FILE, ADMIN_SHEET, USER_SHEET, GUEST_SHEET, DOMAIN_SHEET
from app.modules.db_module import SessionLocal, Admin, User, Guest, Domain

def migrate_users_to_db():
    print("Starting migration from Excel to Database...")

    try:
        # Load data from Excel
        df_admin = pd.read_excel(EXCEL_FILE, sheet_name=ADMIN_SHEET)
        df_user = pd.read_excel(EXCEL_FILE, sheet_name=USER_SHEET)
        df_guest = pd.read_excel(EXCEL_FILE, sheet_name=GUEST_SHEET)
        df_domains = pd.read_excel(EXCEL_FILE, sheet_name=DOMAIN_SHEET)

        db = SessionLocal()

        # Migrate admins
        print("Migrating admins...")
        for _, row in df_admin.iterrows():
            username = str(row['username']).strip()
            password = str(row['password']).strip()
            existing = db.query(Admin).filter(Admin.username == username).first()
            if not existing:
                admin = Admin(username=username, password=password)
                db.add(admin)
                print(f"Added admin: {username}")

        # Migrate users
        print("Migrating users...")
        for _, row in df_user.iterrows():
            username = str(row['username']).strip()
            password = str(row['password']).strip()
            domain = str(row.get('domain', '')).strip()
            subdomain = str(row.get('subdomain', '')).strip()
            existing = db.query(User).filter(User.username == username).first()
            if not existing:
                user = User(username=username, password=password, domain=domain, subdomain=subdomain)
                db.add(user)
                print(f"Added user: {username}")

        # Migrate guests
        print("Migrating guests...")
        for _, row in df_guest.iterrows():
            username = str(row['username']).strip()
            password = str(row['password']).strip()
            existing = db.query(Guest).filter(Guest.username == username).first()
            if not existing:
                guest = Guest(username=username, password=password)
                db.add(guest)
                print(f"Added guest: {username}")

        # Migrate domains
        print("Migrating domains...")
        for _, row in df_domains.iterrows():
            domain_name = str(row['domain']).strip()
            subdomains = str(row.get('subdomains', '')).strip()
            existing = db.query(Domain).filter(Domain.domain == domain_name).first()
            if not existing:
                domain = Domain(domain=domain_name, subdomains=subdomains)
                db.add(domain)
                print(f"Added domain: {domain_name}")

        db.commit()
        print("Migration completed successfully!")

    except Exception as e:
        print(f"Migration failed: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    migrate_users_to_db()