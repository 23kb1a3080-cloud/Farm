# Farm Connect 🌱

A full-stack, direct-to-consumer farm marketplace built with **Flask and MongoDB** that connects local farmers directly with buyers — eliminating middlemen and maximizing farmer profits.

---

## Tech Stack

- **Backend**: Python, Flask
- **Database**: MongoDB (via PyMongo)
- **Frontend**: Jinja2 Templates, Tailwind CSS, Leaflet.js (interactive maps)
- **Authentication**: bcrypt password hashing, Flask session management
- **Deployment**: AWS EC2 (Ubuntu 22.04), Gunicorn, Nginx

---

## Features

### 👨‍🌾 Farmer
- Register and manage a farm profile
- Add, edit, and delete product listings with automatic image mapping
- Track incoming orders and update order statuses
- View total revenue, pending and delivered order counts

### 🛒 Consumer
- Browse products by category with search and filter support
- Add to cart with real-time quantity management
- Wishlist for saving favourite products
- Checkout with:
  - **Location / City** field
  - **Pincode** (6-digit validation)
  - Full shipping address and phone number
  - Interactive Leaflet map for precise delivery location
  - Distance-based delivery fee calculation
  - Coupon code support (`FARM20` for 20% off)
- **Cash on Delivery** as the payment method
- Order history with delivery details (location, pincode, address, phone)

### 🛡️ Admin
- Dashboard with total sales, farmer count, consumer count, product count
- Approve farmers
- Trigger database seeding

### 🤖 AI Assistant
- Soil analysis with NPK and pH inputs
- Crop recommendations based on soil moisture
- Agricultural advice chatbot

---

## Product Categories

| Category | Description |
|---|---|
| Vegetables | 25+ fresh vegetables |
| Fruits | 25+ seasonal fruits |
| Grains & Pulses | Rice, Wheat |
| Spices | 10 common spices |
| Organic | Certified organic produce |
| Seeds | Planting seeds |

---

## Folder Structure

```
Farm/
├── app.py                  # Main Flask application (all routes, image map)
├── config.py               # MongoDB URI and secret key configuration
├── database.py             # PyMongo collections setup
├── seed.py                 # Database seeder (farmers, consumers, products)
├── requirements.txt        # Python dependencies
├── deploy.sh               # Automated AWS EC2 deployment script
├── templates/
│   ├── base.html           # Base layout with navbar and flash messages
│   ├── home.html           # Landing page with featured products
│   ├── products.html       # Product listing with search and category filter
│   ├── product_detail.html # Single product page with reviews and recommendations
│   ├── cart.html           # Shopping cart
│   ├── checkout.html       # Checkout with location, pincode, map
│   ├── login.html          # Login page
│   ├── register.html       # Registration page
│   ├── dashboard.html      # Farmer dashboard
│   ├── consumer_dashboard.html  # Consumer orders and wishlist
│   ├── admin_dashboard.html     # Admin controls
│   ├── ai_assistant.html        # AI soil and crop advisor
│   └── payment_success.html     # Order confirmation
└── .gitignore
```

---

## Getting Started (Local)

### Prerequisites

- Python 3.10+
- MongoDB running locally or a [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) connection string

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/23kb1a3080-cloud/Farm.git
   cd Farm
   ```

2. **Create and activate a virtual environment**
   ```bash
   python3 -m venv venv
   # Windows
   venv\Scripts\activate
   # Mac/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the database**

   Edit `config.py` and update the `MONGO_URI`:
   ```python
   class Config:
       SECRET_KEY = 'your-secret-key'
       MONGO_URI = 'mongodb://127.0.0.1:27017/farmconnect'
       # OR MongoDB Atlas:
       # MONGO_URI = 'mongodb+srv://user:password@cluster.mongodb.net/farmconnect'
   ```

5. **Seed the database**
   ```bash
   python seed.py
   ```
   This creates:
   - 1 Admin user
   - 100 Farmers
   - 1000 Consumers
   - 500 Products

6. **Run the application**
   ```bash
   python app.py
   ```
   Visit: [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## Default Login Credentials

| Role | Email | Password |
|---|---|---|
| Admin | admin@farmconnect.com | admin123 |
| Farmer | farmer1@farmconnect.com | password123 |
| Consumer | consumer1@gmail.com | password123 |

---

## Deployment on AWS EC2

### Quick Deploy (Automated)

After launching an EC2 instance (Ubuntu 22.04, t2.micro) and connecting via SSH:

```bash
wget https://raw.githubusercontent.com/23kb1a3080-cloud/Farm/main/deploy.sh
chmod +x deploy.sh
./deploy.sh
```

Then seed the database:
```bash
cd ~/Farm
source venv/bin/activate
python3 seed.py
```

### Manual Steps Summary

1. Install dependencies: `sudo apt install python3 python3-pip python3-venv git nginx -y`
2. Clone repo: `git clone https://github.com/23kb1a3080-cloud/Farm.git`
3. Install Python packages: `pip install -r requirements.txt gunicorn`
4. Configure `config.py` with MongoDB Atlas URI
5. Setup Gunicorn systemd service
6. Configure Nginx as reverse proxy on port 80
7. Access at `http://YOUR_EC2_PUBLIC_IP`

> See `AWS_EC2_DEPLOYMENT_GUIDE.md` for the full step-by-step guide.

---

## EC2 Security Group Rules

| Type | Port | Source |
|---|---|---|
| SSH | 22 | Your IP |
| HTTP | 80 | 0.0.0.0/0 |
| HTTPS | 443 | 0.0.0.0/0 |
| Custom TCP | 5000 | 0.0.0.0/0 |

---

## Useful Commands (on EC2)

```bash
# View live application logs
sudo journalctl -u farm -f

# Restart application
sudo systemctl restart farm

# Pull latest code and restart
cd ~/Farm && git pull origin main && sudo systemctl restart farm

# Check service status
sudo systemctl status farm nginx
```

---

## Cost (AWS Free Tier)

| Service | Cost |
|---|---|
| EC2 t2.micro | Free for 12 months (750 hrs/month) |
| MongoDB Atlas M0 | Free forever |
| Data Transfer | 15 GB/month free |

---

## Python Dependencies

```
Flask==3.0.3
pymongo==4.8.0
bcrypt==4.1.3
python-dotenv==1.0.1
```

---

## Repository

**GitHub:** [https://github.com/23kb1a3080-cloud/Farm](https://github.com/23kb1a3080-cloud/Farm)
