from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional, List, Dict, Any

# User schemas
class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Essay schemas
class EssayBase(BaseModel):
    content: str = Field(..., description="The essay content")
    prompt: str = Field(..., description="The essay prompt/question")

class EssayCreate(EssayBase):
    pass

class EssayUpdate(EssayBase):
    pass

# Evaluation schemas
class EvaluationBase(BaseModel):
    task_achievement: float = Field(..., ge=0, le=9, description="Task Achievement score (0-9)")
    coherence_cohesion: float = Field(..., ge=0, le=9, description="Coherence and Cohesion score (0-9)")
    lexical_resource: float = Field(..., ge=0, le=9, description="Lexical Resource score (0-9)")
    grammatical_range: float = Field(..., ge=0, le=9, description="Grammatical Range and Accuracy score (0-9)")
    overall_score: float = Field(..., ge=0, le=9, description="Overall band score (0-9)")
    feedback: str = Field(..., description="Detailed feedback for the essay")

class EvaluationCreate(EvaluationBase):
    essay_id: str

class EvaluationResponse(EvaluationBase):
    id: str
    essay_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class EssayResponse(EssayBase):
    id: str
    created_at: datetime
    updated_at: datetime
    user_id: Optional[str] = None
    band_score: Optional[float] = None
    evaluation: Optional[EvaluationResponse] = None

    class Config:
        from_attributes = True

class ScoreTrend(BaseModel):
    date: str
    overall: float
    task_achievement: float
    coherence_cohesion: float
    lexical_resource: float
    grammatical_range: float

class EvaluationStats(BaseModel):
    average_score: float
    total_evaluations: int
    score_distribution: Dict[int, int]

    class Config:
        from_attributes = True