from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, create_engine, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    essays = relationship("Essay", back_populates="author")

class Essay(Base):
    __tablename__ = "essays"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    prompt = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"))
    band_score = Column(Float)
    author = relationship("User", back_populates="essays")
    
    # Relationship with evaluation
    evaluation = relationship("Evaluation", back_populates="essay", uselist=False)

class Evaluation(Base):
    __tablename__ = "evaluations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    essay_id = Column(String, ForeignKey("essays.id"), nullable=False)
    task_achievement = Column(Float, nullable=False)
    coherence_cohesion = Column(Float, nullable=False)
    lexical_resource = Column(Float, nullable=False)
    grammatical_range = Column(Float, nullable=False)
    overall_score = Column(Float, nullable=False)
    feedback = Column(Text, nullable=False)
    similar_essays = Column(JSON, nullable=True)  # Store similar essays used in RAG
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with essay
    essay = relationship("Essay", back_populates="evaluation")

# Database connection
def get_db_engine():
    POSTGRES_USER = "postgres"
    POSTGRES_PASSWORD = "postgres"
    POSTGRES_HOST = "localhost"
    POSTGRES_PORT = "5432"
    POSTGRES_DB = "ielts_evaluator"
    
    SQLALCHEMY_DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    return engine

def get_db_session(engine):
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()