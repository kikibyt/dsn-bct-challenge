import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from task_a.agent import simulate_review
from task_b.agent import recommend

print("=" * 55)
print("ÌMỌ̀ — Cold-Start & Cross-Domain Demonstration")
print("=" * 55)

# ── SCENARIO 1: True Cold Start (1 review only) ──
print("\n📌 SCENARIO 1: True Cold-Start User (1 review)")
print("-" * 55)

cold_start_history = [
    {
        "business": "Mama Cass Restaurant",
        "rating": 5,
        "review": "Best amala in Lagos. Authentic and filling."
    }
]

context_cold = {
    "occasion": "Quick lunch",
    "location": "Lagos Mainland",
    "budget": "₦1,500 - ₦4,000",
    "mood": "Want something local and filling"
}

print("User history: 1 review only")
print("Testing Task B recommendation with minimal data...\n")

result_cold = recommend(cold_start_history, context_cold)
print(f"Persona extracted: {result_cold['user_persona'][:200]}...")
print(f"\nRecommendations despite cold-start:")
for rec in result_cold["recommendations"][:3]:
    print(f"  → {rec.get('name')} (Confidence: {rec.get('confidence')})")
    print(f"     {rec.get('pitch')}")

# ── SCENARIO 2: Cross-Domain (food history → different category) ──
print("\n\n📌 SCENARIO 2: Cross-Domain Recommendation")
print("-" * 55)
print("User has restaurant history → recommend cafe/brunch\n")

food_history = [
    {
        "business": "Nkoyo Restaurant",
        "rating": 5,
        "review": "The banga soup was rich and authentic. Love this place."
    },
    {
        "business": "Buka Hut Mainland",
        "rating": 4,
        "review": "Good amala, fair price. Does the job well."
    },
    {
        "business": "KFC Ikeja",
        "rating": 1,
        "review": "Overpriced and tasteless. Never again."
    }
]

context_cross = {
    "occasion": "Morning meeting with a colleague",
    "location": "Ikoyi",
    "budget": "₦3,000 - ₦8,000",
    "mood": "Need coffee and light food"
}

print("User context: Nigerian food lover → morning cafe setting")
result_cross = recommend(food_history, context_cross)
print(f"\nCross-domain recommendations:")
for rec in result_cross["recommendations"][:3]:
    print(f"  → {rec.get('name')} (Confidence: {rec.get('confidence')})")
    print(f"     {rec.get('pitch')}")

# ── SCENARIO 3: Cold-Start Task A (simulate review with 2 reviews) ──
print("\n\n📌 SCENARIO 3: Cold-Start Review Simulation (2 reviews)")
print("-" * 55)

minimal_history = [
    {
        "business": "Tantalizers Yaba",
        "rating": 3,
        "review": "Okay food. Nothing special but fills you up."
    },
    {
        "business": "Suya Spot Surulere",
        "rating": 5,
        "review": "The suya here is on another level. Spicy and fresh!"
    }
]

new_product = {
    "name": "Hilda's Kitchen Lekki",
    "category": "Fine Dining Nigerian",
    "description": "Premium Nigerian cuisine. Known for lobster jollof and wagyu suya."
}

print("User history: 2 reviews only")
print("Testing Task A simulation with minimal data...\n")

result_sim = simulate_review(minimal_history, new_product)
print(f"Simulated Rating: {'⭐' * result_sim['simulated_rating']} ({result_sim['simulated_rating']}/5)")
print(f"Simulated Review: {result_sim['simulated_review'][:300]}...")

# ── SCENARIO 4: Multi-turn Conversational Context ──
print("\n\n📌 SCENARIO 4: Multi-Turn Context Shift")
print("-" * 55)
print("Same user, different context → different recommendations\n")

base_history = [
    {
        "business": "Terra Kulture VI",
        "rating": 5,
        "review": "Beautiful place! Great food and amazing ambiance."
    },
    {
        "business": "Craft Grill VI",
        "rating": 4,
        "review": "Premium experience. Worth the price for special occasions."
    },
    {
        "business": "Buka Hut Mainland",
        "rating": 2,
        "review": "Too noisy and crowded for my taste."
    }
]

context_turn1 = {
    "occasion": "Romantic anniversary dinner",
    "location": "Victoria Island",
    "budget": "₦20,000+",
    "mood": "Special and intimate"
}

context_turn2 = {
    "occasion": "Quick solo lunch",
    "location": "Anywhere",
    "budget": "₦2,000 - ₦5,000",
    "mood": "Just need to eat fast"
}

result_t1 = recommend(base_history, context_turn1)
result_t2 = recommend(base_history, context_turn2)

print("Turn 1 — Anniversary dinner:")
for rec in result_t1["recommendations"][:2]:
    print(f"  → {rec.get('name')} | {rec.get('pitch')}")

print("\nTurn 2 — Quick solo lunch (same user, different context):")
for rec in result_t2["recommendations"][:2]:
    print(f"  → {rec.get('name')} | {rec.get('pitch')}")

print("\n✅ Cold-start & cross-domain demonstration complete!")
print("ÌMỌ̀ handles sparse history, domain shifts, and context changes gracefully.")