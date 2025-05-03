from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.models.database import Base, Essay, Evaluation
import os
from typing import Optional, List, Dict, Any
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/ielts_essays")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class DatabaseService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_essay(
        self,
        id: str,
        prompt: str,
        content: str,
        created_at: datetime,
        updated_at: datetime
    ) -> Essay:
        """Create a new essay"""
        db_essay = Essay(
            id=id,
            prompt=prompt,
            content=content,
            created_at=created_at,
            updated_at=updated_at
        )
        self.db.add(db_essay)
        self.db.commit()
        self.db.refresh(db_essay)
        return db_essay
    
    def get_essay(self, essay_id: str) -> Optional[Essay]:
        """Get essay by ID"""
        return self.db.query(Essay).filter(Essay.id == essay_id).first()
    
    def get_essays(self, skip: int = 0, limit: int = 10) -> List[Essay]:
        """Get all essays with pagination"""
        return self.db.query(Essay).offset(skip).limit(limit).all()
    
    def create_evaluation(
        self,
        id: str,
        essay_id: str,
        task_achievement: float,
        coherence_cohesion: float,
        lexical_resource: float,
        grammatical_range: float,
        overall_score: float,
        feedback: str
    ) -> Evaluation:
        """Create a new evaluation"""
        db_evaluation = Evaluation(
            id=id,
            essay_id=essay_id,
            task_achievement=task_achievement,
            coherence_cohesion=coherence_cohesion,
            lexical_resource=lexical_resource,
            grammatical_range=grammatical_range,
            overall_score=overall_score,
            feedback=feedback,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        self.db.add(db_evaluation)
        self.db.commit()
        self.db.refresh(db_evaluation)
        return db_evaluation
    
    def get_evaluation(self, essay_id: str) -> Optional[Evaluation]:
        """Get evaluation by essay ID"""
        return self.db.query(Evaluation).filter(Evaluation.essay_id == essay_id).first()

    def get_all_evaluations(self) -> List[Evaluation]:
        """Get all evaluations"""
        return self.db.query(Evaluation).all() 