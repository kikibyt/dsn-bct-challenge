from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from agent import simulate_review

app = FastAPI(
    title="DSN x BCT — Task A: User Modeling Agent",
    description="Give us a user's review history + a product, we'll simulate what they'd say.",
    version="1.0.0"
)

# ── CORS — allows frontend to call this API ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PastReview(BaseModel):
    business: str
    rating: int
    review: str

class ProductInput(BaseModel):
    name: str
    category: str
    description: str

class SimulateReviewRequest(BaseModel):
    user_history: List[PastReview]
    product: ProductInput

class SimulateReviewResponse(BaseModel):
    product: str
    simulated_rating: int
    simulated_review: str
    user_persona_summary: str

@app.get("/")
def root():
    return {
        "message": "Task A: User Modeling Agent is running 🚀",
        "endpoints": {
            "simulate_review": "POST /simulate-review",
            "health": "GET /health"
        }
    }

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/simulate-review", response_model=SimulateReviewResponse)
def simulate_review_endpoint(request: SimulateReviewRequest):
    try:
        user_history = [r.model_dump() for r in request.user_history]
        product = request.product.model_dump()
        result = simulate_review(user_history, product)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))