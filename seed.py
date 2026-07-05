import random
import datetime
import bcrypt
from database import users_col, products_col, orders_col, payments_col
from app import PRODUCT_IMAGE_MAP, FALLBACK_IMAGE, get_product_image

# Constants for password hashing
SEED_PASSWORD = bcrypt.hashpw(b'password123', bcrypt.gensalt()).decode('utf-8')
ADMIN_PASSWORD = bcrypt.hashpw(b'admin123', bcrypt.gensalt()).decode('utf-8')

# ── Canonical product lists ───────────────────────────────────────────────────

VEGETABLE_ITEMS = [
    'Tomato', 'Potato', 'Onion', 'Carrot', 'Brinjal', 'Cabbage', 'Cauliflower',
    'Capsicum', 'Green Chilli', 'Lady Finger', 'Beetroot', 'Spinach',
    'Cucumber', 'Pumpkin', 'Bottle Gourd', 'Bitter Gourd', 'Drumstick',
    'Radish', 'French Beans', 'Green Peas', 'Ridge Gourd', 'Snake Gourd',
    'Ash Gourd', 'Sweet Potato', 'Coriander Leaves',
]

FRUIT_ITEMS = [
    'Apple', 'Banana', 'Mango', 'Orange', 'Grapes', 'Guava', 'Papaya',
    'Pomegranate', 'Watermelon', 'Pineapple', 'Sapota', 'Lemon',
    'Sweet Lime', 'Coconut', 'Strawberry', 'Muskmelon', 'Dragon Fruit',
    'Kiwi', 'Pear', 'Peach', 'Plum', 'Litchi', 'Custard Apple',
    'Jackfruit', 'Amla',
]

GRAINS_ITEMS = [
    'Rice', 'Wheat',
]

SPICE_ITEMS = [
    'Turmeric', 'Coriander', 'Cumin', 'Red Chilli Powder', 'Black Pepper',
    'Cardamom', 'Cloves', 'Cinnamon', 'Fenugreek', 'Mustard Seeds',
]

ORGANIC_ITEMS = [
    'Organic Tomato', 'Organic Potato', 'Organic Spinach', 'Organic Carrot',
    'Organic Mango', 'Organic Wheat', 'Organic Rice', 'Organic Turmeric',
]

SEED_ITEMS = [
    'Tomato Seeds', 'Cucumber Seeds', 'Sunflower Seeds', 'Pumpkin Seeds',
    'Sesame Seeds', 'Flax Seeds', 'Chia Seeds', 'Fennel Seeds',
]

FARMER_FIRST_NAMES = ['Ramesh', 'Suresh', 'Amit', 'Rajesh', 'Anil', 'Vijay', 'Sunil', 'Harish', 'Mahendra', 'Devendra']
FARMER_LAST_NAMES = ['Kumar', 'Singh', 'Sharma', 'Patel', 'Yadav', 'Choudhary', 'Reddy', 'Gowda', 'Verma', 'Joshi']
FARM_NAMES = ['Green Meadows', 'Golden Harvest', 'Sunrich Farms', 'Happy Cattle', 'Pure Yield', 'Fresh Fields', "Nature's Bounty", 'Harvest Gold']

CONSUMER_FIRST_NAMES = ['Pooja', 'Neha', 'Rohan', 'Vikram', 'Anjali', 'Karan', 'Sneha', 'Deepak', 'Preeti', 'Sanjay']
CONSUMER_LAST_NAMES = ['Gupta', 'Mehta', 'Sen', 'Nair', 'Rao', 'Bose', 'Das', 'Roy', 'Mishra', 'Pandey']

REVIEW_COMMENTS = [
    'Super fresh, family loved it! Delivered straight from the farm.',
    'Very tasty, way better than supermarket produce.',
    'Top quality, delivery was quick and packaging was clean.',
    'Great value for money. Direct farm pricing makes a real difference.',
    'Excellent freshness, will definitely order again.',
    'Good quality produce, arrived well-packed.',
    'Genuinely fresh. You can tell it came directly from the farmer.',
]

def seed_db():
    print("Seed process: Clearing old collections...")
    users_col.delete_many({})
    products_col.delete_many({})
    orders_col.delete_many({})
    payments_col.delete_many({})

    # 1. Insert default Admin User
    admin_user = {
        "name": "System Administrator",
        "email": "admin@farmconnect.com",
        "password": ADMIN_PASSWORD,
        "role": "admin",
        "phone": "9999999999",
        "address": "Central Agricultural Hub, Bangalore, India",
        "location": {
            "type": "Point",
            "coordinates": [77.6200, 12.9100]
        },
        "isApproved": True,
        "wishlist": [],
        "notifications": []
    }
    users_col.insert_one(admin_user)
    print("Admin user seeded.")

    # 2. Seed 100 Farmers
    farmers = []
    for i in range(1, 101):
        name = f"{random.choice(FARMER_FIRST_NAMES)} {random.choice(FARMER_LAST_NAMES)}"
        farm_name = f"{random.choice(FARM_NAMES)} Farm"
        email = f"farmer{i}@farmconnect.com"
        phone = f"98765{str(10000 + i)[1:]}"
        lat = 12.9716 + (random.random() - 0.5) * 2
        lng = 77.5946 + (random.random() - 0.5) * 2

        farmers.append({
            "name": name,
            "email": email,
            "password": SEED_PASSWORD,
            "role": "farmer",
            "phone": phone,
            "address": f"Village Road No. {random.randint(1, 40)}, District Farm State",
            "farmName": farm_name,
            "farmDescription": f"We grow and sell premium quality fresh crops directly to consumers at {farm_name}.",
            "location": {
                "type": "Point",
                "coordinates": [lng, lat]
            },
            "isApproved": True,
            "wishlist": [],
            "notifications": []
        })
    inserted_farmers = users_col.insert_many(farmers)
    farmer_ids = inserted_farmers.inserted_ids
    print(f"Seeded 100 Farmers.")

    # 3. Seed 1000 Consumers
    consumers = []
    for i in range(1, 1001):
        name = f"{random.choice(CONSUMER_FIRST_NAMES)} {random.choice(CONSUMER_LAST_NAMES)}"
        email = f"consumer{i}@gmail.com"
        phone = f"87654{str(10000 + i)[1:]}"
        lat = 12.9716 + (random.random() - 0.5) * 0.4
        lng = 77.5946 + (random.random() - 0.5) * 0.4

        consumers.append({
            "name": name,
            "email": email,
            "password": SEED_PASSWORD,
            "role": "consumer",
            "phone": phone,
            "address": f"Apt {random.randint(101, 999)}, Green Villa, Tech Park Road, Bengaluru",
            "location": {
                "type": "Point",
                "coordinates": [lng, lat]
            },
            "wishlist": [],
            "notifications": []
        })
    inserted_consumers = users_col.insert_many(consumers)
    consumer_ids = inserted_consumers.inserted_ids
    print(f"Seeded 1000 Consumers.")

    # 4. Seed 500 Products
    products = []
    now = datetime.datetime.now()
    for i in range(1, 501):
        # Category rotation
        if i <= 150:
            category = "Vegetables"
            name = random.choice(VEGETABLE_ITEMS)
            unit = "kg"
        elif i <= 300:
            category = "Fruits"
            name = random.choice(FRUIT_ITEMS)
            unit = "kg"
        elif i <= 380:
            category = "Grains & Pulses"
            name = random.choice(GRAINS_ITEMS)
            unit = "kg"
        elif i <= 430:
            category = "Spices"
            name = random.choice(SPICE_ITEMS)
            unit = "100g"
        elif i <= 460:
            category = "Organic"
            name = random.choice(ORGANIC_ITEMS)
            unit = "kg"
        else:
            category = "Seeds"
            name = random.choice(SEED_ITEMS)
            unit = "50g"

        farmer_id = random.choice(farmer_ids)
        farmer_obj = users_col.find_one({"_id": farmer_id})
        farmer_price = random.randint(5, 60)
        market_price = int(farmer_price * random.uniform(1.25, 1.60))
        savings = market_price - farmer_price
        discount_percentage = int((savings / market_price) * 100)

        # Historical prices list
        historical_prices = []
        for w in range(4, -1, -1):
            trend_date = now - datetime.timedelta(days=w * 7)
            variation = (random.random() - 0.5) * 10
            historical_prices.append({
                "date": trend_date,
                "price": max(10, int(farmer_price + variation)),
                "marketPrice": max(15, int(market_price + variation * 1.5))
            })

        # Mapped Product Name with variant
        suffix = random.choice(['Organic', 'Freshly Picked', 'Standard'])
        full_name = f"{name} ({suffix})"
        img = get_product_image(full_name)

        # Reviews list
        reviews = []
        review_count = random.randint(2, 8)
        review_sum = 0
        for _ in range(review_count):
            cons_id = random.choice(consumer_ids)
            cons_obj = users_col.find_one({"_id": cons_id})
            rating_val = random.randint(4, 5)
            review_sum += rating_val
            reviews.append({
                "user": cons_id,
                "name": cons_obj["name"],
                "rating": rating_val,
                "comment": random.choice(REVIEW_COMMENTS),
                "createdAt": now - datetime.timedelta(days=random.randint(1, 30))
            })
        rating_avg = round(review_sum / review_count, 1)

        products.append({
            "farmer": farmer_id,
            "name": full_name,
            "description": f"Premium quality {category.lower()} directly harvested from {farmer_obj['farmName']}. Cleaned, sorted, and packed under absolute hygiene standards.",
            "price": farmer_price,
            "marketPrice": market_price,
            "discountPercentage": discount_percentage,
            "unit": unit,
            "category": category,
            "image": img,
            "stock": random.randint(50, 400),
            "organicStatus": random.choice(['Organic', 'Organic', 'Inorganic']),
            "rating": rating_avg,
            "numReviews": review_count,
            "reviews": reviews,
            "availability": True,
            "historicalPrices": historical_prices
        })

    products_col.insert_many(products)
    print("Seeded 500 agricultural products successfully.")

if __name__ == '__main__':
    seed_db()
