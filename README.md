markdown# ÌMỌ̀ — Intelligent Modelling & Omnichannel Recommendation

> DSN × BCT LLM Agent Challenge 2026

A dual-agent LLM system for Nigerian user behaviour modelling and personalised recommendation.

## Live APIs
- **Task A (User Modeling):** https://dsn-bct-task-a.onrender.com/docs
- **Task B (Recommendation):** https://dsn-bct-task-b.onrender.com/docs

## Results
| Metric | Score |
|--------|-------|
| ROUGE-L | 0.0754 |
| RMSE | 1.2649 |
| NDCG@10 | 0.3063 |
| Hit Rate | 0.5000 |

## Project Structure
dsn-bct-challenge/
├── task_a/          # User Modeling Agent
│   ├── agent.py     # Core persona + review simulation
│   └── api.py       # FastAPI endpoint
├── task_b/          # Recommendation Agent
│   ├── agent.py     # Core recommendation logic
│   └── api.py       # FastAPI endpoint
├── data/            # Synthetic Nigerian dataset
│   ├── generate_dataset.py
│   ├── users.json
│   ├── reviews.json
│   └── businesses.json
├── evaluation/      # Evaluation suite
│   ├── evaluate.py
│   └── results.json
└── README.md

## Setup
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Add your `.env` file:
ANTHROPIC_API_KEY=your_key_here

## Run Locally
```bash
# Task A
cd task_a && uvicorn api:app --reload

# Task B  
cd task_b && uvicorn api:app --reload --port 8001

# Evaluation
python evaluation/evaluate.py
```

## Architecture
Both agents share a common **Persona Engine** that extracts behavioural traits
from review history. Task A uses this to simulate authentic Nigerian reviews.
Task B uses it to rank and recommend with explicit reasoning.

## Dataset
Synthetic Yelp-style Nigerian dataset — 200 users, 1,990 reviews, 15 businesses.
Generated with `data/generate_dataset.py`. Disclosed per competition rules.

## Nigerian Contextualisation
Reviews and recommendations are calibrated for Lagos cultural context,
Nigerian English register, and Naira price sensitivity.