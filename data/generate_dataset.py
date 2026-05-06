import json
import random
import os

# ── Nigerian-flavoured synthetic Yelp-style dataset ──

BUSINESSES = [
    {"business_id": "b001", "name": "Mama Cass Restaurant", "category": "Nigerian/Buka", "city": "Lagos", "stars": 4.2, "price": "₦1,500-₦4,000"},
    {"business_id": "b002", "name": "Chicken Republic Lekki", "category": "Fast Food", "city": "Lagos", "stars": 3.1, "price": "₦1,500-₦4,000"},
    {"business_id": "b003", "name": "Terra Kulture VI", "category": "Cultural Dining", "city": "Lagos", "stars": 4.5, "price": "₦5,000-₦15,000"},
    {"business_id": "b004", "name": "Nkoyo Restaurant", "category": "Niger Delta Cuisine", "city": "Lagos", "stars": 4.7, "price": "₦3,000-₦8,000"},
    {"business_id": "b005", "name": "Yellow Chilli Ikeja", "category": "Contemporary Nigerian", "city": "Lagos", "stars": 4.3, "price": "₦8,000-₦20,000"},
    {"business_id": "b006", "name": "Buka Hut Mainland", "category": "Street Food/Buka", "city": "Lagos", "stars": 4.0, "price": "₦800-₦2,500"},
    {"business_id": "b007", "name": "Craft Grill VI", "category": "Continental", "city": "Lagos", "stars": 4.1, "price": "₦15,000-₦40,000"},
    {"business_id": "b008", "name": "Cafe Neo Ikoyi", "category": "Cafe/Brunch", "city": "Lagos", "stars": 4.4, "price": "₦3,000-₦10,000"},
    {"business_id": "b009", "name": "KFC Ikeja City Mall", "category": "Fast Food", "city": "Lagos", "stars": 3.0, "price": "₦2,000-₦5,000"},
    {"business_id": "b010", "name": "Okrika Mama Kitchen", "category": "Homestyle Nigerian", "city": "Lagos", "stars": 4.6, "price": "₦2,000-₦5,000"},
    {"business_id": "b011", "name": "The Place Restaurant", "category": "Nigerian Casual", "city": "Lagos", "stars": 3.8, "price": "₦2,500-₦6,000"},
    {"business_id": "b012", "name": "Suya Spot Surulere", "category": "Street Food", "city": "Lagos", "stars": 4.5, "price": "₦500-₦2,000"},
    {"business_id": "b013", "name": "Dominos Pizza VI", "category": "Fast Food/Pizza", "city": "Lagos", "stars": 3.2, "price": "₦3,000-₦8,000"},
    {"business_id": "b014", "name": "Tantalizers Yaba", "category": "Fast Food Nigerian", "city": "Lagos", "stars": 3.5, "price": "₦1,000-₦3,500"},
    {"business_id": "b015", "name": "Hilda's Kitchen Lekki", "category": "Fine Dining Nigerian", "city": "Lagos", "stars": 4.8, "price": "₦10,000-₦25,000"},
]

# Review templates per persona type
REVIEW_TEMPLATES = {
    "purist": {
        5: [
            "This place ehn! {food} was exactly like mama used to make. Authentic to the bone.",
            "Finally found somewhere that knows how to cook proper {food}. No shortcuts, no nonsense. 5 stars.",
            "The {food} here is the real deal. Rich, fresh, and plenty. This is what Nigerian food should taste like.",
        ],
        4: [
            "Very good {food}. Tastes genuine and portions are decent. Small complaint about service but food carried it.",
            "The {food} was solid. Not my mama's recipe but close enough. Will come back.",
            "Good authentic taste on the {food}. Service could be faster but I understand — quality takes time.",
        ],
        3: [
            "Average {food}. Nothing special. Has potential but needs consistency.",
            "The {food} was okay. Some days good, some days not. Hard to rely on.",
        ],
        2: [
            "Overpriced for the quality. The {food} tasted like it was reheated. Disappointing.",
            "Expected authentic but got watered-down {food}. This is not it.",
        ],
        1: [
            "Never again. The {food} was an insult to Nigerian cuisine. Dry, tasteless, and expensive.",
            "Terrible. The {food} had no soul. How do you mess up {food} this badly?",
        ]
    },
    "value_hunter": {
        5: [
            "Plenty {food} for the price! Got change back and still full. This is value.",
            "Best price-to-portion ratio in Lagos. {food} was good and my wallet survived. 5 stars.",
        ],
        4: [
            "Good value. {food} was tasty and affordable. Slight wait but worth it for the price.",
            "Decent {food} at a fair price. Not fancy but fills you up properly.",
        ],
        3: [
            "{food} was average and price was average. Nothing to write home about.",
            "Okay value. Could be better portions for what they charge.",
        ],
        2: [
            "Too expensive for small {food}. I've had better for less elsewhere.",
            "Charged me Lagos Island prices for Mainland food quality. Not acceptable.",
        ],
        1: [
            "Robbery. Tiny {food} at ridiculous price. Never returning.",
        ]
    },
    "social_diner": {
        5: [
            "The vibe here is everything! Great ambiance, lovely service, and {food} was delicious. Perfect for dates.",
            "Came for a work dinner — beautiful setting, attentive staff, {food} impressed everyone. Will book again.",
        ],
        4: [
            "Nice atmosphere and good {food}. Service was warm and professional. Great spot for catch-ups.",
            "Lovely place! {food} was good and the staff made us feel welcome. Minor wait time though.",
        ],
        3: [
            "Decent ambiance but {food} was just okay. Service was distracted. Has potential.",
            "Nice decor but {food} didn't match the setting. Mediocre for the presentation.",
        ],
        2: [
            "Beautiful interior wasted on cold {food} and rude service. Very disappointing.",
            "Came for a special occasion — service ruined it. {food} was average at best.",
        ],
        1: [
            "Embarrassing experience. Waited 1 hour for {food} that arrived cold. Staff was dismissive.",
        ]
    }
}

FOODS = {
    "Nigerian/Buka": ["amala and ewedu", "jollof rice", "egusi soup", "pepper soup", "eba and okra"],
    "Fast Food": ["fried chicken", "burger", "chips", "chicken wrap", "spicy wings"],
    "Cultural Dining": ["afang soup", "banga soup", "ofe akwu", "native soup", "assorted pepper soup"],
    "Niger Delta Cuisine": ["banga soup and starch", "ofe akwu", "fresh catfish pepper soup", "native soup"],
    "Contemporary Nigerian": ["deconstructed egusi", "jollof risotto", "suya steak", "ogbono fusion"],
    "Street Food/Buka": ["amala", "ewedu and gbegiri", "oxtail pepper soup", "roasted corn"],
    "Continental": ["ribeye steak", "grilled salmon", "pasta", "club sandwich"],
    "Cafe/Brunch": ["avocado toast", "smoothie bowl", "pancakes", "specialty coffee"],
    "Homestyle Nigerian": ["fresh fish stew", "ofe onugbu", "pepper soup", "native rice"],
    "Nigerian Casual": ["jollof rice", "grilled chicken", "ofada rice", "moin moin"],
    "Street Food": ["suya", "grilled fish", "roasted plantain", "kilishi"],
    "Fast Food/Pizza": ["pepperoni pizza", "chicken pizza", "garlic bread", "pasta"],
    "Fast Food Nigerian": ["meat pie", "jollof rice", "fried chicken", "puff puff"],
    "Fine Dining Nigerian": ["tasting menu", "premium pepper soup", "lobster jollof", "wagyu suya"],
}

PERSONA_TYPES = ["purist", "value_hunter", "social_diner"]


def generate_user(user_id: int) -> dict:
    persona = random.choice(PERSONA_TYPES)
    
    # How many businesses this user has reviewed
    num_reviews = random.randint(5, 15)
    reviewed_businesses = random.sample(BUSINESSES, min(num_reviews, len(BUSINESSES)))
    
    reviews = []
    for biz in reviewed_businesses:
        category = biz["category"]
        food_options = FOODS.get(category, ["food"])
        food = random.choice(food_options)
        
        # Generate rating based on persona + business quality
        base_stars = round(biz["stars"])
        
        if persona == "purist":
            # Purists are polarised — push toward extremes
            if base_stars >= 4:
                star = random.choices([5, 4, 3], weights=[60, 30, 10])[0]
            else:
                star = random.choices([1, 2, 3], weights=[40, 40, 20])[0]
        elif persona == "value_hunter":
            # Value hunters care about price — cheap places score higher
            price_score = 1 if "₦" in biz["price"] and int(biz["price"].split("₦")[1].split("-")[0].replace(",", "")) < 3000 else 0
            if price_score:
                star = random.choices([5, 4, 3], weights=[50, 35, 15])[0]
            else:
                star = random.choices([2, 3, 4], weights=[30, 40, 30])[0]
        else:  # social_diner
            # Social diners are generous but care about vibe
            star = random.choices([5, 4, 3, 2], weights=[35, 40, 15, 10])[0]
        
        # Get review template
        templates = REVIEW_TEMPLATES[persona].get(star, REVIEW_TEMPLATES[persona][3])
        template = random.choice(templates)
        review_text = template.format(food=food)
        
        reviews.append({
            "review_id": f"r{user_id:04d}_{biz['business_id']}",
            "user_id": f"u{user_id:04d}",
            "business_id": biz["business_id"],
            "business_name": biz["name"],
            "category": category,
            "stars": star,
            "text": review_text,
            "persona_type": persona  # ground truth for evaluation
        })
    
    return {
        "user_id": f"u{user_id:04d}",
        "persona_type": persona,
        "reviews": reviews
    }


def generate_dataset(num_users: int = 200):
    print(f"Generating dataset with {num_users} users...")
    
    users = []
    all_reviews = []
    
    for i in range(1, num_users + 1):
        user = generate_user(i)
        users.append({
            "user_id": user["user_id"],
            "persona_type": user["persona_type"],
            "review_count": len(user["reviews"])
        })
        all_reviews.extend(user["reviews"])
    
    # Save files
    os.makedirs("data", exist_ok=True)
    
    with open("data/users.json", "w") as f:
        json.dump(users, f, indent=2)
    
    with open("data/reviews.json", "w") as f:
        json.dump(all_reviews, f, indent=2)
    
    with open("data/businesses.json", "w") as f:
        json.dump(BUSINESSES, f, indent=2)
    
    print(f"✅ Generated {len(users)} users")
    print(f"✅ Generated {len(all_reviews)} reviews")
    print(f"✅ Generated {len(BUSINESSES)} businesses")
    print(f"✅ Files saved to data/")
    print(f"\nPersona breakdown:")
    
    for p in PERSONA_TYPES:
        count = sum(1 for u in users if u["persona_type"] == p)
        print(f"  {p}: {count} users")


if __name__ == "__main__":
    generate_dataset(200)