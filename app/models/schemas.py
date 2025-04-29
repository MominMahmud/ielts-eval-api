from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional, List, Dict

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
    title: str
    prompt: str
    content: str

class EssayCreate(EssayBase):
    pass

class EssayResponse(EssayBase):
    id: int
    created_at: datetime
    band_score: Optional[float] = None
    
    class Config:
        from_attributes = True

# Evaluation schemas
class EvaluationBase(BaseModel):
    task_achievement: float = Field(..., ge=0, le=9)
    coherence_cohesion: float = Field(..., ge=0, le=9)
    lexical_resource: float = Field(..., ge=0, le=9)
    grammatical_range: float = Field(..., ge=0, le=9)
    overall_score: float = Field(..., ge=0, le=9)
    feedback: str

class EvaluationCreate(EvaluationBase):
    pass

class EvaluationResponse(EvaluationBase):
    id: int
    essay_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Essay with evaluation schema
class EssayWithEvaluation(EssayResponse):
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
    total_evaluations: int
    average_scores: Dict[str, float]
    best_scores: Dict[str, float]
    score_trend: List[ScoreTrend]

    class Config:
        json_encoders = {
            datetime: lambda dt: dt.strftime("%Y-%m-%d %H:%M")
        }