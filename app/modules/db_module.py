# DB Module
from sqlalchemy import create_engine, Column, Integer, String, Text, Float, ForeignKey, DateTime, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from app.config.settings import DB_URL
from datetime import datetime

engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True)
    area = Column(String)
    domain = Column(String)  # For filtering
    subdomain = Column(String)
    content = Column(Text)
    source = Column(String)
    chunks = relationship("Chunk", back_populates="document")
    qas = relationship("QA", back_populates="document")


def ensure_document_source_column():
    with engine.begin() as conn:
        result = conn.execute(text("PRAGMA table_info(documents)"))
        columns = [row[1] for row in result]
        if columns and "source" not in columns:
            conn.execute(text("ALTER TABLE documents ADD COLUMN source VARCHAR"))


def ensure_document_subdomain_column():
    with engine.begin() as conn:
        result = conn.execute(text("PRAGMA table_info(documents)"))
        columns = [row[1] for row in result]
        if columns and "subdomain" not in columns:
            conn.execute(text("ALTER TABLE documents ADD COLUMN subdomain VARCHAR"))


class Chunk(Base):
    __tablename__ = "chunks"
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    index = Column(Integer)
    content = Column(Text)
    source = Column(String)
    metadata_json = Column(Text)  # JSON string for chunk metadata
    document = relationship("Document", back_populates="chunks")
    qas = relationship("QA", back_populates="chunk")

class QA(Base):
    __tablename__ = "qa"
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    chunk_id = Column(Integer, ForeignKey("chunks.id"), nullable=True)
    question = Column(Text)
    options = Column(Text)  # JSON string
    answer = Column(String)
    document = relationship("Document", back_populates="qas")
    chunk = relationship("Chunk", back_populates="qas")

class QuizResult(Base):
    __tablename__ = "quiz_results"
    id = Column(Integer, primary_key=True)
    username = Column(String)
    area = Column(String)
    subdomain = Column(String)
    score = Column(Float)
    total = Column(Integer)
    passed = Column(Integer)  # 1 or 0

class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"
    id = Column(Integer, primary_key=True)
    username = Column(String)
    domain = Column(String)
    subdomain = Column(String)
    attempted_at = Column(DateTime, default=datetime.utcnow)
    # Composite key: username + domain = one attempt per user per domain

class UserStats(Base):
    __tablename__ = "user_stats"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    total_quizzes = Column(Integer, default=0)
    highest_score = Column(Float, default=0)
    total_correct = Column(Integer, default=0)
    total_questions = Column(Integer, default=0)
    badges = Column(Text, default="")  # JSON list of badge names
    longest_streak = Column(Integer, default=0)
    current_streak = Column(Integer, default=0)

Base.metadata.create_all(bind=engine)


def ensure_qa_chunk_id_column():
    with engine.begin() as conn:
        result = conn.execute(text("PRAGMA table_info(qa)"))
        columns = [row[1] for row in result]
        if columns and "chunk_id" not in columns:
            conn.execute(text("ALTER TABLE qa ADD COLUMN chunk_id INTEGER"))


def ensure_quizattempt_subdomain_column():
    with engine.begin() as conn:
        result = conn.execute(text("PRAGMA table_info(quiz_attempts)"))
        columns = [row[1] for row in result]
        if columns and "subdomain" not in columns:
            conn.execute(text("ALTER TABLE quiz_attempts ADD COLUMN subdomain VARCHAR"))


def ensure_quizresult_subdomain_column():
    with engine.begin() as conn:
        result = conn.execute(text("PRAGMA table_info(quiz_results)"))
        columns = [row[1] for row in result]
        if columns and "subdomain" not in columns:
            conn.execute(text("ALTER TABLE quiz_results ADD COLUMN subdomain VARCHAR"))

ensure_document_source_column()
ensure_document_subdomain_column()
ensure_qa_chunk_id_column()
ensure_quizattempt_subdomain_column()
ensure_quizresult_subdomain_column()

def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()