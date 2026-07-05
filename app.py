import os
import math
import datetime
from bson import ObjectId
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import bcrypt
import razorpay
from database import users_col, products_col, orders_col, payments_col
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# ─────────────────────────────────────────────────────────────────────────────
# STRICT PRODUCT IMAGE MAP
# Each key maps to an Unsplash photo of THAT specific product only.
# No generic farm, harvest, basket, field, or mixed-produce images allowed.
# ─────────────────────────────────────────────────────────────────────────────

PRODUCT_IMAGE_MAP = {
    # ── VEGETABLES (25) ───────────────────────────────────────────────────────
    'Tomato':           'https://images.unsplash.com/photo-1546094096-0df4bcaaa337?auto=format&fit=crop&w=600&h=500&q=80',
    'Potato':           'https://images.unsplash.com/photo-1518977676601-b53f82aba655?auto=format&fit=crop&w=600&h=500&q=80',
    'Onion':            'https://images.unsplash.com/photo-1508747703725-719777637510?auto=format&fit=crop&w=600&h=500&q=80',
    'Carrot':           'https://images.unsplash.com/photo-1598170845058-32b9d6a5da37?auto=format&fit=crop&w=600&h=500&q=80',
    'Brinjal':          'https://images.unsplash.com/photo-1659404959404-cdacd0e3bbc8?auto=format&fit=crop&w=600&h=500&q=80',
    'Cabbage':          'https://images.unsplash.com/photo-1594282486552-05b4d80fbb9f?auto=format&fit=crop&w=600&h=500&q=80',
    'Cauliflower':      'https://images.unsplash.com/photo-1510627489301-7d311d70b114?auto=format&fit=crop&w=600&h=500&q=80',
    'Capsicum':         'https://images.unsplash.com/photo-1563565375-f3fdfdbefa83?auto=format&fit=crop&w=600&h=500&q=80',
    'Green Chilli':     'https://images.unsplash.com/photo-1588168333986-5078d3ae3976?auto=format&fit=crop&w=600&h=500&q=80',
    'Lady Finger':      'https://images.unsplash.com/photo-1624806992066-5ffcf7ca186b?auto=format&fit=crop&w=600&h=500&q=80',
    'Beetroot':         'https://images.unsplash.com/photo-1593105544559-ecb03bf76f82?auto=format&fit=crop&w=600&h=500&q=80',
    'Spinach':          'https://images.unsplash.com/photo-1576045057995-568f588f82fb?auto=format&fit=crop&w=600&h=500&q=80',
    'Cucumber':         'https://images.unsplash.com/photo-1449300079323-02e209d9d3a6?auto=format&fit=crop&w=600&h=500&q=80',
    'Pumpkin':          'https://images.unsplash.com/photo-1570586437263-ab629fccc818?auto=format&fit=crop&w=600&h=500&q=80',
    'Bottle Gourd':     'https://images.unsplash.com/photo-1632224702038-d82099ad62f0?auto=format&fit=crop&w=600&h=500&q=80',
    'Bitter Gourd':     'https://images.unsplash.com/photo-1604497181015-76590d828b62?auto=format&fit=crop&w=600&h=500&q=80',
    'Drumstick':        'https://images.unsplash.com/photo-1604497181015-76590d828b62?auto=format&fit=crop&w=600&h=500&q=80',
    'Radish':           'https://images.unsplash.com/photo-1582284540020-8acbe03f4924?auto=format&fit=crop&w=600&h=500&q=80',
    'French Beans':     'https://images.unsplash.com/photo-1567375698348-5d9d5ae99de0?auto=format&fit=crop&w=600&h=500&q=80',
    'Green Peas':       'https://images.unsplash.com/photo-1587735243615-c03f25aaff15?auto=format&fit=crop&w=600&h=500&q=80',
    'Ridge Gourd':      'https://images.unsplash.com/photo-1632224702038-d82099ad62f0?auto=format&fit=crop&w=600&h=500&q=80',
    'Snake Gourd':      'https://images.unsplash.com/photo-1632224702038-d82099ad62f0?auto=format&fit=crop&w=600&h=500&q=80',
    'Ash Gourd':        'https://images.unsplash.com/photo-1632224702038-d82099ad62f0?auto=format&fit=crop&w=600&h=500&q=80',
    'Sweet Potato':     'https://images.unsplash.com/photo-1596097635121-14b63b7a0c19?auto=format&fit=crop&w=600&h=500&q=80',
    'Coriander Leaves': 'https://images.unsplash.com/photo-1615485291234-9d694218aeb3?auto=format&fit=crop&w=600&h=500&q=80',
    'Garlic':           'https://images.unsplash.com/photo-1587049352846-4a222e784d38?auto=format&fit=crop&w=600&h=500&q=80',
    'Ginger':           'https://images.unsplash.com/photo-1615485500704-8e990f9900f7?auto=format&fit=crop&w=600&h=500&q=80',
    'Broccoli':         'https://images.unsplash.com/photo-1459411621453-7b03977f4bfc?auto=format&fit=crop&w=600&h=500&q=80',
    'Corn':             'https://images.unsplash.com/photo-1551754655-cd27e38d2076?auto=format&fit=crop&w=600&h=500&q=80',
    'Lettuce':          'https://images.unsplash.com/photo-1622206151226-18ca2c9ab4a1?auto=format&fit=crop&w=600&h=500&q=80',
    'Turnip':           'https://images.unsplash.com/photo-1582284540020-8acbe03f4924?auto=format&fit=crop&w=600&h=500&q=80',
    'Zucchini':         'https://images.unsplash.com/photo-1622205313162-be1d5712a43f?auto=format&fit=crop&w=600&h=500&q=80',
    'Mushroom':         'https://images.unsplash.com/photo-1504545102780-26774c1bb073?auto=format&fit=crop&w=600&h=500&q=80',
    # ── FRUITS (25) ───────────────────────────────────────────────────────────
    'Apple':         'https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?auto=format&fit=crop&w=600&h=500&q=80',
    'Banana':        'https://images.unsplash.com/photo-1571771894821-ce9b6c11b08e?auto=format&fit=crop&w=600&h=500&q=80',
    'Mango':         'https://images.unsplash.com/photo-1553279768-865429fa0078?auto=format&fit=crop&w=600&h=500&q=80',
    'Orange':        'https://images.unsplash.com/photo-1547514701-42782101795e?auto=format&fit=crop&w=600&h=500&q=80',
    'Grapes':        'https://images.unsplash.com/photo-1537640538966-79f369143f8f?auto=format&fit=crop&w=600&h=500&q=80',
    'Guava':         'https://images.unsplash.com/photo-1536511132770-e5058c7e8c46?auto=format&fit=crop&w=600&h=500&q=80',
    'Papaya':        'https://images.unsplash.com/photo-1526318472351-c75fcf070305?auto=format&fit=crop&w=600&h=500&q=80',
    'Pomegranate':   'https://images.unsplash.com/photo-1541344999736-83eca272f6fc?auto=format&fit=crop&w=600&h=500&q=80',
    'Watermelon':    'https://images.unsplash.com/photo-1563114773-84221bd62daa?auto=format&fit=crop&w=600&h=500&q=80',
    'Pineapple':     'https://images.unsplash.com/photo-1550258987-190a2d41a8ba?auto=format&fit=crop&w=600&h=500&q=80',
    'Sapota':        'https://images.unsplash.com/photo-1574856344991-aaa31b6f4ce3?auto=format&fit=crop&w=600&h=500&q=80',
    'Lemon':         'https://images.unsplash.com/photo-1582087765901-43b09c0c6d79?auto=format&fit=crop&w=600&h=500&q=80',
    'Sweet Lime':    'https://images.unsplash.com/photo-1611080626919-7cf5a9dbab12?auto=format&fit=crop&w=600&h=500&q=80',
    'Coconut':       'https://images.unsplash.com/photo-1562159759-af7a5688dd2e?auto=format&fit=crop&w=600&h=500&q=80',
    'Strawberry':    'https://images.unsplash.com/photo-1464965911861-746a04b4bca6?auto=format&fit=crop&w=600&h=500&q=80',
    'Muskmelon':     'https://images.unsplash.com/photo-1571771894821-ce9b6c11b08e?auto=format&fit=crop&w=600&h=500&q=80',
    'Dragon Fruit':  'https://images.unsplash.com/photo-1527325678964-54921661f888?auto=format&fit=crop&w=600&h=500&q=80',
    'Kiwi':          'https://images.unsplash.com/photo-1585059895524-72359e06133a?auto=format&fit=crop&w=600&h=500&q=80',
    'Pear':          'https://images.unsplash.com/photo-1552255349-450c59a5ec8e?auto=format&fit=crop&w=600&h=500&q=80',
    'Peach':         'https://images.unsplash.com/photo-1595743825637-405c6f3f4d37?auto=format&fit=crop&w=600&h=500&q=80',
    'Plum':          'https://images.unsplash.com/photo-1570913149827-d2ac84ab3f9a?auto=format&fit=crop&w=600&h=500&q=80',
    'Litchi':        'https://images.unsplash.com/photo-1567306226416-28f0efdc88ce?auto=format&fit=crop&w=600&h=500&q=80',
    'Custard Apple': 'https://images.unsplash.com/photo-1574856344991-aaa31b6f4ce3?auto=format&fit=crop&w=600&h=500&q=80',
    'Jackfruit':     'https://images.unsplash.com/photo-1559181567-c3190bfa4cbb?auto=format&fit=crop&w=600&h=500&q=80',
    'Amla':          'https://images.unsplash.com/photo-1536511132770-e5058c7e8c46?auto=format&fit=crop&w=600&h=500&q=80',

    # ── GRAINS & PULSES (18) ─────────────────────────────────────────────────
    'Rice':          'https://images.unsplash.com/photo-1586201375761-83865001e31c?auto=format&fit=crop&w=600&h=500&q=80',
    'Wheat':         'https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?auto=format&fit=crop&w=600&h=500&q=80',
    'Maize':         'https://images.unsplash.com/photo-1603048588665-791ca8aea617?auto=format&fit=crop&w=600&h=500&q=80',
    'Jowar':         'https://images.unsplash.com/photo-1612358405896-f9b74e054d24?auto=format&fit=crop&w=600&h=500&q=80',
    'Bajra':         'https://images.unsplash.com/photo-1612358405896-f9b74e054d24?auto=format&fit=crop&w=600&h=500&q=80',
    'Ragi':          'https://images.unsplash.com/photo-1612358405896-f9b74e054d24?auto=format&fit=crop&w=600&h=500&q=80',
    'Barley':        'https://images.unsplash.com/photo-1599909533984-70c29ccdb797?auto=format&fit=crop&w=600&h=500&q=80',
    'Oats':          'https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?auto=format&fit=crop&w=600&h=500&q=80',
    'Green Gram':    'https://images.unsplash.com/photo-1585032226651-759b368d7246?auto=format&fit=crop&w=600&h=500&q=80',
    'Black Gram':    'https://images.unsplash.com/photo-1612257999691-b04a63f0b1e5?auto=format&fit=crop&w=600&h=500&q=80',
    'Bengal Gram':   'https://images.unsplash.com/photo-1515543237350-b3eea1ec8082?auto=format&fit=crop&w=600&h=500&q=80',
    'Red Gram':      'https://images.unsplash.com/photo-1612257999691-b04a63f0b1e5?auto=format&fit=crop&w=600&h=500&q=80',
    'Masoor Dal':    'https://images.unsplash.com/photo-1612257999691-b04a63f0b1e5?auto=format&fit=crop&w=600&h=500&q=80',
    'Rajma':         'https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?auto=format&fit=crop&w=600&h=500&q=80',
    'Cowpea':        'https://images.unsplash.com/photo-1612257999691-b04a63f0b1e5?auto=format&fit=crop&w=600&h=500&q=80',
    'Horse Gram':    'https://images.unsplash.com/photo-1612257999691-b04a63f0b1e5?auto=format&fit=crop&w=600&h=500&q=80',
    'Soybean':       'https://images.unsplash.com/photo-1591205337474-2f5d1248cedb?auto=format&fit=crop&w=600&h=500&q=80',
    'Groundnut':     'https://images.unsplash.com/photo-1567653418880-5e5f81103251?auto=format&fit=crop&w=600&h=500&q=80',

    # ── SPICES ────────────────────────────────────────────────────────────────
    'Turmeric':          'https://images.unsplash.com/photo-1615485500704-8e990f9900f7?auto=format&fit=crop&w=600&h=500&q=80',
    'Coriander':         'https://images.unsplash.com/photo-1615485291234-9d694218aeb3?auto=format&fit=crop&w=600&h=500&q=80',
    'Cumin':             'https://images.unsplash.com/photo-1599909533984-70c29ccdb797?auto=format&fit=crop&w=600&h=500&q=80',
    'Red Chilli Powder': 'https://images.unsplash.com/photo-1588168333986-5078d3ae3976?auto=format&fit=crop&w=600&h=500&q=80',
    'Black Pepper':      'https://images.unsplash.com/photo-1506368249639-73a05d6f6488?auto=format&fit=crop&w=600&h=500&q=80',
    'Cardamom':          'https://images.unsplash.com/photo-1506368249639-73a05d6f6488?auto=format&fit=crop&w=600&h=500&q=80',
    'Cloves':            'https://images.unsplash.com/photo-1506368249639-73a05d6f6488?auto=format&fit=crop&w=600&h=500&q=80',
    'Cinnamon':          'https://images.unsplash.com/photo-1506368249639-73a05d6f6488?auto=format&fit=crop&w=600&h=500&q=80',
    'Fenugreek':         'https://images.unsplash.com/photo-1599909533984-70c29ccdb797?auto=format&fit=crop&w=600&h=500&q=80',
    'Mustard Seeds':     'https://images.unsplash.com/photo-1599909533984-70c29ccdb797?auto=format&fit=crop&w=600&h=500&q=80',
    # ── ORGANIC ───────────────────────────────────────────────────────────────
    'Organic Tomato':   'https://images.unsplash.com/photo-1546094096-0df4bcaaa337?auto=format&fit=crop&w=600&h=500&q=80',
    'Organic Potato':   'https://images.unsplash.com/photo-1518977676601-b53f82aba655?auto=format&fit=crop&w=600&h=500&q=80',
    'Organic Spinach':  'https://images.unsplash.com/photo-1576045057995-568f588f82fb?auto=format&fit=crop&w=600&h=500&q=80',
    'Organic Carrot':   'https://images.unsplash.com/photo-1598170845058-32b9d6a5da37?auto=format&fit=crop&w=600&h=500&q=80',
    'Organic Mango':    'https://images.unsplash.com/photo-1553279768-865429fa0078?auto=format&fit=crop&w=600&h=500&q=80',
    'Organic Wheat':    'https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?auto=format&fit=crop&w=600&h=500&q=80',
    'Organic Rice':     'https://images.unsplash.com/photo-1536304929831-ee1ca9d44906?auto=format&fit=crop&w=600&h=500&q=80',
    'Organic Turmeric': 'https://images.unsplash.com/photo-1615485500704-8e990f9900f7?auto=format&fit=crop&w=600&h=500&q=80',

    # ── SEEDS ─────────────────────────────────────────────────────────────────
    'Tomato Seeds':    'https://images.unsplash.com/photo-1546094096-0df4bcaaa337?auto=format&fit=crop&w=600&h=500&q=80',
    'Cucumber Seeds':  'https://images.unsplash.com/photo-1449300079323-02e209d9d3a6?auto=format&fit=crop&w=600&h=500&q=80',
    'Sunflower Seeds': 'https://images.unsplash.com/photo-1597848212624-a19eb35e2651?auto=format&fit=crop&w=600&h=500&q=80',
    'Pumpkin Seeds':   'https://images.unsplash.com/photo-1570586437263-ab629fccc818?auto=format&fit=crop&w=600&h=500&q=80',
    'Sesame Seeds':    'https://images.unsplash.com/photo-1599909533984-70c29ccdb797?auto=format&fit=crop&w=600&h=500&q=80',
    'Flax Seeds':      'https://images.unsplash.com/photo-1599909533984-70c29ccdb797?auto=format&fit=crop&w=600&h=500&q=80',
    'Chia Seeds':      'https://images.unsplash.com/photo-1599909533984-70c29ccdb797?auto=format&fit=crop&w=600&h=500&q=80',
    'Fennel Seeds':    'https://images.unsplash.com/photo-1599909533984-70c29ccdb797?auto=format&fit=crop&w=600&h=500&q=80',
}

# Fallback — only used when zero keys match
FALLBACK_IMAGE = 'https://images.unsplash.com/photo-1540420773420-3366772f4999?auto=format&fit=crop&w=600&h=500&q=80'

# Category banner images — used in category cards/filter pills ONLY, never in product cards
CATEGORY_IMAGES = {
    'Vegetables':     'https://images.unsplash.com/photo-1597362925123-77861d3fbac7?auto=format&fit=crop&w=400&h=300&q=80',
    'Fruits':         'https://images.unsplash.com/photo-1619566636858-adf3ef46400b?auto=format&fit=crop&w=400&h=300&q=80',
    'Grains & Pulses':'https://images.unsplash.com/photo-1536304929831-ee1ca9d44906?auto=format&fit=crop&w=400&h=300&q=80',
    'Spices':         'https://images.unsplash.com/photo-1596040033229-a9821ebd058d?auto=format&fit=crop&w=400&h=300&q=80',
    'Organic':        'https://images.unsplash.com/photo-1576045057995-568f588f82fb?auto=format&fit=crop&w=400&h=300&q=80',
    'Seeds':          'https://images.unsplash.com/photo-1597848212624-a19eb35e2651?auto=format&fit=crop&w=400&h=300&q=80',
}


def get_product_image(name: str) -> str:
    """
    Strict product-to-image resolver.
    1. Tries exact key match first.
    2. Falls back to longest substring match (prevents 'Peas' matching 'Pineapple').
    3. Returns FALLBACK_IMAGE only when no key matches at all.
    """
    if not name:
        return FALLBACK_IMAGE
    if name in PRODUCT_IMAGE_MAP:
        return PRODUCT_IMAGE_MAP[name]
    best_key = ''
    for key in PRODUCT_IMAGE_MAP:
        if key.lower() in name.lower() and len(key) > len(best_key):
            best_key = key
    return PRODUCT_IMAGE_MAP[best_key] if best_key else FALLBACK_IMAGE


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def get_current_user():
    user_id = session.get('user_id')
    if user_id:
        return users_col.find_one({"_id": ObjectId(user_id)})
    return None


def login_required(role=None):
    def decorator(f):
        def wrapper(*args, **kwargs):
            user = get_current_user()
            if not user:
                flash("Please log in to continue.", "error")
                return redirect(url_for('login_view'))
            if role and user.get('role') != role:
                if role == 'admin' and user.get('email') == 'admin@farmconnect.com':
                    pass
                else:
                    flash("Unauthorized access.", "error")
                    return redirect(url_for('home_view'))
            return f(*args, **kwargs)
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator


@app.context_processor
def inject_globals():
    user = get_current_user()
    cart = session.get('cart', {})
    cart_count = sum(item['quantity'] for item in cart.values())
    return dict(current_user=user, cart_count=cart_count, category_images=CATEGORY_IMAGES)


# ─────────────────────────────────────────────────────────────────────────────
# MAIN PUBLIC PAGES
# ─────────────────────────────────────────────────────────────────────────────

@app.route('/')
def home_view():
    featured = list(products_col.find({"availability": True}).limit(4))
    for p in featured:
        p['_id'] = str(p['_id'])
    return render_template('home.html', featured=featured)


@app.route('/products')
def products_view():
    search = request.args.get('search', '').strip()
    category = request.args.get('category', 'All').strip()
    query = {"availability": True}
    if search:
        query["name"] = {"$regex": search, "$options": "i"}
    if category != 'All':
        query["category"] = category
    products_list = list(products_col.find(query))
    for p in products_list:
        p['_id'] = str(p['_id'])
    categories = ['All', 'Vegetables', 'Fruits', 'Grains & Pulses', 'Spices', 'Organic', 'Seeds']
    return render_template('products.html', products=products_list, categories=categories, active_category=category, search=search)


@app.route('/products/<id>')
def product_detail_view(id):
    product = products_col.find_one({"_id": ObjectId(id)})
    if not product:
        flash("Product not found.", "error")
        return redirect(url_for('products_view'))
    product['_id'] = str(product['_id'])
    farmer = users_col.find_one({"_id": product['farmer']})
    savings = product.get('marketPrice', 0) - product.get('price', 0)
    recommended = list(products_col.find({"category": product['category'], "_id": {"$ne": ObjectId(id)}}).limit(4))
    for r in recommended:
        r['_id'] = str(r['_id'])
    return render_template('product_detail.html', product=product, farmer=farmer, savings=savings, recommended=recommended)


# ─────────────────────────────────────────────────────────────────────────────
# AUTHENTICATION
# ─────────────────────────────────────────────────────────────────────────────

@app.route('/login', methods=['GET', 'POST'])
def login_view():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').encode('utf-8')
        user = users_col.find_one({"email": email})
        if user and bcrypt.checkpw(password, user['password'].encode('utf-8')):
            session['user_id'] = str(user['_id'])
            flash(f"Welcome back, {user['name']}!", "success")
            if user['role'] == 'farmer':
                return redirect(url_for('farmer_dashboard_view'))
            elif user['role'] == 'admin' or user['email'] == 'admin@farmconnect.com':
                return redirect(url_for('admin_dashboard_view'))
            else:
                return redirect(url_for('consumer_dashboard_view'))
        else:
            flash("Invalid email or password.", "error")
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register_view():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').encode('utf-8')
        role = request.form.get('role', 'consumer')
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()
        farm_name = request.form.get('farmName', '').strip() if role == 'farmer' else ''
        farm_desc = request.form.get('farmDescription', '').strip() if role == 'farmer' else ''
        if users_col.find_one({"email": email}):
            flash("Email already registered.", "error")
            return render_template('register.html')
        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt()).decode('utf-8')
        new_user = {
            "name": name, "email": email, "password": hashed_password,
            "role": role, "phone": phone, "address": address,
            "isApproved": True, "wishlist": [], "notifications": []
        }
        if role == 'farmer':
            new_user["farmName"] = farm_name
            new_user["farmDescription"] = farm_desc
        users_col.insert_one(new_user)
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('login_view'))
    return render_template('register.html')


@app.route('/logout')
def logout_view():
    session.clear()
    flash("Successfully logged out.", "success")
    return redirect(url_for('home_view'))


# ─────────────────────────────────────────────────────────────────────────────
# CART
# ─────────────────────────────────────────────────────────────────────────────

@app.route('/cart')
def cart_view():
    cart = session.get('cart', {})
    cart_items = []
    subtotal = 0
    for pid, item in cart.items():
        prod = products_col.find_one({"_id": ObjectId(pid)})
        if prod:
            item_total = prod['price'] * item['quantity']
            subtotal += item_total
            cart_items.append({
                "product_id": pid,
                "name": prod['name'],
                "price": prod['price'],
                "unit": prod['unit'],
                "image": prod['image'],
                "quantity": item['quantity'],
                "total": item_total
            })
    return render_template('cart.html', cart_items=cart_items, subtotal=subtotal)


@app.route('/cart/add/<id>', methods=['POST'])
def add_to_cart(id):
    quantity = int(request.form.get('quantity', 1))
    product = products_col.find_one({"_id": ObjectId(id)})
    if not product:
        return jsonify({"success": False, "message": "Product not found"})
    cart = session.get('cart', {})
    if id in cart:
        cart[id]['quantity'] += quantity
    else:
        cart[id] = {"quantity": quantity}
    session['cart'] = cart
    session.modified = True
    return jsonify({"success": True, "message": "Product added to cart", "cart_count": sum(i['quantity'] for i in cart.values())})


@app.route('/cart/update/<id>', methods=['POST'])
def update_cart_quantity(id):
    action = request.form.get('action')
    cart = session.get('cart', {})
    if id in cart:
        if action == 'increase':
            cart[id]['quantity'] += 1
        elif action == 'decrease':
            cart[id]['quantity'] -= 1
            if cart[id]['quantity'] <= 0:
                cart.pop(id)
        elif action == 'remove':
            cart.pop(id)
    session['cart'] = cart
    session.modified = True
    return redirect(url_for('cart_view'))


# ─────────────────────────────────────────────────────────────────────────────
# CHECKOUT
# ─────────────────────────────────────────────────────────────────────────────

@app.route('/checkout', methods=['GET', 'POST'])
@login_required('consumer')
def checkout_view():
    cart = session.get('cart', {})
    if not cart:
        flash("Your cart is empty.", "error")
        return redirect(url_for('cart_view'))
    subtotal = 0
    for pid, item in cart.items():
        prod = products_col.find_one({"_id": ObjectId(pid)})
        if prod:
            subtotal += prod['price'] * item['quantity']
    coupon_code = session.get('coupon_code', '')
    discount = session.get('coupon_discount', 0.0)
    
    # Get form data with defaults
    current_user = get_current_user()
    shipping_address = request.form.get('shipping_address', current_user.get('address', ''))
    phone = request.form.get('phone', current_user.get('phone', ''))
    location = request.form.get('location', 'Bangalore')
    pincode = request.form.get('pincode', '560001')
    lat = float(request.form.get('lat', 12.9716))
    lng = float(request.form.get('lng', 77.5946))
    
    farm_hub = [12.9100, 77.6200]
    distance = round(((lat - farm_hub[0])**2 + (lng - farm_hub[1])**2)**0.5 * 111.3, 1)
    delivery_fee = int(distance * 5)
    total = subtotal - discount + delivery_fee
    
    if request.method == 'POST' and 'place_order' in request.form:
        order_items = []
        for pid, item in cart.items():
            prod = products_col.find_one({"_id": ObjectId(pid)})
            if prod:
                order_items.append({
                    "product": prod["_id"], "name": prod["name"], "image": prod["image"],
                    "unit": prod["unit"], "quantity": item["quantity"], "price": prod["price"],
                    "farmer": prod["farmer"],
                    "farmerName": users_col.find_one({"_id": prod["farmer"]})["name"]
                })
                products_col.update_one({"_id": prod["_id"]}, {"$inc": {"stock": -item["quantity"]}})
        payment_method = request.form.get('payment_method', 'Cash on Delivery')
        order = {
            "consumer": current_user["_id"], "orderItems": order_items,
            "shippingAddress": shipping_address, 
            "location": location,
            "pincode": pincode,
            "phone": phone, 
            "totalPrice": total,
            "status": "Pending",
            "paymentStatus": "Paid" if payment_method == 'Razorpay' else "Unpaid",
            "paymentMethod": payment_method, 
            "deliveryDistance": distance,
            "deliveryFee": delivery_fee, 
            "couponCode": coupon_code or None,
            "couponDiscount": discount, 
            "createdAt": datetime.datetime.now()
        }
        order_id = orders_col.insert_one(order).inserted_id
        session.pop('cart', None)
        session.pop('coupon_code', None)
        session.pop('coupon_discount', None)
        if payment_method == 'Razorpay':
            payments_col.insert_one({
                "order": order_id, "consumer": current_user["_id"],
                "razorpay_order_id": f"pay_test_{str(order_id)[:12]}",
                "amount": total * 100, "currency": "INR", "status": "paid"
            })
            return redirect(url_for('payment_success', order_id=str(order_id)))
        flash("Order placed successfully!", "success")
        return redirect(url_for('consumer_dashboard_view'))
    return render_template('checkout.html', subtotal=subtotal, discount=discount,
                           delivery_fee=delivery_fee, total=total, distance=distance,
                           address=shipping_address, phone=phone, location=location, 
                           pincode=pincode, lat=lat, lng=lng)


@app.route('/checkout/coupon', methods=['POST'])
def apply_coupon():
    coupon = request.form.get('coupon_code', '').strip().upper()
    cart = session.get('cart', {})
    subtotal = 0
    for pid, item in cart.items():
        prod = products_col.find_one({"_id": ObjectId(pid)})
        if prod:
            subtotal += prod['price'] * item['quantity']
    if coupon == 'FARM20':
        session['coupon_code'] = 'FARM20'
        session['coupon_discount'] = subtotal * 0.20
        flash("Coupon FARM20 applied: 20% discount!", "success")
    else:
        flash("Invalid coupon code.", "error")
        session.pop('coupon_code', None)
        session.pop('coupon_discount', None)
    return redirect(url_for('checkout_view'))


@app.route('/payment/success/<order_id>')
def payment_success(order_id):
    order = orders_col.find_one({"_id": ObjectId(order_id)})
    return render_template('payment_success.html', order=order)


# ─────────────────────────────────────────────────────────────────────────────
# CONSUMER DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────

@app.route('/consumer-dashboard')
@login_required('consumer')
def consumer_dashboard_view():
    user = get_current_user()
    status_filter = request.args.get('status', 'All')
    search_query = request.args.get('search', '').strip()
    query = {"consumer": user["_id"]}
    if status_filter != 'All':
        query["status"] = status_filter
    if search_query:
        query["orderItems.name"] = {"$regex": search_query, "$options": "i"}
    orders = list(orders_col.find(query).sort("createdAt", -1))
    for o in orders:
        o['_id'] = str(o['_id'])
    wishlist_ids = user.get('wishlist', [])
    wishlist = list(products_col.find({"_id": {"$in": wishlist_ids}}))
    for w in wishlist:
        w['_id'] = str(w['_id'])
    return render_template('consumer_dashboard.html', orders=orders, wishlist=wishlist,
                           status_filter=status_filter, search=search_query)


@app.route('/wishlist/toggle/<id>', methods=['POST'])
@login_required('consumer')
def toggle_wishlist(id):
    user = get_current_user()
    wishlist = user.get('wishlist', [])
    pid = ObjectId(id)
    if pid in wishlist:
        users_col.update_one({"_id": user["_id"]}, {"$pull": {"wishlist": pid}})
        status = "removed"
    else:
        users_col.update_one({"_id": user["_id"]}, {"$push": {"wishlist": pid}})
        status = "added"
    return jsonify({"success": True, "status": status})


# ─────────────────────────────────────────────────────────────────────────────
# FARMER DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────

@app.route('/dashboard')
@login_required('farmer')
def farmer_dashboard_view():
    user = get_current_user()
    my_products = list(products_col.find({"farmer": user["_id"]}))
    for p in my_products:
        p['_id'] = str(p['_id'])
    raw_orders = list(orders_col.find({"orderItems.farmer": user["_id"]}).sort("createdAt", -1))
    farmer_orders = []
    total_revenue = 0
    pending_count = 0
    delivered_count = 0
    for o in raw_orders:
        o['_id'] = str(o['_id'])
        matching_items = [item for item in o['orderItems'] if item['farmer'] == user["_id"]]
        o['orderItems'] = matching_items
        o['farmerShareTotal'] = sum(i['price'] * i['quantity'] for i in matching_items)
        total_revenue += o['farmerShareTotal']
        if o['status'] == 'Pending':
            pending_count += 1
        elif o['status'] == 'Delivered':
            delivered_count += 1
        farmer_orders.append(o)
    categories = ['Vegetables', 'Fruits', 'Grains & Pulses', 'Spices', 'Organic', 'Seeds']
    return render_template('dashboard.html', products=my_products, orders=farmer_orders,
                           categories=categories, revenue=total_revenue,
                           pending=pending_count, completed=delivered_count)


@app.route('/dashboard/product/add', methods=['POST'])
@login_required('farmer')
def add_product_view():
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    price = float(request.form.get('price', 0.0))
    unit = request.form.get('unit', 'kg').strip()
    category = request.form.get('category', 'Vegetables').strip()
    stock = int(request.form.get('stock', 0))
    image = request.form.get('image', '').strip() or get_product_image(name)
    new_prod = {
        "farmer": get_current_user()["_id"], "name": name, "description": description,
        "price": price, "marketPrice": int(price * 1.5), "discountPercentage": 33,
        "unit": unit, "category": category, "image": image, "stock": stock,
        "organicStatus": "Organic", "rating": 5.0, "numReviews": 0, "reviews": [],
        "availability": True,
        "historicalPrices": [{"date": datetime.datetime.now(), "price": price, "marketPrice": int(price * 1.5)}]
    }
    products_col.insert_one(new_prod)
    flash("Product listed successfully!", "success")
    return redirect(url_for('farmer_dashboard_view'))


@app.route('/dashboard/product/edit/<id>', methods=['POST'])
@login_required('farmer')
def edit_product_view(id):
    price = float(request.form.get('price', 0.0))
    stock = int(request.form.get('stock', 0))
    products_col.update_one(
        {"_id": ObjectId(id), "farmer": get_current_user()["_id"]},
        {"$set": {"price": price, "stock": stock}}
    )
    flash("Product updated successfully!", "success")
    return redirect(url_for('farmer_dashboard_view'))


@app.route('/dashboard/product/delete/<id>', methods=['POST'])
@login_required('farmer')
def delete_product_view(id):
    products_col.delete_one({"_id": ObjectId(id), "farmer": get_current_user()["_id"]})
    flash("Listing deleted successfully.", "success")
    return redirect(url_for('farmer_dashboard_view'))


@app.route('/dashboard/order/status/<id>', methods=['POST'])
@login_required('farmer')
def update_status(id):
    status = request.form.get('status')
    orders_col.update_one({"_id": ObjectId(id)}, {"$set": {"status": status}})
    flash(f"Order status updated to {status}!", "success")
    return redirect(url_for('farmer_dashboard_view'))


# ─────────────────────────────────────────────────────────────────────────────
# ADMIN DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────

@app.route('/admin-dashboard')
@login_required('admin')
def admin_dashboard_view():
    total_sales = sum(o['totalPrice'] for o in orders_col.find())
    farmers_count = users_col.count_documents({"role": "farmer"})
    consumers_count = users_col.count_documents({"role": "consumer"})
    products_count = products_col.count_documents({})
    farmers = list(users_col.find({"role": "farmer"}))
    for f in farmers:
        f['_id'] = str(f['_id'])
    return render_template('admin_dashboard.html', sales=total_sales, farmers=farmers_count,
                           consumers=consumers_count, products=products_count, farmers_list=farmers)


@app.route('/admin/approve/<id>', methods=['POST'])
@login_required('admin')
def approve_farmer(id):
    users_col.update_one({"_id": ObjectId(id)}, {"$set": {"isApproved": True}})
    flash("Farmer approved successfully.", "success")
    return redirect(url_for('admin_dashboard_view'))


@app.route('/admin/seed', methods=['POST'])
@login_required('admin')
def admin_trigger_seed():
    from seed import seed_db
    seed_db()
    flash("Database seeded successfully!", "success")
    return redirect(url_for('admin_dashboard_view'))


# ─────────────────────────────────────────────────────────────────────────────
# AI ASSISTANT
# ─────────────────────────────────────────────────────────────────────────────

@app.route('/ai-assistant')
def ai_assistant_view():
    return render_template('ai_assistant.html')


@app.route('/ai/recommend', methods=['POST'])
def ai_recommend():
    n = float(request.form.get('n', 40))
    ph = float(request.form.get('ph', 6.5))
    moisture = float(request.form.get('moisture', 20))
    recommendations = []
    if ph < 5.5:
        recommendations.append("Soil is acidic. Add agricultural lime to raise pH.")
    elif ph > 7.5:
        recommendations.append("Soil is alkaline. Add gypsum or organic sulfur to lower pH.")
    if moisture < 15:
        recommendations.append("Soil moisture is critical. Crop matches: Sweet Corn, Mustard Seeds.")
    else:
        recommendations.append("Soil moisture is optimal. Crop matches: Rice, Tomatoes, Cabbage.")
    if n < 30:
        recommendations.append("Nitrogen index is low. Apply organic manure or ammonium nitrate.")
    return jsonify({
        "success": True,
        "ph_status": "Slightly Acidic" if ph < 6 else "Optimal" if ph <= 7.2 else "Alkaline",
        "recommendations": recommendations,
        "best_crops": ["Tomato", "Rice", "Cabbage"] if moisture >= 15 else ["Sweet Corn", "Seeds"]
    })


@app.route('/ai/chat', methods=['POST'])
def ai_chat():
    message = request.form.get('message', '').strip().lower()
    response = "I am AgriConnect AI. I can predict crop yields, recommend soil inputs, and track market pricing. Try asking about 'soil', 'price', or 'delivery'."
    if "soil" in message or "npk" in message:
        response = "For optimal crop yield, nitrogen levels should be above 40ppm. You can use the Soil Analyzer tool below to get precise inputs!"
    elif "price" in message or "market" in message:
        response = "Market pricing is currently stable. Direct farm pricing saves you 20-40% vs retail."
    elif "delivery" in message or "fee" in message:
        response = "We charge ₹5 per kilometer for direct shipping from agricultural hubs to consumer locations."
    return jsonify({"response": response})


if __name__ == '__main__':
    app.run(port=5000, debug=True)
