# Gamified Internal Evaluation Application

This is a Python-based application for internal evaluations with gamification.

## Features
- Admin login to upload documents and generate Q&A using LLM (Google Gemini).
- User login to view theory and take gamified quizzes based on areas.
- Guest access to view theory.
- Modular design for LLM, DB, Auth, Vector DB.
- Configurable settings.

## Tech Stack
- Backend: FastAPI
- Frontend: Streamlit
- LLM: Google Gemini API
- DB: SQLite (configurable)
- Vector DB: ChromaDB
- Auth: Excel-based

## Setup
1. Install Python 3.14.
2. Create venv: `python3.14.exe -m venv venv`
3. Activate: `.\venv\Scripts\Activate.ps1`
4. Install dependencies: `pip install -r requirements.txt`
5. Set GEMINI_API_KEY in `app/config/settings.py`.
6. Sample users in `data/users.xlsx` (created).
7. Run: `streamlit run app/frontend/app.py`

## Usage
- Login as admin (admin1/pass1) to upload documents for areas.
- Login as user (user1/pass1) to view theory for area1 and take quiz.
- Login as guest (guest1/pass1) to view theory.

## Architecture
- Documents chunked and embedded in ChromaDB.
- Q&A generated via LLM and stored in SQLite.
- Quizzes: Random questions, scored with pass/fail threshold (70%).
- Modular: Change LLM/DB modules for alternatives.