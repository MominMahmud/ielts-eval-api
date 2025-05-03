from datasets import load_dataset
from sqlalchemy.orm import Session
from app.models.database import get_db_engine, get_db_session, Essay, User
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_huggingface_dataset(db: Session, dataset_name: str = "ielts-writing-task-2", split: str = "train"):
    """
    Process essays from a Hugging Face dataset and add them to the database
    """
    try:
        # Load the dataset
        logger.info(f"Loading dataset {dataset_name} from Hugging Face...")
        dataset = load_dataset(dataset_name, split=split)
        
        # Ensure system user exists
        system_user = db.query(User).filter(User.username == "system").first()
        if not system_user:
            system_user = User(
                username="system",
                email="system@example.com",
                hashed_password="not_used_for_system"
            )
            db.add(system_user)
            db.commit()
            db.refresh(system_user)
        
        essays_added = 0
        for item in dataset:
            try:
                # Extract essay data (adjust field names based on the dataset structure)
                title = item.get('title', f"essay_{essays_added + 1}")
                prompt = item.get('prompt', '')
                content = item.get('content', '')
                band_score = item.get('band_score', 8.0)  # Default to 8.0 if not provided
                
                # Add to database
                essay = Essay(
                    title=title,
                    prompt=prompt,
                    content=content,
                    user_id=system_user.id,
                    band_score=float(band_score) if band_score else 8.0
                )
                db.add(essay)
                essays_added += 1
                
                if essays_added % 100 == 0:
                    db.commit()
                    logger.info(f"Added {essays_added} essays...")
            
            except Exception as e:
                logger.error(f"Error processing essay: {str(e)}")
                continue
        
        db.commit()
        logger.info(f"Successfully added {essays_added} essays from Hugging Face dataset to the database.")
        
    except Exception as e:
        logger.error(f"Error loading dataset: {str(e)}")
        raise

def main():
    # Initialize database connection
    engine = get_db_engine()
    db = get_db_session(engine)
    
    try:
        # Process the dataset
        process_huggingface_dataset(db)
    finally:
        db.close()

if __name__ == "__main__":
    main() 