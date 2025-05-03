from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models import schemas
from app.services.evaluator import EssayEvaluator
from app.services.chroma_service import ChromaService
from app.services.database import DatabaseService, get_db
from fastapi.responses import JSONResponse
import uuid
from datetime import datetime

router = APIRouter(
    prefix="/essays",
    tags=["essays"],
    responses={404: {"description": "Not found"}},
)

# Initialize services
chroma_service = ChromaService()

@router.post("/", response_model=schemas.EssayResponse)
async def create_essay(
    essay: schemas.EssayCreate,
    db: Session = Depends(get_db),
    evaluator: EssayEvaluator = Depends(EssayEvaluator)
):
    """Create a new essay and evaluate it"""
    try:
        # Create essay
        essay_id = str(uuid.uuid4())
        created_at = datetime.utcnow()
        db_service = DatabaseService(db)
        db_essay = db_service.create_essay(
            id=essay_id,
            prompt=essay.prompt,
            content=essay.content,
            created_at=created_at,
            updated_at=created_at
        )

        # Evaluate essay
        evaluation = await evaluator.evaluate_essay(
            essay_content=essay.content,
            essay_prompt=essay.prompt
        )

        # Create evaluation in database
        evaluation_id = str(uuid.uuid4())
        db_evaluation = db_service.create_evaluation(
            id=evaluation_id,
            essay_id=essay_id,
            **evaluation
        )

        return {
            "id": essay_id,
            "content": essay.content,
            "prompt": essay.prompt,
            "created_at": created_at,
            "updated_at": created_at,
            "user_id": None,
            "band_score": None,
            "evaluation": {
                "id": evaluation_id,
                "essay_id": essay_id,
                "task_achievement": evaluation["task_achievement"],
                "coherence_cohesion": evaluation["coherence_cohesion"],
                "lexical_resource": evaluation["lexical_resource"],
                "grammatical_range": evaluation["grammatical_range"],
                "overall_score": evaluation["overall_score"],
                "feedback": evaluation["feedback"],
                "created_at": created_at,
                "updated_at": created_at
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[schemas.EssayResponse])
def list_essays(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """List all essays with their evaluations"""
    db_service = DatabaseService(db)
    essays = db_service.get_essays(skip=skip, limit=limit)
    
    result = []
    for essay in essays:
        evaluation = db_service.get_evaluation(essay.id)
        essay_dict = {
            "id": essay.id,
            "prompt": essay.prompt,
            "content": essay.content,
            "created_at": essay.created_at,
            "updated_at": essay.updated_at,
            "user_id": essay.user_id,
            "band_score": essay.band_score,
            "evaluation": None
        }
        
        if evaluation:
            essay_dict["evaluation"] = {
                "id": evaluation.id,
                "essay_id": evaluation.essay_id,
                "task_achievement": evaluation.task_achievement,
                "coherence_cohesion": evaluation.coherence_cohesion,
                "lexical_resource": evaluation.lexical_resource,
                "grammatical_range": evaluation.grammatical_range,
                "overall_score": evaluation.overall_score,
                "feedback": evaluation.feedback,
                "created_at": evaluation.created_at,
                "updated_at": evaluation.updated_at
            }
        
        result.append(essay_dict)
    return result

@router.get("/stats", response_model=schemas.EvaluationStats)
def get_evaluation_stats(
    db: Session = Depends(get_db)
):
    """Get evaluation statistics"""
    db_service = DatabaseService(db)
    evaluations = db_service.get_all_evaluations()
    
    if not evaluations:
        return schemas.EvaluationStats(
            average_score=0.0,
            total_evaluations=0,
            score_distribution={}
        )
    
    total = len(evaluations)
    average = sum(e.overall_score for e in evaluations) / total
    
    # Create score distribution
    distribution = {}
    for e in evaluations:
        score = int(e.overall_score)
        distribution[score] = distribution.get(score, 0) + 1
    
    return schemas.EvaluationStats(
        average_score=round(average, 2),
        total_evaluations=total,
        score_distribution=distribution
    )

@router.get("/similar", response_model=List[schemas.EssayResponse])
async def get_similar_essays(query: str, limit: int = 5):
    """Get similar essays based on content using ChromaDB"""
    similar_essays = chroma_service.search_similar_essays(query, n_results=limit)
    return [{
        'id': essay['id'],
        'prompt': essay['metadata']['prompt'],
        'content': essay['content'],
        'created_at': essay['metadata']['created_at'],
        'updated_at': essay['metadata']['created_at'],
        'user_id': None,
        'band_score': None,
        'evaluation': None
    } for essay in similar_essays]

@router.get("/{essay_id}", response_model=schemas.EssayResponse)
def get_essay(
    essay_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific essay by ID"""
    db_service = DatabaseService(db)
    essay = db_service.get_essay(essay_id)
    if not essay:
        raise HTTPException(status_code=404, detail="Essay not found")
    
    evaluation = db_service.get_evaluation(essay_id)
    essay_dict = {
        "id": essay.id,
        "prompt": essay.prompt,
        "content": essay.content,
        "created_at": essay.created_at,
        "updated_at": essay.updated_at,
        "user_id": essay.user_id,
        "band_score": essay.band_score,
        "evaluation": None
    }
    
    if evaluation:
        essay_dict["evaluation"] = {
            "id": evaluation.id,
            "essay_id": evaluation.essay_id,
            "task_achievement": evaluation.task_achievement,
            "coherence_cohesion": evaluation.coherence_cohesion,
            "lexical_resource": evaluation.lexical_resource,
            "grammatical_range": evaluation.grammatical_range,
            "overall_score": evaluation.overall_score,
            "feedback": evaluation.feedback,
            "created_at": evaluation.created_at,
            "updated_at": evaluation.updated_at
        }
    
    return essay_dict

@router.get("/{essay_id}/similar", response_model=List[schemas.EssayResponse])
def get_similar_essays_endpoint(essay_id: int, db: Session = Depends(get_db)):
    essay = db.query(Essay).filter(Essay.id == essay_id).first()
    if essay is None:
        raise HTTPException(status_code=404, detail="Essay not found")
    
    similar_essays = get_similar_essays(essay.content)
    return [schemas.EssayResponse.from_orm(essay) for essay in similar_essays]