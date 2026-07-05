# 🚀 AWS EC2 Deployment Guide - Farm Marketplace

Complete step-by-step guide to deploy your Flask Farm Marketplace application on AWS EC2.

---

## 📋 Prerequisites

1. AWS Account with billing enabled
2. Your GitHub repository URL: `https://github.com/23kb1a3080-cloud/Farm`
3. MongoDB Atlas account (for cloud database) OR Install MongoDB on EC2

---

## Part 1: Setup MongoDB Atlas (Recommended)

### Step 1: Create MongoDB Atlas Account
1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Sign up for a free account
3. Create a new cluster (Free tier M0 is sufficient)

### Step 2: Configure Database Access
1. Click **Database Access** → **Add New Database User**
2. Username: `farmuser`
3. Password: Create a strong password (save it!)
4. User Privileges: **Read and write to any database**
5. Click **Add User**

### Step 3: Configure Network Access
1. Click **Network Access** → **Add IP Address**
2. Click **Allow Access from Anywhere** (0.0.0.0/0)
3. Click **Confirm**

### Step 4: Get Connection String
1. Click **Database** → **Connect**
2. Choose **Connect your application**
3. Copy the connection string (looks like):
   ```
   mongodb+srv://farmuser:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```
4. Replace `<password>` with your actual password
5. Save this for later!

---

## Part 2: Launch AWS EC2 Instance

### Step 1: Sign in to AWS Console
1. Go to [AWS Console](https://console.aws.amazon.com)
2. Sign in with your credentials
3. Select your preferred region (e.g., **us-east-1** or **ap-south-1** for India)

### Step 2: Launch EC2 Instance
1. Navigate to **EC2 Dashboard**
2. Click **Launch Instance**

### Step 3: Configure Instance
**Name and tags:**
- Name: `Farm-Marketplace-Server`

**Application and OS Images:**
- AMI: **Ubuntu Server 22.04 LTS** (Free tier eligible)

**Instance type:**
- Select: **t2.micro** (Free tier eligible - 1 vCPU, 1 GB RAM)

**Key pair:**
- Click **Create new key pair**
- Key pair name: `farm-marketplace-key`
- Key pair type: **RSA**
- Private key format: **pem** (for Mac/Linux) or **ppk** (for Windows/PuTTY)
- Click **Create key pair** and **download it** (save it safely!)

**Network settings:**
- Click **Edit**
- Auto-assign public IP: **Enable**
- Firewall (security groups): **Create security group**
- Security group name: `farm-marketplace-sg`

**Add these rules:**
1. **SSH** - Port 22 - Source: My IP (for security) or Anywhere (0.0.0.0/0)
2. **HTTP** - Port 80 - Source: Anywhere (0.0.0.0/0)
3. **HTTPS** - Port 443 - Source: Anywhere (0.0.0.0/0)
4. **Custom TCP** - Port 5000 - Source: Anywhere (0.0.0.0/0) [Flask app]

**Configure storage:**
- Size: **20 GB** (Free tier includes up to 30 GB)
- Volume type: **gp2**

### Step 4: Launch Instance
1. Click **Launch instance**
2. Wait for instance state to be **Running**
3. Note down the **Public IPv4 address** (e.g., 3.15.123.45)

---

## Part 3: Connect to EC2 Instance

### For Windows Users (using PuTTY):

1. **Convert .pem to .ppk:**
   - Download PuTTYgen
   - Load your `.pem` file
   - Click "Save private key"
   - Save as `.ppk` file

2. **Connect using PuTTY:**
   - Open PuTTY
   - Host Name: `ubuntu@YOUR_PUBLIC_IP`
   - Port: 22
   - Connection → SSH → Auth → Browse for your `.ppk` file
   - Click **Open**

### For Mac/Linux Users (using Terminal):

```bash
# Set proper permissions for your key
chmod 400 farm-marketplace-key.pem

# Connect to EC2
ssh -i farm-marketplace-key.pem ubuntu@YOUR_PUBLIC_IP
```

Replace `YOUR_PUBLIC_IP` with your actual EC2 public IP address.

---

## Part 4: Setup Server Environment

Once connected to EC2, run these commands:

### Step 1: Update System
```bash
sudo apt update
sudo apt upgrade -y
```

### Step 2: Install Python and Required Tools
```bash
# Install Python 3 and pip
sudo apt install python3 python3-pip python3-venv -y

# Install Git
sudo apt install git -y

# Install nginx (web server)
sudo apt install nginx -y

# Install supervisor (process manager)
sudo apt install supervisor -y
```

### Step 3: Clone Your Repository
```bash
# Navigate to home directory
cd ~

# Clone your GitHub repository
git clone https://github.com/23kb1a3080-cloud/Farm.git

# Navigate into the project
cd Farm
```

### Step 4: Create Virtual Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Install additional production server
pip install gunicorn
```

### Step 5: Create Configuration File
```bash
# Create config.py file
nano config.py
```

**Paste this content** (replace with your MongoDB connection string):

```python
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-super-secret-key-change-this-in-production'
    
    # MongoDB Atlas Connection String
    # Replace <password> with your MongoDB Atlas password
    # Replace <dbname> with your database name (e.g., farmdb)
    MONGO_URI = os.environ.get('MONGO_URI') or 'mongodb+srv://farmuser:YOUR_PASSWORD@cluster0.xxxxx.mongodb.net/farmdb?retryWrites=true&w=majority'
    
    # Razorpay Keys (if using payment gateway)
    RAZORPAY_KEY_ID = os.environ.get('RAZORPAY_KEY_ID') or 'your_razorpay_key_id'
    RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET') or 'your_razorpay_secret'
```

**Save and exit:**
- Press `Ctrl + X`
- Press `Y`
- Press `Enter`

### Step 6: Test the Application
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Run the app (test)
python3 app.py
```

**Test in browser:** Go to `http://YOUR_PUBLIC_IP:5000`

If it works, press `Ctrl + C` to stop the server.

---

## Part 5: Setup Production Server with Gunicorn and Nginx

### Step 1: Create Gunicorn Service File
```bash
sudo nano /etc/systemd/system/farm.service
```

**Paste this content:**

```ini
[Unit]
Description=Gunicorn instance to serve Farm Marketplace
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/Farm
Environment="PATH=/home/ubuntu/Farm/venv/bin"
ExecStart=/home/ubuntu/Farm/venv/bin/gunicorn --workers 3 --bind 0.0.0.0:5000 app:app

[Install]
WantedBy=multi-user.target
```

**Save and exit** (Ctrl + X, Y, Enter)

### Step 2: Start and Enable the Service
```bash
# Reload systemd
sudo systemctl daemon-reload

# Start the service
sudo systemctl start farm

# Enable service to start on boot
sudo systemctl enable farm

# Check status
sudo systemctl status farm
```

### Step 3: Configure Nginx as Reverse Proxy
```bash
sudo nano /etc/nginx/sites-available/farm
```

**Paste this content:**

```nginx
server {
    listen 80;
    server_name YOUR_PUBLIC_IP;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /home/ubuntu/Farm/static;
    }
}
```

Replace `YOUR_PUBLIC_IP` with your actual EC2 public IP.

**Save and exit** (Ctrl + X, Y, Enter)

### Step 4: Enable Nginx Configuration
```bash
# Create symbolic link
sudo ln -s /etc/nginx/sites-available/farm /etc/nginx/sites-enabled/

# Remove default nginx site
sudo rm /etc/nginx/sites-enabled/default

# Test nginx configuration
sudo nginx -t

# Restart nginx
sudo systemctl restart nginx

# Enable nginx to start on boot
sudo systemctl enable nginx
```

---

## Part 6: Seed the Database (First Time Only)

```bash
# Activate virtual environment
cd ~/Farm
source venv/bin/activate

# Run seed script
python3 seed.py
```

This will create:
- 1 Admin user
- 100 Farmers
- 1000 Consumers
- 500 Products

---

## Part 7: Access Your Website

### Open your browser and visit:
```
http://YOUR_PUBLIC_IP
```

Replace `YOUR_PUBLIC_IP` with your EC2 instance's public IP address.

### Default Login Credentials:

**Admin:**
- Email: `admin@farmconnect.com`
- Password: `admin123`

**Consumer:**
- Email: `consumer1@gmail.com`
- Password: `password123`

**Farmer:**
- Email: `farmer1@farmconnect.com`
- Password: `password123`

---

## Part 8: Useful Commands

### Check Application Logs
```bash
# View Gunicorn service logs
sudo journalctl -u farm -f

# View Nginx access logs
sudo tail -f /var/log/nginx/access.log

# View Nginx error logs
sudo tail -f /var/log/nginx/error.log
```

### Restart Services
```bash
# Restart Farm application
sudo systemctl restart farm

# Restart Nginx
sudo systemctl restart nginx

# Check service status
sudo systemctl status farm
sudo systemctl status nginx
```

### Update Application Code
```bash
cd ~/Farm
git pull origin main
sudo systemctl restart farm
```

### Stop Services
```bash
sudo systemctl stop farm
sudo systemctl stop nginx
```

---

## Part 9: Security Best Practices

### 1. Update EC2 Security Group
- Go to EC2 Dashboard → Security Groups
- Find `farm-marketplace-sg`
- For SSH (Port 22), change source from "Anywhere" to "My IP"

### 2. Create Strong Passwords
- Change the SECRET_KEY in config.py to a random string
- Use strong MongoDB passwords

### 3. Enable Firewall (UFW)
```bash
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 80/tcp      # HTTP
sudo ufw allow 443/tcp     # HTTPS
sudo ufw enable
```

### 4. Regular Updates
```bash
# Run weekly
sudo apt update && sudo apt upgrade -y
```

---

## Part 10: Troubleshooting

### Issue: Can't access website
**Solution:**
1. Check if services are running:
   ```bash
   sudo systemctl status farm
   sudo systemctl status nginx
   ```
2. Check EC2 security group allows port 80
3. Check public IP address is correct

### Issue: 502 Bad Gateway
**Solution:**
1. Check Gunicorn service:
   ```bash
   sudo systemctl status farm
   sudo journalctl -u farm -n 50
   ```
2. Restart services:
   ```bash
   sudo systemctl restart farm
   sudo systemctl restart nginx
   ```

### Issue: Database connection error
**Solution:**
1. Verify MongoDB Atlas connection string in config.py
2. Check MongoDB Atlas Network Access allows your IP
3. Test connection:
   ```bash
   cd ~/Farm
   source venv/bin/activate
   python3 -c "from database import db; print(db.name)"
   ```

### Issue: Application not updating
**Solution:**
```bash
cd ~/Farm
git pull origin main
sudo systemctl restart farm
sudo systemctl restart nginx
```

---

## Part 11: Optional - Setup Domain Name

### If you have a domain (e.g., farmmarket.com):

1. **Point DNS to EC2:**
   - Go to your domain registrar (GoDaddy, Namecheap, etc.)
   - Add an A record pointing to your EC2 public IP

2. **Update Nginx configuration:**
   ```bash
   sudo nano /etc/nginx/sites-available/farm
   ```
   
   Change `server_name YOUR_PUBLIC_IP;` to:
   ```nginx
   server_name farmmarket.com www.farmmarket.com;
   ```

3. **Restart Nginx:**
   ```bash
   sudo systemctl restart nginx
   ```

4. **Install SSL Certificate (HTTPS):**
   ```bash
   sudo apt install certbot python3-certbot-nginx -y
   sudo certbot --nginx -d farmmarket.com -d www.farmmarket.com
   ```

---

## 🎉 Deployment Complete!

Your Farm Marketplace is now live on AWS EC2!

### Quick Links:
- **Website:** `http://YOUR_PUBLIC_IP`
- **EC2 Dashboard:** https://console.aws.amazon.com/ec2
- **MongoDB Atlas:** https://cloud.mongodb.com

### Need Help?
- Check logs: `sudo journalctl -u farm -f`
- Restart app: `sudo systemctl restart farm`
- Update code: `cd ~/Farm && git pull && sudo systemctl restart farm`

---

## 💰 Cost Estimation

**Free Tier (First 12 months):**
- EC2 t2.micro: Free for 750 hours/month
- MongoDB Atlas M0: Free forever
- Data Transfer: 15 GB/month free

**After Free Tier:**
- EC2 t2.micro: ~$8-10/month
- MongoDB Atlas M10: ~$57/month (optional upgrade)

---

## 📚 Additional Resources

- [AWS EC2 Documentation](https://docs.aws.amazon.com/ec2/)
- [MongoDB Atlas Documentation](https://docs.atlas.mongodb.com/)
- [Flask Deployment](https://flask.palletsprojects.com/en/2.3.x/deploying/)
- [Nginx Documentation](https://nginx.org/en/docs/)

---

**Created by:** Kiro AI Assistant  
**Date:** 2026-07-05  
**Repository:** https://github.com/23kb1a3080-cloud/Farm
