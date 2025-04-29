from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import essays

app = FastAPI(
    title="IELTS Essay Evaluator API",
    description="API for evaluating IELTS essays using Gemini API",
    version="1.0.0"
)

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # React frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(essays.router)

@app.get("/")
async def root():
    return {"message": "Welcome to the IELTS Essay Evaluator API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)