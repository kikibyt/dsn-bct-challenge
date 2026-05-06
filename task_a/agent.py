import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic()

def build_user_persona(user_history: list[dict]) -> str:
    """Convert user review history into a persona description."""
    
    persona_prompt = f"""
    Analyze these past reviews from a user and write a short persona summary 
    describing their taste, tone, and rating behaviour.
    
    Past Reviews:
    {user_history}
    
    Write a 3-4 sentence persona. Be specific about:
    - What they love and hate
    - Their typical rating pattern (harsh, generous, balanced)
    - Their writing tone (casual, formal, expressive, brief)
    """
    
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        messages=[{"role": "user", "content": persona_prompt}]
    )
    
    return response.content[0].text


def simulate_review(user_history: list[dict], product: dict) -> dict:
    """
    Given a user's review history and a new product,
    simulate what rating and review they would write.
    """
    
    # Step 1: Build persona from history
    persona = build_user_persona(user_history)
    
    # Step 2: Calculate rating stats from history
    ratings = [r['rating'] for r in user_history]
    avg_rating = sum(ratings) / len(ratings)
    best = max(user_history, key=lambda x: x['rating'])
    worst = min(user_history, key=lambda x: x['rating'])
    
    # Step 2: Simulate the review
    review_prompt = f"""
    You are simulating a real Nigerian user's review of a product/place.
    
    USER PERSONA:
    {persona}
    
    THEIR RATING HISTORY:
    - Average rating they give: {avg_rating:.1f} stars
    - They loved: {best['business']} ({best['rating']} stars) — "{best['review']}"
    - They disliked: {worst['business']} ({worst['rating']} stars) — "{worst['review']}"
    
    NEW PRODUCT/PLACE TO REVIEW:
    Name: {product['name']}
    Category: {product['category']}
    Description: {product['description']}
    
    RATING INSTRUCTIONS — follow strictly:
    - If this place matches what they LOVE (authentic, homestyle, good value) → rate 4 or 5
    - If this place matches what they HATE (slow, dry food, overpriced) → rate 1 or 2
    - Stay close to their average rating of {avg_rating:.1f} unless strong reason to deviate
    - A polarised rater should give 1, 2, 4, or 5 — rarely 3
    - A balanced rater can give 3
    
    REVIEW INSTRUCTIONS:
    - Write exactly as this user writes — match their tone, vocabulary, length
    - Sound authentically Nigerian where natural
    - Reference specific things about this place that would trigger their known reactions
    - Do NOT sound like an AI
    
    Respond in this exact format:
    RATING: [number 1-5]
    REVIEW: [the review text]
    """
    
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=400,
        messages=[{"role": "user", "content": review_prompt}]
    )
    
    raw_output = response.content[0].text
    
    # Parse the response
    lines = raw_output.strip().split('\n')
    rating = None
    review_text = ""
    
    for i, line in enumerate(lines):
        if line.startswith("RATING:"):
            try:
                rating = int(line.replace("RATING:", "").strip())
            except:
                rating = round(avg_rating)
        elif line.startswith("REVIEW:"):
            review_text = line.replace("REVIEW:", "").strip()
            for j in range(i+1, len(lines)):
                review_text += " " + lines[j].strip()
    
    # Fallback if parsing fails
    if rating is None:
        rating = round(avg_rating)
    
    return {
        "product": product['name'],
        "simulated_rating": rating,
        "simulated_review": review_text,
        "user_persona_summary": persona
    }

# ---- TEST IT RIGHT HERE ----
if __name__ == "__main__":
    
    # Sample user history (like what Yelp data looks like)
    sample_user_history = [
        {
            "business": "Chicken Republic Lekki",
            "rating": 2,
            "review": "The chicken was dry and the service was so slow. I waited 25 minutes for fast food. Never again."
        },
        {
            "business": "Nkoyo Restaurant",
            "rating": 5,
            "review": "This place ehn! The ofe akwu was exactly like my mama used to make. Will definitely be back."
        },
        {
            "business": "Dominos VI",
            "rating": 3,
            "review": "Pizza was okay. Nothing special. They forgot my extra cheese which annoyed me."
        }
    ]
    
    # New product to simulate a review for
    new_product = {
        "name": "Sky Restaurant Ikeja",
        "category": "Nigerian Fine Dining",
        "description": "Upscale Nigerian cuisine in Ikeja GRA. Known for pepper soup, grilled fish and live music on weekends."
    }
    
    print("🤖 Running User Modeling Agent...\n")
    result = simulate_review(sample_user_history, new_product)
    
    print(f"Product: {result['product']}")
    print(f"Simulated Rating: {'⭐' * result['simulated_rating']} ({result['simulated_rating']}/5)")
    print(f"\nSimulated Review:\n{result['simulated_review']}")
    print(f"\nUser Persona:\n{result['user_persona_summary']}")