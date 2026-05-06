from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from agent import recommend

app = FastAPI(
    title="DSN x BCT — Task B: Recommendation Agent",
    description="Give us a user's review history, we'll recommend what they'll love next.",
    version="1.0.0"
)

class PastReview(BaseModel):
    business: str
    rating: int
    review: str

class ContextInput(BaseModel):
    occasion: Optional[str] = None
    location: Optional[str] = None
    budget: Optional[str] = None
    mood: Optional[str] = None

class RecommendRequest(BaseModel):
    user_history: List[PastReview]
    context: Optional[ContextInput] = None

class Recommendation(BaseModel):
    id: str
    name: str
    confidence: str
    why: str
    pitch: str

class RecommendResponse(BaseModel):
    user_persona: str
    context: dict
    recommendations: List[Recommendation]


@app.get("/")
def root():
    return {
        "message": "Task B: Recommendation Agent is running 🚀",
        "endpoints": {
            "recommend": "POST /recommend",
            "health": "GET /health"
        }
    }

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/recommend", response_model=RecommendResponse)
def recommend_endpoint(request: RecommendRequest):
    try:
        user_history = [r.model_dump() for r in request.user_history]
        context = request.context.model_dump() if request.context else None
        
        result = recommend(user_history, context)
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))