import os
import json
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


def load_catalogue():
    """Load from dataset if available, else use defaults."""
    data_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data", "businesses.json"
    )
    if os.path.exists(data_path):
        businesses = json.load(open(data_path))
        return [
            {
                "id": b["business_id"],
                "name": b["name"],
                "category": b["category"],
                "description": f"{b['category']} in Lagos. Rated {b['stars']} stars average. Price: {b['price']}.",
                "price_range": b["price"],
                "location": b["city"]
            }
            for b in businesses
        ]
    # Fallback hardcoded list
    return [
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


PRODUCT_CATALOGUE = load_catalogue()


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
    recommend the TOP 5 options from the catalogue above.

    IMPORTANT RULES:
    - ONLY recommend businesses from the catalogue above — use exact names and IDs
    - Rank by fit to this specific user's persona, not by general popularity
    - If user loves authentic Nigerian food, rank those higher
    - If user hates slow service or overpricing, penalise those options
    - Reference the user's actual behaviour in your WHY explanation

    For each recommendation respond in this EXACT format:

    RANK 1:
    ID: [exact id from catalogue]
    NAME: [exact name from catalogue]
    CONFIDENCE: [score]/10
    WHY: [explanation referencing user persona]
    PITCH: [one line in Nigerian English]

    RANK 2:
    ID: [exact id from catalogue]
    NAME: [exact name from catalogue]
    CONFIDENCE: [score]/10
    WHY: [explanation]
    PITCH: [one line]

    RANK 3:
    ID: [exact id from catalogue]
    NAME: [exact name from catalogue]
    CONFIDENCE: [score]/10
    WHY: [explanation]
    PITCH: [one line]

    RANK 4:
    ID: [exact id from catalogue]
    NAME: [exact name from catalogue]
    CONFIDENCE: [score]/10
    WHY: [explanation]
    PITCH: [one line]

    RANK 5:
    ID: [exact id from catalogue]
    NAME: [exact name from catalogue]
    CONFIDENCE: [score]/10
    WHY: [explanation]
    PITCH: [one line]
    """

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.content[0].text

    # Parse recommendations
    recommendations = []
    blocks = raw.strip().split("RANK ")

    for block in blocks[1:]:
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