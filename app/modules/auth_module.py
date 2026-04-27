# Auth Module
import pandas as pd
from app.config.settings import EXCEL_FILE, ADMIN_SHEET, USER_SHEET, GUEST_SHEET, DOMAIN_SHEET

def load_users():
    df_admin = pd.read_excel(EXCEL_FILE, sheet_name=ADMIN_SHEET)
    df_user = pd.read_excel(EXCEL_FILE, sheet_name=USER_SHEET)
    df_guest = pd.read_excel(EXCEL_FILE, sheet_name=GUEST_SHEET)
    return df_admin, df_user, df_guest

def load_domains():
    try:
        df_domains = pd.read_excel(EXCEL_FILE, sheet_name=DOMAIN_SHEET)
        if 'domain' in df_domains.columns:
            return [str(d).strip() for d in df_domains['domain'].dropna().unique() if str(d).strip()]
        return []
    except Exception:
        return []


def load_subdomains(domain=None):
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