import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database settings
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ielts_evaluator.db")

# API model settings
API_TYPE = "gemini"
API_KEY = "AIzaSyBsd81X11RVaGuNXMElguYnyXpMX5WQKi8"
AI_MODEL = "gemini-1.5-pro"

# Security
SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key_here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# IELTS assessment criteria
ASSESSMENT_CRITERIA = {
    "task_achievement": "Measures how well the essay addresses the question/prompt and develops a position.",
    "coherence_cohesion": "Measures the overall organization, paragraphing, and use of cohesive devices.",
    "lexical_resource": "Measures vocabulary range, accuracy, and appropriateness.",
    "grammatical_range": "Measures grammatical complexity, accuracy, and variety of structures."
}

# Score descriptions for reference
SCORE_DESCRIPTIONS = {
    9: "Expert user",
    8: "Very good user",
    7: "Good user",
    6: "Competent user",
    5: "Modest user",
    4: "Limited user",
    3: "Extremely limited user",
    2: "Intermittent user", 
    1: "Non-user",
    0: "Did not attempt"
}