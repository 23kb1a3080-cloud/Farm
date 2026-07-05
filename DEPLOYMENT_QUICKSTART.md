# 🚀 Quick Deployment Guide

## Two Ways to Deploy

### Option 1: Automated Deployment (Recommended)

After connecting to your EC2 instance via SSH:

```bash
# Download and run the deployment script
wget https://raw.githubusercontent.com/23kb1a3080-cloud/Farm/main/deploy.sh
chmod +x deploy.sh
./deploy.sh
```

The script will automatically:
- ✅ Install all dependencies
- ✅ Clone the repository
- ✅ Setup Python virtual environment
- ✅ Configure Gunicorn and Nginx
- ✅ Start all services

### Option 2: Manual Deployment

Follow the detailed guide: [AWS_EC2_DEPLOYMENT_GUIDE.md](./AWS_EC2_DEPLOYMENT_GUIDE.md)

---

## Prerequisites

1. **AWS EC2 Instance** running Ubuntu 22.04
2. **MongoDB Atlas Account** - [Sign up here](https://www.mongodb.com/cloud/atlas)
3. **SSH Access** to your EC2 instance

---

## Quick Setup Steps

### 1. Setup MongoDB Atlas (5 minutes)
1. Create free MongoDB Atlas account
2. Create a cluster (M0 free tier)
3. Add database user and password
4. Allow access from anywhere (0.0.0.0/0)
5. Get connection string

### 2. Launch EC2 Instance (5 minutes)
- **AMI:** Ubuntu Server 22.04 LTS
- **Instance Type:** t2.micro (free tier)
- **Security Group Rules:**
  - SSH (22) - Your IP
  - HTTP (80) - Anywhere
  - HTTPS (443) - Anywhere
  - Custom TCP (5000) - Anywhere

### 3. Connect to EC2
```bash
# Windows: Use PuTTY
# Mac/Linux:
ssh -i your-key.pem ubuntu@YOUR_PUBLIC_IP
```

### 4. Run Deployment Script
```bash
wget https://raw.githubusercontent.com/23kb1a3080-cloud/Farm/main/deploy.sh
chmod +x deploy.sh
./deploy.sh
```

When prompted, enter your MongoDB connection string.

### 5. Seed Database
```bash
cd ~/Farm
source venv/bin/activate
python3 seed.py
```

### 6. Access Your Website
```
http://YOUR_PUBLIC_IP
```

**Default Credentials:**
- Admin: `admin@farmconnect.com` / `admin123`
- Consumer: `consumer1@gmail.com` / `password123`
- Farmer: `farmer1@farmconnect.com` / `password123`

---

## Troubleshooting

### Can't access website?
```bash
# Check services
sudo systemctl status farm
sudo systemctl status nginx

# View logs
sudo journalctl -u farm -n 50

# Restart services
sudo systemctl restart farm nginx
```

### Database connection error?
1. Check MongoDB Atlas connection string in `config.py`
2. Verify MongoDB Atlas allows connections from 0.0.0.0/0
3. Test connection:
```bash
cd ~/Farm
source venv/bin/activate
python3 -c "from database import db; print(db.name)"
```

---

## Useful Commands

```bash
# Update application
cd ~/Farm && git pull && sudo systemctl restart farm

# View logs
sudo journalctl -u farm -f

# Restart services
sudo systemctl restart farm nginx

# Check status
sudo systemctl status farm nginx
```

---

## Need Detailed Instructions?

See the complete guide: [AWS_EC2_DEPLOYMENT_GUIDE.md](./AWS_EC2_DEPLOYMENT_GUIDE.md)

---

## Support

- 📧 Repository: https://github.com/23kb1a3080-cloud/Farm
- 📖 Full Guide: [AWS_EC2_DEPLOYMENT_GUIDE.md](./AWS_EC2_DEPLOYMENT_GUIDE.md)
- 🐛 Issues: [GitHub Issues](https://github.com/23kb1a3080-cloud/Farm/issues)
