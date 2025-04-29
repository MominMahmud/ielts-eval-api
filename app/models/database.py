from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime

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
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200))
    prompt = Column(Text)
    content = Column(Text)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    band_score = Column(Float)
    author = relationship("User", back_populates="essays")
    evaluation = relationship("Evaluation", back_populates="essay", uselist=False)

class Evaluation(Base):
    __tablename__ = "evaluations"
    
    id = Column(Integer, primary_key=True, index=True)
    essay_id = Column(Integer, ForeignKey("essays.id"))
    task_achievement = Column(Float)  # Score 0-9
    coherence_cohesion = Column(Float)  # Score 0-9
    lexical_resource = Column(Float)  # Score 0-9
    grammatical_range = Column(Float)  # Score 0-9
    overall_score = Column(Float)  # Score 0-9
    feedback = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
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