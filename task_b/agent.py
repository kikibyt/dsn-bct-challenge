import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic()

def build_user_persona(user_history: list[dict]) -> str:
    """Build user persona from review history."""
    
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

load_dotenv()

client = Anthropic()

# Our product catalogue — this simulates a database
# In production you'd pull from Yelp/Amazon dataset
PRODUCT_CATALOGUE = [
    {
        "id": "1",
        "name": "Nkoyo Restaurant Lekki",
        "category": "Traditional Nigerian",
        "description": "Authentic Niger Delta cuisine. Famous for banga soup, starch and fresh catfish.",
        "price_range": "₦3,000 - ₦8,000",
        "location": "Lekki Phase 1"
    },
    {
        "id": "2", 
        "name": "Craft Grill VI",
        "category": "Continental/Grill",
        "description": "Premium grilled meats and continental dishes. Known for ribeye steak and craft cocktails.",
        "price_range": "₦15,000 - ₦40,000",
        "location": "Victoria Island"
    },
    {
        "id": "3",
        "name": "Yellow Chilli Ikeja",
        "category": "Nigerian Contemporary",
        "description": "Modern Nigerian cuisine by Chef Nkesi. Try the deconstructed egusi and jollof risotto.",
        "price_range": "₦8,000 - ₦20,000",
        "location": "Ikeja GRA"
    },
    {
        "id": "4",
        "name": "Chicken Republic Yaba",
        "category": "Fast Food",
        "description": "Nigerian fast food chain. Fried chicken, jollof rice, burgers and sides.",
        "price_range": "₦1,500 - ₦4,000",
        "location": "Yaba"
    },
    {
        "id": "5",
        "name": "Okrika Mama's Kitchen",
        "category": "Homestyle Nigerian",
        "description": "No-frills homestyle cooking. Pepper soup, ofe onugbu, fresh fish stew daily.",
        "price_range": "₦2,000 - ₦5,000",
        "location": "Surulere"
    },
    {
        "id": "6",
        "name": "Cafe Neo Ikoyi",
        "category": "Cafe/Brunch",
        "description": "Specialty coffee, avocado toast, smoothie bowls and light Nigerian fusion bites.",
        "price_range": "₦3,000 - ₦10,000",
        "location": "Ikoyi"
    },
    {
        "id": "7",
        "name": "Buka Hut Mainland",
        "category": "Buka/Street Food",
        "description": "Classic Lagos buka experience. Amala, ewedu, gbegiri, assorted meats.",
        "price_range": "₦800 - ₦2,500",
        "location": "Mushin"
    },
    {
        "id": "8",
        "name": "Terra Kulture VI",
        "category": "Cultural Dining",
        "description": "Art gallery and restaurant. Afang soup, eba, cultural exhibitions and live performances.",
        "price_range": "₦5,000 - ₦15,000",
        "location": "Victoria Island"
    }
]


def recommend(user_history: list[dict], context: dict = None) -> dict:
    """
    Given user history and optional context,
    return personalised ranked recommendations.
    """
    
    # Step 1: Build persona
    persona = build_user_persona(user_history)
    
    # Step 2: Format catalogue for the agent
    catalogue_text = ""
    for p in PRODUCT_CATALOGUE:
        catalogue_text += f"""
        ID: {p['id']}
        Name: {p['name']}
        Category: {p['category']}
        Description: {p['description']}
        Price Range: {p['price_range']}
        Location: {p['location']}
        ---"""
    
    # Step 3: Build context string
    context_text = ""
    if context:
        context_text = f"""
        CURRENT CONTEXT:
        - Occasion: {context.get('occasion', 'Not specified')}
        - Location preference: {context.get('location', 'Anywhere in Lagos')}
        - Budget: {context.get('budget', 'Not specified')}
        - Mood: {context.get('mood', 'Not specified')}
        """
    
    # Step 4: Ask Claude to reason and recommend
    prompt = f"""
    You are a smart restaurant recommendation agent for Lagos, Nigeria.
    
    USER PERSONA:
    {persona}
    
    {context_text}
    
    AVAILABLE OPTIONS:
    {catalogue_text}
    
    TASK:
    Based on this user's taste, behaviour pattern, and current context,
    recommend the TOP 3 options from the catalogue above.
    
    For each recommendation:
    - Explain WHY it fits this specific user (reference their persona)
    - Give a confidence score (1-10)
    - Write a one-line pitch in Nigerian English that would appeal to them
    
    Respond in this EXACT format for each recommendation:
    
    RANK 1:
    ID: [id]
    NAME: [name]
    CONFIDENCE: [score]/10
    WHY: [explanation referencing user persona]
    PITCH: [one line in Nigerian English]
    
    RANK 2:
    ID: [id]
    NAME: [name]
    CONFIDENCE: [score]/10
    WHY: [explanation]
    PITCH: [one line]
    
    RANK 3:
    ID: [id]
    NAME: [name]
    CONFIDENCE: [score]/10
    WHY: [explanation]
    PITCH: [one line]
    """
    
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=800,
        messages=[{"role": "user", "content": prompt}]
    )
    
    raw = response.content[0].text
    
    # Parse recommendations
    recommendations = []
    blocks = raw.strip().split("RANK ")
    
    for block in blocks[1:]:  # Skip empty first split
        lines = block.strip().split('\n')
        rec = {}
        for line in lines:
            line = line.strip()
            if line.startswith("ID:"):
                rec["id"] = line.replace("ID:", "").strip()
            elif line.startswith("NAME:"):
                rec["name"] = line.replace("NAME:", "").strip()
            elif line.startswith("CONFIDENCE:"):
                rec["confidence"] = line.replace("CONFIDENCE:", "").strip()
            elif line.startswith("WHY:"):
                rec["why"] = line.replace("WHY:", "").strip()
            elif line.startswith("PITCH:"):
                rec["pitch"] = line.replace("PITCH:", "").strip()
        if rec:
            recommendations.append(rec)
    
    return {
        "user_persona": persona,
        "context": context or {},
        "recommendations": recommendations
    }


# ---- TEST IT ----
if __name__ == "__main__":
    
    sample_history = [
        {
            "business": "Chicken Republic Lekki",
            "rating": 2,
            "review": "The chicken was dry and the service was so slow. Never again."
        },
        {
            "business": "Nkoyo Restaurant",
            "rating": 5,
            "review": "This place ehn! The ofe akwu was exactly like my mama used to make."
        },
        {
            "business": "Dominos VI",
            "rating": 3,
            "review": "Pizza was okay. Nothing special. They forgot my extra cheese."
        }
    ]
    
    context = {
        "occasion": "Date night",
        "location": "Lagos Island",
        "budget": "₦10,000 - ₦20,000",
        "mood": "Want something special and authentic"
    }
    
    print("🤖 Running Recommendation Agent...\n")
    result = recommend(sample_history, context)
    
    print("=== TOP RECOMMENDATIONS ===\n")
    for rec in result["recommendations"]:
        print(f"#{rec.get('id')} {rec.get('name')}")
        print(f"Confidence: {rec.get('confidence')}")
        print(f"Why: {rec.get('why')}")
        print(f"Pitch: {rec.get('pitch')}")
        print()