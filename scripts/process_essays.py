import re
import argparse
from sqlalchemy.orm import Session
from app.models.database import get_db_engine, get_db_session, Essay, User

def process_formatted_essays_file(file_path, db: Session):
    print(f"Processing essays from {file_path}")
    """Process essays from a pre-formatted .txt file with '=== Essay N ===' delimiters"""
    # Ensure the system user exists
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

    # Load file content
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Split essays using the custom delimiter
    essay_blocks = re.split(r"=== Essay \d+ ===", content)
    essays_added = 0

    for i, block in enumerate(essay_blocks):
        block = block.strip()
        if not block:
            continue

        # Split into lines and process
        lines = block.splitlines()
        
        # Extract band score (default to 8.0 if not specified)
        band_score = 8.0
        if lines and lines[0].strip().startswith("Band Score:"):
            try:
                band_score = float(lines[0].strip().split(":")[1].strip())
                lines = lines[1:]  # Remove the band score line
            except (ValueError, IndexError):
                print(f"Warning: Invalid band score format in essay {i+1}, using default 8.0")

        # First remaining line is the prompt, rest is the essay
        prompt = lines[0].strip()
        essay_content = "\n".join(lines[1:]).strip()

        # Add to database
        essay = Essay(
            title=f"essay_{i + 1}",
            prompt=prompt,
            content=essay_content,
            user_id=system_user.id,
            band_score=band_score
        )
        db.add(essay)
        essays_added += 1

        if essays_added % 100 == 0:
            db.commit()

    db.commit()
    print(f"Successfully added {essays_added} formatted essays to the database.")

def main():
    parser = argparse.ArgumentParser(description='Import formatted IELTS essays')
    parser.add_argument('--file', required=True, help='Path to the formatted .txt file')
    args = parser.parse_args()

    engine = get_db_engine()
    db = get_db_session(engine)

    try:
        process_formatted_essays_file(args.file, db)
    finally:
        db.close()

if __name__ == "__main__":
    main()
