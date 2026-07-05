#!/bin/bash

# ============================================================================
# Farm Marketplace - AWS EC2 Deployment Script
# ============================================================================
# This script automates the deployment process on AWS EC2
# Run this script after connecting to your EC2 instance
# ============================================================================

set -e  # Exit on error

echo "============================================"
echo "🚀 Farm Marketplace Deployment Script"
echo "============================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored messages
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_info() {
    echo -e "${YELLOW}[i]${NC} $1"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    print_error "Please do not run as root. Run as ubuntu user."
    exit 1
fi

# Step 1: Update system
print_info "Step 1/8: Updating system packages..."
sudo apt update && sudo apt upgrade -y
print_status "System updated successfully"
echo ""

# Step 2: Install dependencies
print_info "Step 2/8: Installing Python, Git, Nginx, and Supervisor..."
sudo apt install -y python3 python3-pip python3-venv git nginx supervisor
print_status "Dependencies installed successfully"
echo ""

# Step 3: Clone repository
print_info "Step 3/8: Cloning Farm repository..."
cd ~
if [ -d "Farm" ]; then
    print_info "Farm directory already exists. Pulling latest changes..."
    cd Farm
    git pull origin main
else
    git clone https://github.com/23kb1a3080-cloud/Farm.git
    cd Farm
fi
print_status "Repository cloned/updated successfully"
echo ""

# Step 4: Setup Python virtual environment
print_info "Step 4/8: Setting up Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn
print_status "Virtual environment configured successfully"
echo ""

# Step 5: Configure MongoDB connection
print_info "Step 5/8: Setting up configuration..."
if [ ! -f "config.py" ]; then
    print_info "Creating config.py file..."
    echo "Please enter your MongoDB connection string:"
    read -r MONGO_URI
    
    cat > config.py << EOF
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-super-secret-key-change-this-in-production-$(openssl rand -hex 16)'
    
    # MongoDB Connection String
    MONGO_URI = os.environ.get('MONGO_URI') or '${MONGO_URI}'
    
    # Razorpay Keys (optional)
    RAZORPAY_KEY_ID = os.environ.get('RAZORPAY_KEY_ID') or ''
    RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET') or ''
EOF
    print_status "config.py created successfully"
else
    print_info "config.py already exists. Skipping..."
fi
echo ""

# Step 6: Setup systemd service
print_info "Step 6/8: Configuring Gunicorn systemd service..."
sudo tee /etc/systemd/system/farm.service > /dev/null << EOF
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
EOF

sudo systemctl daemon-reload
sudo systemctl enable farm
print_status "Systemd service configured successfully"
echo ""

# Step 7: Configure Nginx
print_info "Step 7/8: Configuring Nginx reverse proxy..."
PUBLIC_IP=$(curl -s http://checkip.amazonaws.com)
print_info "Detected public IP: $PUBLIC_IP"

sudo tee /etc/nginx/sites-available/farm > /dev/null << EOF
server {
    listen 80;
    server_name $PUBLIC_IP;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /static {
        alias /home/ubuntu/Farm/static;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/farm /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl enable nginx
print_status "Nginx configured successfully"
echo ""

# Step 8: Start services
print_info "Step 8/8: Starting services..."
sudo systemctl start farm
sudo systemctl restart nginx
print_status "Services started successfully"
echo ""

# Check service status
print_info "Checking service status..."
if sudo systemctl is-active --quiet farm; then
    print_status "Farm application is running"
else
    print_error "Farm application failed to start. Check logs with: sudo journalctl -u farm -n 50"
fi

if sudo systemctl is-active --quiet nginx; then
    print_status "Nginx is running"
else
    print_error "Nginx failed to start. Check logs with: sudo journalctl -u nginx -n 50"
fi
echo ""

# Final instructions
echo "============================================"
echo "🎉 Deployment Complete!"
echo "============================================"
echo ""
echo "Your Farm Marketplace is now live at:"
echo "👉 http://$PUBLIC_IP"
echo ""
echo "📝 Next Steps:"
echo "1. Seed the database: cd ~/Farm && source venv/bin/activate && python3 seed.py"
echo "2. Visit http://$PUBLIC_IP in your browser"
echo "3. Login with admin@farmconnect.com / admin123"
echo ""
echo "📊 Useful Commands:"
echo "  - View logs: sudo journalctl -u farm -f"
echo "  - Restart app: sudo systemctl restart farm"
echo "  - Update code: cd ~/Farm && git pull && sudo systemctl restart farm"
echo ""
echo "============================================"
