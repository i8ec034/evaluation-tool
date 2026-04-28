# Gamified Internal Evaluation Application

This is a Python-based application for internal evaluations with gamification.

## Features
- Admin login to upload documents and generate Q&A using LLM (Google Gemini).
- User login to view theory and take gamified quizzes based on areas.
- Guest access to view theory.
- Modular design for LLM, DB, Auth, Vector DB.
- Configurable settings.
- **NEW:** Database-based user management with admin controls.

## Tech Stack
- Backend: FastAPI
- Frontend: Streamlit
- LLM: Google Gemini API
- DB: SQLite (configurable)
- Vector DB: ChromaDB
- Auth: Configurable (Excel or Database)

## Setup
1. Install Python 3.14.
2. Create venv: `python3.14.exe -m venv venv`
3. Activate: `.\venv\Scripts\Activate.ps1`
4. Install dependencies: `pip install -r requirements.txt`
5. Set GEMINI_API_KEY in `app/config/settings.py`.
6. Set USE_DB_FOR_AUTH=True in `app/config/settings.py` for database authentication.
7. Run migration script: `python migrate_users.py` (if switching from Excel to DB)
8. Run: `streamlit run app/frontend/app.py`

## Usage
- Login as admin (admin1/pass1) to upload documents for areas.
- Login as user (user1/pass1) to view theory for area1 and take quiz.
- Login as guest (guest1/pass1) to view theory.
- **NEW:** Admins can manage users via "User Management" tab.

## User Management (Admin Only)
When `USE_DB_FOR_AUTH=True`:
- **Manage Users Tab**: Add new users (admin, user, guest) and remove existing users
- **View Users Tab**: View all users with filtering by role, domain, and subdomain
- For users: assign domain and subdomain during creation
- Database tables: `admins`, `users`, `guests`, `domains`

## Configuration
- `USE_DB_FOR_AUTH`: Set to `True` for database auth, `False` for Excel auth
- Database tables: `admins`, `users`, `guests`, `domains`

## Architecture
- Documents chunked and embedded in ChromaDB.
- Q&A generated via LLM and stored in SQLite.
- Quizzes: Random questions, scored with pass/fail threshold (70%).
- Modular: Change LLM/DB modules for alternatives.