from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from app.models.database import get_db_engine, get_db_session
from app.models import schemas
from app.models.database import Essay, Evaluation
from app.services.evaluator import EssayEvaluator
from fastapi.responses import JSONResponse

router = APIRouter(
    prefix="/api/essays",
    tags=["essays"],
    responses={404: {"description": "Not found"}},
)

# Initialize database engine
engine = get_db_engine()

# Initialize evaluator service
evaluator = EssayEvaluator()

def get_db():
    db = get_db_session(engine)
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=schemas.EssayResponse, status_code=status.HTTP_201_CREATED)
async def create_essay(essay: schemas.EssayCreate, db: Session = Depends(get_db)):
    """Create a new essay"""
    # In a real app, get user_id from auth token
    user_id = 1  # Placeholder
    
    db_essay = Essay(
        title=essay.title,
        prompt=essay.prompt,
        content=essay.content,
        user_id=user_id,
    )
    
    db.add(db_essay)
    db.commit()
    db.refresh(db_essay)
    
    return db_essay

@router.get("/", response_model=List[schemas.EssayResponse])
async def list_essays(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """List essays with optional filtering"""
    query = db.query(Essay)
    
    essays = query.offset(skip).limit(limit).all()
    return essays

@router.get("/all", response_model=List[schemas.EssayWithEvaluation])
async def get_all_essays_with_evaluations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all essays with their evaluations"""
    # Get total count
    total = db.query(Essay).filter(Essay.evaluation != None).count()
    
    # Get paginated results
    essays = db.query(Essay).filter(
        Essay.evaluation != None
    ).order_by(Essay.created_at.desc()).offset(skip).limit(limit).all()
    
    # Add total count to response headers
    response = JSONResponse(content=[essay.dict() for essay in essays])
    response.headers["X-Total-Count"] = str(total)
    return response

@router.get("/reference/sample", response_model=List[schemas.EssayResponse])
async def get_sample_reference_essays(band_score: Optional[float] = None, limit: int = 5, db: Session = Depends(get_db)):
    """Get sample reference essays optionally filtered by band score"""
    query = db.query(Essay).all()
    
    if band_score:
        query = query.filter(Essay.band_score == band_score)
    
    essays = query.order_by(func.random()).limit(limit).all()
    return essays

@router.get("/evaluations", response_model=List[schemas.EssayWithEvaluation])
async def get_user_evaluations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all evaluations for the current user"""
    # In a real app, get user_id from auth token
    user_id = 1  # Placeholder
    
    essays = db.query(Essay).filter(
        Essay.user_id == user_id,
        Essay.evaluation != None
    ).order_by(Essay.created_at.desc()).offset(skip).limit(limit).all()
    
    return essays

@router.get("/stats", response_model=schemas.EvaluationStats)
async def get_evaluation_stats(db: Session = Depends(get_db)):
    """Get evaluation statistics for the current user"""
    # In a real app, get user_id from auth token
    user_id = 1  # Placeholder
    
    # Get all evaluations for the user
    evaluations = db.query(Evaluation).join(Essay).filter(
        Essay.user_id == user_id
    ).all()
    
    if not evaluations:
        return {
            "total_evaluations": 0,
            "average_scores": {
                "overall": 0,
                "task_achievement": 0,
                "coherence_cohesion": 0,
                "lexical_resource": 0,
                "grammatical_range": 0
            },
            "best_scores": {
                "overall": 0,
                "task_achievement": 0,
                "coherence_cohesion": 0,
                "lexical_resource": 0,
                "grammatical_range": 0
            },
            "score_trend": []
        }
    
    # Calculate averages
    total = len(evaluations)
    avg_scores = {
        "overall": sum(e.overall_score for e in evaluations) / total,
        "task_achievement": sum(e.task_achievement for e in evaluations) / total,
        "coherence_cohesion": sum(e.coherence_cohesion for e in evaluations) / total,
        "lexical_resource": sum(e.lexical_resource for e in evaluations) / total,
        "grammatical_range": sum(e.grammatical_range for e in evaluations) / total
    }
    
    # Find best scores
    best_scores = {
        "overall": max(e.overall_score for e in evaluations),
        "task_achievement": max(e.task_achievement for e in evaluations),
        "coherence_cohesion": max(e.coherence_cohesion for e in evaluations),
        "lexical_resource": max(e.lexical_resource for e in evaluations),
        "grammatical_range": max(e.grammatical_range for e in evaluations)
    }
    
    # Get score trend (last 10 evaluations)
    recent_evaluations = db.query(Essay, Evaluation).join(Evaluation).filter(
        Essay.user_id == user_id
    ).order_by(Essay.created_at.desc()).limit(10).all()
    
    score_trend = [
        {
            "date": essay.created_at.strftime("%Y-%m-%d %H:%M"),
            "overall": evaluation.overall_score,
            "task_achievement": evaluation.task_achievement,
            "coherence_cohesion": evaluation.coherence_cohesion,
            "lexical_resource": evaluation.lexical_resource,
            "grammatical_range": evaluation.grammatical_range
        }
        for essay, evaluation in recent_evaluations
    ]
    
    return {
        "total_evaluations": total,
        "average_scores": avg_scores,
        "best_scores": best_scores,
        "score_trend": score_trend
    }

@router.get("/{essay_id}", response_model=schemas.EssayWithEvaluation)
async def get_essay(essay_id: int, db: Session = Depends(get_db)):
    """Get essay by ID with its evaluation if available"""
    essay = db.query(Essay).filter(Essay.id == essay_id).first()
    
    if not essay:
        raise HTTPException(status_code=404, detail="Essay not found")
    
    return essay

@router.post("/{essay_id}/evaluate", response_model=schemas.EvaluationResponse)
async def evaluate_essay(essay_id: int, db: Session = Depends(get_db)):
    """Evaluate an essay using the Gemini API"""
    essay = db.query(Essay).filter(Essay.id == essay_id).first()
    
    if not essay:
        raise HTTPException(status_code=404, detail="Essay not found")
    
    # Check if evaluation already exists
    existing_evaluation = db.query(Evaluation).filter(Evaluation.essay_id == essay_id).first()
    if existing_evaluation:
        return existing_evaluation
    
    # Get evaluation from the model
    try:
        evaluation_results = await evaluator.evaluate_essay(db, essay.title, essay.content)
        
        # Create evaluation record
        evaluation = Evaluation(
            essay_id=essay_id,
            task_achievement=evaluation_results["task_achievement"],
            coherence_cohesion=evaluation_results["coherence_cohesion"],
            lexical_resource=evaluation_results["lexical_resource"],
            grammatical_range=evaluation_results["grammatical_range"],
            overall_score=evaluation_results["overall_score"],
            feedback=evaluation_results["feedback"]
        )
        
        db.add(evaluation)
        db.commit()
        db.refresh(evaluation)
        
        return evaluation
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to evaluate essay: {str(e)}"
        )