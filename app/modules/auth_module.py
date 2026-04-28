# Auth Module
import pandas as pd
from app.config.settings import EXCEL_FILE, ADMIN_SHEET, USER_SHEET, GUEST_SHEET, DOMAIN_SHEET, USE_DB_FOR_AUTH
from app.modules.db_module import SessionLocal, Admin, User, Guest, Domain

def load_users():
    if USE_DB_FOR_AUTH:
        db = SessionLocal()
        try:
            admins = db.query(Admin).all()
            users = db.query(User).all()
            guests = db.query(Guest).all()
            
            df_admin = pd.DataFrame([(a.username, a.password) for a in admins], columns=['username', 'password'])
            df_user = pd.DataFrame([(u.username, u.password, u.domain, u.subdomain) for u in users], columns=['username', 'password', 'domain', 'subdomain'])
            df_guest = pd.DataFrame([(g.username, g.password) for g in guests], columns=['username', 'password'])
            
            return df_admin, df_user, df_guest
        finally:
            db.close()
    else:
        df_admin = pd.read_excel(EXCEL_FILE, sheet_name=ADMIN_SHEET)
        df_user = pd.read_excel(EXCEL_FILE, sheet_name=USER_SHEET)
        df_guest = pd.read_excel(EXCEL_FILE, sheet_name=GUEST_SHEET)
        return df_admin, df_user, df_guest

def load_domains():
    if USE_DB_FOR_AUTH:
        db = SessionLocal()
        try:
            domains = db.query(Domain).all()
            return [d.domain for d in domains if d.domain]
        finally:
            db.close()
    else:
        try:
            df_domains = pd.read_excel(EXCEL_FILE, sheet_name=DOMAIN_SHEET)
            if 'domain' in df_domains.columns:
                return [str(d).strip() for d in df_domains['domain'].dropna().unique() if str(d).strip()]
            return []
        except Exception:
            return []


def load_subdomains(domain=None):
    if USE_DB_FOR_AUTH:
        db = SessionLocal()
        try:
            if domain:
                domain_obj = db.query(Domain).filter(Domain.domain == domain).first()
                if domain_obj and domain_obj.subdomains:
                    return sorted([s.strip() for s in domain_obj.subdomains.split(',') if s.strip()])
                return []
            else:
                return []
        finally:
            db.close()
    else:
        try:
            df_domains = pd.read_excel(EXCEL_FILE, sheet_name=DOMAIN_SHEET)
            if 'domain' not in df_domains.columns or 'subdomains' not in df_domains.columns:
                return []
            
            if domain:
                domain_row = df_domains[df_domains['domain'] == domain]
                if domain_row.empty:
                    return []
                subs_str = str(domain_row['subdomains'].iloc[0]).strip()
                if not subs_str:
                    return []
                return sorted([s.strip() for s in subs_str.split(',') if s.strip()])
            
            return []
        except Exception:
            return []


def add_domain(domain):
    if not domain or not str(domain).strip():
        return False
    domain = str(domain).strip()
    
    if USE_DB_FOR_AUTH:
        db = SessionLocal()
        try:
            existing = db.query(Domain).filter(Domain.domain == domain).first()
            if existing:
                return False
            new_domain = Domain(domain=domain, subdomains='')
            db.add(new_domain)
            db.commit()
            return True
        except Exception:
            db.rollback()
            return False
        finally:
            db.close()
    else:
        try:
            try:
                df_domains = pd.read_excel(EXCEL_FILE, sheet_name=DOMAIN_SHEET)
            except Exception:
                df_domains = pd.DataFrame(columns=['domain', 'subdomains'])
            
            if 'subdomains' not in df_domains.columns:
                df_domains['subdomains'] = ''
            
            existing = [str(d).strip() for d in df_domains['domain'].dropna().unique() if str(d).strip()]
            if domain in existing:
                return False
            df_domains = pd.concat([df_domains, pd.DataFrame({'domain': [domain], 'subdomains': ['']})], ignore_index=True)
            with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                df_domains.to_excel(writer, sheet_name=DOMAIN_SHEET, index=False)
            return True
        except Exception:
            return False

def add_subdomain_to_domain(domain, subdomain):
    if not domain or not subdomain:
        return False
    domain = str(domain).strip()
    subdomain = str(subdomain).strip()
    
    if USE_DB_FOR_AUTH:
        db = SessionLocal()
        try:
            domain_obj = db.query(Domain).filter(Domain.domain == domain).first()
            if not domain_obj:
                return False
            
            existing_subs = domain_obj.subdomains or ''
            if existing_subs:
                sub_list = [s.strip() for s in existing_subs.split(',')]
                if subdomain in sub_list:
                    return True
                sub_list.append(subdomain)
                new_subs = ', '.join(sub_list)
            else:
                new_subs = subdomain
            
            domain_obj.subdomains = new_subs
            db.commit()
            return True
        except Exception:
            db.rollback()
            return False
        finally:
            db.close()
    else:
        try:
            try:
                df_domains = pd.read_excel(EXCEL_FILE, sheet_name=DOMAIN_SHEET)
            except Exception:
                return False
            
            if 'subdomains' not in df_domains.columns:
                df_domains['subdomains'] = ''
            
            domain_idx = df_domains[df_domains['domain'] == domain].index
            if len(domain_idx) == 0:
                return False
            
            existing_subs = str(df_domains.loc[domain_idx[0], 'subdomains']).strip()
            if existing_subs:
                sub_list = [s.strip() for s in existing_subs.split(',')]
                if subdomain in sub_list:
                    return True
                sub_list.append(subdomain)
                new_subs = ', '.join(sub_list)
            else:
                new_subs = subdomain
            
            df_domains.loc[domain_idx[0], 'subdomains'] = new_subs
            df_domains.to_excel(EXCEL_FILE, sheet_name=DOMAIN_SHEET, index=False, engine='openpyxl')
            return True
        except Exception as e:
            return False

def authenticate(username, password, role):
    df_admin, df_user, df_guest = load_users()
    if role == "admin":
        df = df_admin
    elif role == "user":
        df = df_user
    else:
        df = df_guest
    user = df[(df['username'] == username) & (df['password'] == password)]
    return not user.empty

# User management functions
def add_admin_user(username, password):
    if USE_DB_FOR_AUTH:
        db = SessionLocal()
        try:
            existing = db.query(Admin).filter(Admin.username == username).first()
            if existing:
                return False
            new_admin = Admin(username=username, password=password)
            db.add(new_admin)
            db.commit()
            return True
        except Exception:
            db.rollback()
            return False
        finally:
            db.close()
    else:
        # For Excel, we'd need to modify the Excel file
        # This is more complex, so for now we'll focus on DB
        return False

def add_user(username, password, domain, subdomain):
    if USE_DB_FOR_AUTH:
        db = SessionLocal()
        try:
            existing = db.query(User).filter(User.username == username).first()
            if existing:
                return False
            new_user = User(username=username, password=password, domain=domain, subdomain=subdomain)
            db.add(new_user)
            db.commit()
            return True
        except Exception:
            db.rollback()
            return False
        finally:
            db.close()
    else:
        return False

def add_guest_user(username, password):
    if USE_DB_FOR_AUTH:
        db = SessionLocal()
        try:
            existing = db.query(Guest).filter(Guest.username == username).first()
            if existing:
                return False
            new_guest = Guest(username=username, password=password)
            db.add(new_guest)
            db.commit()
            return True
        except Exception:
            db.rollback()
            return False
        finally:
            db.close()
    else:
        return False

def remove_user(username, role):
    if USE_DB_FOR_AUTH:
        db = SessionLocal()
        try:
            if role == "admin":
                user = db.query(Admin).filter(Admin.username == username).first()
                if user:
                    db.delete(user)
            elif role == "user":
                user = db.query(User).filter(User.username == username).first()
                if user:
                    db.delete(user)
            elif role == "guest":
                user = db.query(Guest).filter(Guest.username == username).first()
                if user:
                    db.delete(user)
            db.commit()
            return True
        except Exception:
            db.rollback()
            return False
        finally:
            db.close()
    else:
        return False

def get_all_users():
    if USE_DB_FOR_AUTH:
        db = SessionLocal()
        try:
            admins = db.query(Admin).all()
            users = db.query(User).all()
            guests = db.query(Guest).all()
            
            admin_list = [{"username": a.username, "role": "admin"} for a in admins]
            user_list = [{"username": u.username, "role": "user", "domain": u.domain, "subdomain": u.subdomain} for u in users]
            guest_list = [{"username": g.username, "role": "guest"} for g in guests]
            
            return admin_list + user_list + guest_list
        finally:
            db.close()
    else:
        df_admin, df_user, df_guest = load_users()
        admin_list = [{"username": row['username'], "role": "admin"} for _, row in df_admin.iterrows()]
        user_list = [{"username": row['username'], "role": "user", "domain": row.get('domain', ''), "subdomain": row.get('subdomain', '')} for _, row in df_user.iterrows()]
        guest_list = [{"username": row['username'], "role": "guest"} for _, row in df_guest.iterrows()]
        return admin_list + user_list + guest_list