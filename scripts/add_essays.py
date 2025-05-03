from sqlalchemy.orm import Session
from app.models.database import get_db_engine, get_db_session, Essay, User
import json

def add_essays_from_json(file_path: str, db: Session):
    """Add essays from a JSON file to the database"""
    with open(file_path, 'r') as f:
        essays = json.load(f)
    
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
    for essay_data in essays:
        essay = Essay(
            title=essay_data['title'],
            prompt=essay_data['prompt'],
            content=essay_data['content'],
            user_id=system_user.id,
            band_score=essay_data.get('band_score', None)  # Optional band score
        )
        db.add(essay)
        essays_added += 1
    
    db.commit()
    print(f"Successfully added {essays_added} essays to the database")

if __name__ == "__main__":
    # Initialize database connection
    engine = get_db_engine()
    db = get_db_session(engine)
    
    # Example usage
    essays_data = [
        {
            "title": "Sample Essay 1",
            "prompt": "Some people believe that...",
            "content": "This is the essay content...",
            "band_score": 8.0
        },
        {
            "title": "Sample Essay 2",
            "prompt": "Another essay prompt...",
            "content": "Another essay content...",
            "band_score": 7.5
        }
    ]
    
    # Save sample data to JSON file
    with open('sample_essays.json', 'w') as f:
        json.dump(essays_data, f, indent=2)
    
    # Add essays from the JSON file
    add_essays_from_json('sample_essays.json', db) 