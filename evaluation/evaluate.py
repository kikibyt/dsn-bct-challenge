import json
import numpy as np
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rouge_score import rouge_scorer
from task_a.agent import simulate_review
from task_b.agent import recommend

# ── TASK A EVALUATION ──

def evaluate_task_a(num_samples: int = 10):
    """
    For each test user:
    - Take their first N-1 reviews as history
    - Simulate a review for their Nth business
    - Compare simulated review to actual review using ROUGE
    - Compare simulated rating to actual rating using RMSE
    """
    print("\n" + "="*50)
    print("TASK A EVALUATION — User Modeling")
    print("="*50)

    reviews = json.load(open("data/reviews.json"))
    
    # Group reviews by user
    user_reviews = {}
    for r in reviews:
        uid = r["user_id"]
        if uid not in user_reviews:
            user_reviews[uid] = []
        user_reviews[uid].append(r)
    
    # Filter users with at least 5 reviews
    eligible = {k: v for k, v in user_reviews.items() if len(v) >= 5}
    test_users = list(eligible.items())[:num_samples]
    
    scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
    
    rouge1_scores = []
    rouge2_scores = []
    rougeL_scores = []
    rmse_values = []
    
    businesses = json.load(open("data/businesses.json"))
    biz_lookup = {b["business_id"]: b for b in businesses}
    
    print(f"\nEvaluating {num_samples} users...\n")
    
    for user_id, user_review_list in test_users:
        # Split: history = first N-1, test = last 1
        history = user_review_list[:-1]
        test_review = user_review_list[-1]
        
        # Format history for agent
        history_input = [
            {
                "business": r["business_name"],
                "rating": r["stars"],
                "review": r["text"]
            }
            for r in history
        ]
        
        # Get the business details
        biz = biz_lookup.get(test_review["business_id"], {})
        product = {
            "name": test_review["business_name"],
            "category": test_review["category"],
            "description": biz.get("name", test_review["business_name"])
        }
        
        try:
            result = simulate_review(history_input, product)
            
            # ROUGE scores
            scores = scorer.score(
                test_review["text"],           # reference (actual)
                result["simulated_review"]     # hypothesis (simulated)
            )
            
            rouge1_scores.append(scores["rouge1"].fmeasure)
            rouge2_scores.append(scores["rouge2"].fmeasure)
            rougeL_scores.append(scores["rougeL"].fmeasure)
            
            # RMSE
            rmse_values.append((result["simulated_rating"] - test_review["stars"]) ** 2)
            
            print(f"User {user_id} | Actual: {test_review['stars']}★ | Simulated: {result['simulated_rating']}★ | ROUGE-L: {scores['rougeL'].fmeasure:.3f}")
        
        except Exception as e:
            print(f"User {user_id} — Error: {e}")
            continue
    
    # Final scores
    print("\n" + "-"*50)
    print("TASK A RESULTS")
    print("-"*50)
    print(f"ROUGE-1:  {np.mean(rouge1_scores):.4f}")
    print(f"ROUGE-2:  {np.mean(rouge2_scores):.4f}")
    print(f"ROUGE-L:  {np.mean(rougeL_scores):.4f}")
    print(f"RMSE:     {np.sqrt(np.mean(rmse_values)):.4f}")
    
    return {
        "rouge1": round(np.mean(rouge1_scores), 4),
        "rouge2": round(np.mean(rouge2_scores), 4),
        "rougeL": round(np.mean(rougeL_scores), 4),
        "rmse": round(np.sqrt(np.mean(rmse_values)), 4)
    }


# ── TASK B EVALUATION ──

def ndcg_at_k(recommended_ids: list, relevant_ids: list, k: int = 10) -> float:
    """Calculate NDCG@10."""
    def dcg(ids):
        score = 0.0
        for i, item_id in enumerate(ids[:k]):
            rel = 1 if item_id in relevant_ids else 0
            score += rel / np.log2(i + 2)
        return score
    
    ideal = sorted([1]*len(relevant_ids) + [0]*(k - len(relevant_ids)), reverse=True)
    ideal_dcg = sum(ideal[i] / np.log2(i + 2) for i in range(min(k, len(ideal))))
    
    actual_dcg = dcg(recommended_ids)
    return actual_dcg / ideal_dcg if ideal_dcg > 0 else 0.0


def evaluate_task_b(num_samples: int = 10):
    """
    For each test user:
    - Use their review history as persona
    - Get recommendations
    - Compare against businesses they actually rated 4+ stars
    """
    print("\n" + "="*50)
    print("TASK B EVALUATION — Recommendation")
    print("="*50)

    reviews = json.load(open("data/reviews.json"))
    businesses = json.load(open("data/businesses.json"))
    
    # Group by user
    user_reviews = {}
    for r in reviews:
        uid = r["user_id"]
        if uid not in user_reviews:
            user_reviews[uid] = []
        user_reviews[uid].append(r)
    
    eligible = {k: v for k, v in user_reviews.items() if len(v) >= 5}
    test_users = list(eligible.items())[:num_samples]
    
    ndcg_scores = []
    hit_rates = []
    
    print(f"\nEvaluating {num_samples} users...\n")
    
    for user_id, user_review_list in test_users:
        # History = first N-2, ground truth = last 2 (businesses they liked)
        history = user_review_list[:-2]
        held_out = user_review_list[-2:]
        
        # Relevant = held out businesses they rated 4+
        relevant_ids = [r["business_id"] for r in held_out if r["stars"] >= 4]
        
        if not relevant_ids:
            continue
        
        history_input = [
            {"business": r["business_name"], "rating": r["stars"], "review": r["text"]}
            for r in history
        ]
        
        context = {"occasion": "casual dining", "location": "Lagos", "budget": "any", "mood": "hungry"}
        
        try:
            result = recommend(history_input, context)
            
            # Extract recommended business names and match to IDs
            recommended_names = [rec.get("name", "") for rec in result["recommendations"]]
            biz_name_to_id = {b["name"]: b["business_id"] for b in businesses}
            recommended_ids = [biz_name_to_id.get(name, "") for name in recommended_names]
            
            # NDCG@10
            ndcg = ndcg_at_k(recommended_ids, relevant_ids, k=10)
            ndcg_scores.append(ndcg)
            
            # Hit Rate — did any recommendation match?
            hit = any(rid in relevant_ids for rid in recommended_ids)
            hit_rates.append(1 if hit else 0)
            
            print(f"User {user_id} | Relevant: {len(relevant_ids)} | Hit: {'✅' if hit else '❌'} | NDCG: {ndcg:.3f}")
        
        except Exception as e:
            print(f"User {user_id} — Error: {e}")
            continue
    
    print("\n" + "-"*50)
    print("TASK B RESULTS")
    print("-"*50)
    print(f"NDCG@10:   {np.mean(ndcg_scores):.4f}")
    print(f"Hit Rate:  {np.mean(hit_rates):.4f}")
    
    return {
        "ndcg_at_10": round(np.mean(ndcg_scores), 4),
        "hit_rate": round(np.mean(hit_rates), 4)
    }


if __name__ == "__main__":
    print("ÌMỌ̀ — Evaluation Suite")
    print("Synthetic Yelp-style Nigerian dataset | 200 users | 1,990 reviews")
    
    task_a = evaluate_task_a(num_samples=10)
    task_b = evaluate_task_b(num_samples=10)
    
    print("\n" + "="*50)
    print("FINAL SCORECARD")
    print("="*50)
    print(f"Task A — ROUGE-1:  {task_a['rouge1']}")
    print(f"Task A — ROUGE-2:  {task_a['rouge2']}")
    print(f"Task A — ROUGE-L:  {task_a['rougeL']}")
    print(f"Task A — RMSE:     {task_a['rmse']}")
    print(f"Task B — NDCG@10:  {task_b['ndcg_at_10']}")
    print(f"Task B — Hit Rate: {task_b['hit_rate']}")
    
    # Save results
    import json
    with open("evaluation/results.json", "w") as f:
        json.dump({"task_a": task_a, "task_b": task_b}, f, indent=2)
    print("\n✅ Results saved to evaluation/results.json")