# VM Internal Transition Evaluation Tool - Architecture & Flow

## Overview

A gamified internal evaluation application built for domain-based quizzes and content management. Admins upload documents, AI generates Q&A, users take domain-specific quizzes, and results are tracked.

## Tech Stack

### Core Technologies

- **Language**: Python 3.14
- **Frontend**: Streamlit (interactive web UI)
- **Backend**: FastAPI (minimal use, extensible)
- **Database**: SQLite (relational data storage)
- **Vector Database**: ChromaDB (embeddings for future AI features)
- **LLM**: Google Gemini API (Q&A generation)

### Libraries & Frameworks

- **ORM**: SQLAlchemy (database models and queries)
- **Data Processing**: Pandas, OpenPyXL (Excel handling for auth)
- **Document Parsing**: PyPDF2 (PDF), python-docx (DOCX)
- **AI/ML**: google-generativeai (Gemini integration)
- **Vector Ops**: ChromaDB (embeddings)
- **Utilities**: json, random, os, sys

### Infrastructure

- **Environment**: Virtual environment (venv)
- **Configuration**: Python settings file
- **Authentication**: Excel-based (admin/users/guest sheets)
- **Deployment**: Local Streamlit app

## Architecture Overview

### Modular Structure

```
app/
├── config/
│   └── settings.py          # Configurable constants
├── modules/
│   ├── auth_module.py       # User authentication & domain management
│   ├── db_module.py         # SQLAlchemy models & database operations
│   ├── llm_module.py        # Gemini API integration & Q&A generation
│   └── vector_db_module.py  # ChromaDB embeddings & retrieval
└── frontend/
    └── app.py               # Main Streamlit application
```

### Data Flow

1. **Input**: Documents uploaded via Streamlit UI
2. **Processing**: Text extraction → Chunking → Q&A Generation
3. **Storage**: SQLite (structured data), Todo: ChromaDB (embeddings)
4. **Retrieval**: Domain-based filtering from SQLite
5. **Output**: Streamlit UI displays quizzes, results

## Application Flow

### 1. Login Process

- User selects role (admin/user/guest), enters credentials
- Authenticates against Excel sheets (`data/users.xlsx`)
- Session state stores role, username, domain (for users)

### 2. Admin Panel

- **Upload Document**:
  - Select/create domain
  - Upload PDF/TXT/DOCX
  - Process: Extract text → Chunk →Generate Q&A → Store in DB
- **Manage Content**:
  - View domain-specific documents, Q&A, quiz results
  - Delete individual entries or clear entire domains

### 3. User Quiz Flow

- Filter content by user's domain (from Excel)
- Display quiz: Random Q&A selection, progress tracking
- Submit answers: Immediate feedback, score calculation
- Results: Percentage, pass/fail (70% threshold), store in DB
- No retake option (one-time quiz)

### 4. Guest View

- View all areas' Q&A (questions only)
- No quiz access

## Document Processing Pipeline

### Step 1: Upload & Extraction

```python
# Extract text based on file type
if uploaded_file.type == "application/pdf":
    content = PyPDF2.PdfReader(uploaded_file).extract_text()
elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
    content = docx.Document(uploaded_file).text
else:
    content = uploaded_file.read().decode("utf-8")
```

### Step 2: Chunking

- Split text into chunks (1000 chars, 200 overlap)
- Purpose: Handle large documents, prepare for embeddings

### Step 3: Embedding & Storage

- Generate embeddings using ChromaDB
- Store with domain metadata (for future retrieval)

### Step 4: Q&A Generation

- Estimate token count (len(text) // 4)
- If > 4000 tokens: Chunk further and generate Q&A per chunk
- Send prompt to Gemini API:

```python
prompt = f"Generate {QA_PER_CHUNK} multiple choice questions from the following text..."
response = model.generate_content(prompt)
qa_list = json.loads(response.text)
```

- Parse JSON response into question/options/answer format

### Step 5: Database Storage

- Store document in `documents` table
- Store Q&A in `qa` table (linked by `document_id`)
- All Q&A from chunks share same document metadata

## LLM Integration

### Prompt Engineering

- **Input**: Text chunk + instruction to generate multiple-choice Q&A
- **Format**: JSON array with question, options (4 choices), answer
- **Config**: `QA_PER_CHUNK` (default 10) controls Q&A count per chunk

### API Interaction

```python
import google.generativeai as genai
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(LLM_MODEL)
response = model.generate_content(prompt)
```

### Response Handling

- Strip markdown formatting (`response.text.strip('```json\n')`)
- Parse JSON, handle errors gracefully
- Return list of Q&A objects

## Database Schema and Operations

### Tables

- **documents**: `id`, `area`, `domain`, `content`
- **qa**: `id`, `document_id`, `question`, `options` (JSON), `answer`
- **quiz_results**: `id`, `username`, `area`, `score`, `total`, `passed`

### Key Operations

- **Storage**: SQLAlchemy ORM creates tables, adds records
- **Retrieval**: Domain-based queries (e.g., `filter(Document.domain == user_domain)`)
- **Relationships**: QA linked to documents via foreign key

### Authentication

- Excel sheets: `admin`, `users` (with domain), `guest`
- Domains managed in `domains` sheet

## User Roles and Permissions

### Admin

- Upload documents to domains
- Create new domains
- View/manage all domain content
- Delete documents, Q&A, quiz results

### User

- Access domain-specific quizzes only
- Take one-time quiz, view results
- No theory preview, no retakes

### Guest

- View Q&A (questions only) across all areas
- No quiz access

## Configuration

### settings.py

```python
GEMINI_API_KEY = "your_key"
DB_URL = "sqlite:///evaluation.db"
CHUNK_SIZE = 1000
OVERLAP = 200
QA_PER_CHUNK = 10
QUESTIONS_PER_QUIZ = 20
THRESHOLD = 0.7  # 70% to pass
```

### Excel Files

- `data/users.xlsx`: Authentication and domains
- `evaluation.db`: SQLite database

## Current Features

- ✅ Domain-based content isolation
- ✅ AI-powered Q&A generation
- ✅ Gamified quiz interface
- ✅ Admin content management
- ✅ User authentication via Excel
- ✅ Large document chunking
- ✅ Configurable settings
- ✅ Professional UI with branding

## Future Enhancements

- Integrate ChromaDB for dynamic Q&A retrieval
- Add quiz timers and hints
- Implement full FastAPI backend
- Support more file types
- Advanced analytics dashboard
- Multi-language support

---

*Built with Streamlit, powered by Google Gemini AI, and designed for scalable internal evaluations.*
