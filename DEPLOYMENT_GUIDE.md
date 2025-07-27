# EduManage Ultimate - Complete Deployment Guide

## 🚀 Production Deployment Guide

This comprehensive guide will help you deploy EduManage Ultimate School Management System in various environments - from single school installations to multi-tenant SaaS platforms.

## 📋 Table of Contents

1. [System Requirements](#system-requirements)
2. [Environment Setup](#environment-setup)
3. [Database Configuration](#database-configuration)
4. [Backend Deployment](#backend-deployment)
5. [Frontend Deployment](#frontend-deployment)
6. [External Service Integration](#external-service-integration)
7. [Security Configuration](#security-configuration)
8. [Multi-Tenant Setup](#multi-tenant-setup)
9. [Monitoring & Logging](#monitoring--logging)
10. [Backup & Recovery](#backup--recovery)
11. [Scaling & Performance](#scaling--performance)
12. [Troubleshooting](#troubleshooting)

## 📊 System Requirements

### Minimum Requirements (Single School)
- **CPU**: 2 cores, 2.4 GHz
- **RAM**: 4 GB
- **Storage**: 50 GB SSD
- **OS**: Ubuntu 20.04+ / CentOS 8+ / Windows Server 2019+
- **Database**: PostgreSQL 12+ or MySQL 8+

### Recommended Requirements (Multi-School SaaS)
- **CPU**: 8 cores, 3.0 GHz
- **RAM**: 16 GB
- **Storage**: 500 GB SSD
- **Load Balancer**: Nginx or Apache
- **CDN**: CloudFront, CloudFlare, or similar
- **Database**: PostgreSQL 13+ with read replicas

### Cloud Provider Options
- **AWS**: EC2, RDS, S3, CloudFront
- **Azure**: VMs, Azure Database, Blob Storage, CDN
- **Google Cloud**: Compute Engine, Cloud SQL, Cloud Storage
- **DigitalOcean**: Droplets, Managed Databases, Spaces

## 🔧 Environment Setup

### 1. Server Preparation

#### Ubuntu/Debian
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.9+
sudo apt install python3.9 python3.9-venv python3.9-dev python3-pip -y

# Install Node.js 18+
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install nodejs -y

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Install Nginx
sudo apt install nginx -y

# Install Redis (for caching and background tasks)
sudo apt install redis-server -y

# Install SSL certificates
sudo apt install certbot python3-certbot-nginx -y
```

#### CentOS/RHEL
```bash
# Update system
sudo yum update -y

# Install Python 3.9+
sudo yum install python39 python39-devel python39-pip -y

# Install Node.js
curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
sudo yum install nodejs -y

# Install PostgreSQL
sudo yum install postgresql postgresql-server postgresql-contrib -y
sudo postgresql-setup initdb
sudo systemctl enable postgresql
sudo systemctl start postgresql

# Install Nginx
sudo yum install nginx -y

# Install Redis
sudo yum install redis -y
sudo systemctl enable redis
sudo systemctl start redis
```

### 2. Python Environment Setup

```bash
# Create application user
sudo useradd -m -s /bin/bash edumanage
sudo usermod -aG sudo edumanage

# Switch to application user
sudo su - edumanage

# Create application directory
mkdir -p /home/edumanage/app
cd /home/edumanage/app

# Clone the repository (if using git)
git clone <your-repository-url> .

# Create virtual environment
python3.9 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r backend/requirements.txt
```

## 🗄️ Database Configuration

### PostgreSQL Setup

#### 1. Create Database and User
```bash
sudo -u postgres psql

-- Create database
CREATE DATABASE edumanage_prod;

-- Create user
CREATE USER edumanage_user WITH PASSWORD 'your_secure_password_here';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE edumanage_prod TO edumanage_user;
ALTER USER edumanage_user CREATEDB;

-- Exit PostgreSQL
\q
```

#### 2. Configure Connection Settings
```bash
# Edit PostgreSQL configuration
sudo nano /etc/postgresql/13/main/postgresql.conf

# Update these settings:
listen_addresses = 'localhost'
max_connections = 100
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
maintenance_work_mem = 64MB

# Edit authentication
sudo nano /etc/postgresql/13/main/pg_hba.conf

# Add line for local connections:
local   edumanage_prod   edumanage_user   md5

# Restart PostgreSQL
sudo systemctl restart postgresql
```

#### 3. Environment Configuration
```bash
# Create production environment file
cd /home/edumanage/app/backend
cp .env.example .env.production

# Edit environment variables
nano .env.production
```

```env
# Production Environment Configuration
FLASK_ENV=production
SECRET_KEY=your_super_secret_key_here_make_it_long_and_random
JWT_SECRET_KEY=another_super_secret_key_for_jwt_tokens

# Database Configuration
SQLALCHEMY_DATABASE_URI=postgresql://edumanage_user:your_secure_password_here@localhost/edumanage_prod

# Multi-Tenant Configuration
MULTI_TENANT_MODE=true
DEFAULT_SCHOOL_DOMAIN=demo.edumanage.com

# SMS Configuration (Africa's Talking)
AFRICASTALKING_USERNAME=your_username
AFRICASTALKING_API_KEY=your_api_key

# SMS Configuration (Twilio - Alternative)
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=your_twilio_number

# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
MAIL_DEFAULT_SENDER=noreply@yourdomain.com

# WhatsApp Configuration
WHATSAPP_API_URL=https://api.whatsapp.com/send
WHATSAPP_TOKEN=your_whatsapp_token

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# File Upload Configuration
UPLOAD_FOLDER=/home/edumanage/app/uploads
MAX_CONTENT_LENGTH=16777216

# Security Configuration
WTF_CSRF_ENABLED=true
PERMANENT_SESSION_LIFETIME=3600

# Feature Flags
ENABLE_SMS_NOTIFICATIONS=true
ENABLE_EMAIL_NOTIFICATIONS=true
ENABLE_WHATSAPP_NOTIFICATIONS=false
ENABLE_BIOMETRIC_ATTENDANCE=false
ENABLE_QR_ATTENDANCE=true

# Backup Configuration
BACKUP_ENABLED=true
BACKUP_SCHEDULE=daily
BACKUP_RETENTION_DAYS=30
```

## 🖥️ Backend Deployment

### 1. Database Migration
```bash
cd /home/edumanage/app/backend
source venv/bin/activate

# Initialize database
python -c "from app import create_app, db; app = create_app('production'); app.app_context().push(); db.create_all()"

# Run seed data (if needed)
python seed.py
```

### 2. Gunicorn Configuration
```bash
# Install Gunicorn
pip install gunicorn

# Create Gunicorn configuration
nano /home/edumanage/app/backend/gunicorn.conf.py
```

```python
# Gunicorn configuration file
bind = "127.0.0.1:5000"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True
user = "edumanage"
group = "edumanage"
tmp_upload_dir = None
errorlog = "/home/edumanage/app/logs/gunicorn_error.log"
accesslog = "/home/edumanage/app/logs/gunicorn_access.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
```

### 3. Systemd Service
```bash
# Create systemd service file
sudo nano /etc/systemd/system/edumanage.service
```

```ini
[Unit]
Description=EduManage Ultimate School Management System
After=network.target postgresql.service redis.service

[Service]
Type=notify
User=edumanage
Group=edumanage
WorkingDirectory=/home/edumanage/app/backend
Environment="PATH=/home/edumanage/app/backend/venv/bin"
Environment="FLASK_ENV=production"
ExecStart=/home/edumanage/app/backend/venv/bin/gunicorn --config gunicorn.conf.py run:app
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=10
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=edumanage

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable edumanage
sudo systemctl start edumanage
sudo systemctl status edumanage
```

### 4. Celery Background Tasks
```bash
# Create Celery service
sudo nano /etc/systemd/system/edumanage-celery.service
```

```ini
[Unit]
Description=EduManage Celery Worker
After=network.target redis.service

[Service]
Type=forking
User=edumanage
Group=edumanage
WorkingDirectory=/home/edumanage/app/backend
Environment="PATH=/home/edumanage/app/backend/venv/bin"
ExecStart=/home/edumanage/app/backend/venv/bin/celery -A app.celery worker --detach --loglevel=info
ExecStop=/bin/kill -s TERM $MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start Celery
sudo systemctl daemon-reload
sudo systemctl enable edumanage-celery
sudo systemctl start edumanage-celery
```

## 🌐 Frontend Deployment

### 1. Build Production Frontend
```bash
cd /home/edumanage/app/frontend

# Install dependencies
npm install

# Build for production
npm run build

# The build files will be in the 'dist' directory
```

### 2. Nginx Configuration
```bash
# Create Nginx configuration
sudo nano /etc/nginx/sites-available/edumanage
```

```nginx
# EduManage Ultimate Nginx Configuration

upstream edumanage_backend {
    server 127.0.0.1:5000;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    ssl_stapling on;
    ssl_stapling_verify on;

    # Security Headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Frontend (React)
    location / {
        root /home/edumanage/app/frontend/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
        
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # Backend API
    location /api/ {
        proxy_pass http://edumanage_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Health check
    location /health {
        proxy_pass http://edumanage_backend;
        access_log off;
    }

    # File uploads
    location /uploads/ {
        alias /home/edumanage/app/uploads/;
        expires 1y;
        add_header Cache-Control "public";
    }

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;

    # Client max body size for file uploads
    client_max_body_size 50M;
}

# Multi-tenant subdomain support
server {
    listen 443 ssl http2;
    server_name *.yourdomain.com;

    # SSL Configuration (wildcard certificate)
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # Same configuration as above but for subdomains
    location / {
        root /home/edumanage/app/frontend/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://edumanage_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable site and test configuration
sudo ln -s /etc/nginx/sites-available/edumanage /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 3. SSL Certificate Setup
```bash
# Get SSL certificate using Let's Encrypt
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# For wildcard certificate (for multi-tenant)
sudo certbot certonly --manual --preferred-challenges=dns -d yourdomain.com -d *.yourdomain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 🔗 External Service Integration

### 1. SMS Configuration

#### Africa's Talking Setup
1. Sign up at [africastalking.com](https://africastalking.com)
2. Get API key and username
3. Add credits to your account
4. Update environment variables

#### Twilio Setup (Alternative)
1. Sign up at [twilio.com](https://twilio.com)
2. Get Account SID and Auth Token
3. Purchase a phone number
4. Update environment variables

### 2. Email Configuration

#### Gmail Setup
1. Enable 2-factor authentication
2. Generate App Password
3. Update environment variables

#### SendGrid Setup (Recommended for production)
1. Sign up at [sendgrid.com](https://sendgrid.com)
2. Get API key
3. Configure DNS records
4. Update environment variables

### 3. Cloud Storage (Optional)

#### AWS S3 Setup
```bash
pip install boto3

# Add to environment variables
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_S3_BUCKET=your_bucket_name
AWS_S3_REGION=us-east-1
```

## 🔐 Security Configuration

### 1. Firewall Setup
```bash
# Install UFW (Ubuntu)
sudo ufw enable

# Allow necessary ports
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS

# Block all other ports
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Check status
sudo ufw status
```

### 2. Fail2Ban Setup
```bash
# Install Fail2Ban
sudo apt install fail2ban -y

# Configure Fail2Ban
sudo nano /etc/fail2ban/jail.local
```

```ini
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true

[nginx-http-auth]
enabled = true

[nginx-noscript]
enabled = true

[nginx-badbots]
enabled = true
```

```bash
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 3. Database Security
```bash
# Secure PostgreSQL installation
sudo nano /etc/postgresql/13/main/postgresql.conf

# Update settings:
ssl = on
password_encryption = scram-sha-256
log_statement = 'all'
log_min_duration_statement = 1000

# Restart PostgreSQL
sudo systemctl restart postgresql
```

## 🏢 Multi-Tenant Setup

### 1. Domain Configuration
```bash
# Add subdomains to DNS
# school1.yourdomain.com -> your_server_ip
# school2.yourdomain.com -> your_server_ip
# *.yourdomain.com -> your_server_ip (wildcard)
```

### 2. School Registration Script
```python
# scripts/add_school.py
from app import create_app, db
from app.models import School, User
from werkzeug.security import generate_password_hash

def add_school(name, code, domain, admin_email, admin_password):
    app = create_app('production')
    with app.app_context():
        # Create school
        school = School(
            name=name,
            code=code,
            domain=domain,
            subdomain=domain.split('.')[0]
        )
        db.session.add(school)
        db.session.flush()
        
        # Create admin user
        admin = User(
            username=admin_email,
            email=admin_email,
            password_hash=generate_password_hash(admin_password),
            role='admin',
            school_id=school.id,
            is_verified=True
        )
        db.session.add(admin)
        db.session.commit()
        
        print(f"School '{name}' created successfully!")
        print(f"Admin login: {admin_email}")
        print(f"Domain: {domain}")

if __name__ == "__main__":
    add_school("Demo School", "DEMO", "demo.yourdomain.com", "admin@demo.com", "admin123")
```

## 📊 Monitoring & Logging

### 1. Log Configuration
```bash
# Create log directories
sudo mkdir -p /var/log/edumanage
sudo chown edumanage:edumanage /var/log/edumanage

# Configure log rotation
sudo nano /etc/logrotate.d/edumanage
```

```
/var/log/edumanage/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 edumanage edumanage
    postrotate
        systemctl reload edumanage
    endscript
}
```

### 2. System Monitoring
```bash
# Install monitoring tools
sudo apt install htop iotop nethogs -y

# Install New Relic (optional)
# Follow instructions at newrelic.com

# Basic monitoring script
nano /home/edumanage/monitor.sh
```

```bash
#!/bin/bash
# Basic system monitoring

LOG_FILE="/var/log/edumanage/system_monitor.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

# Check disk space
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "$DATE: WARNING - Disk usage is ${DISK_USAGE}%" >> $LOG_FILE
fi

# Check memory usage
MEMORY_USAGE=$(free | grep Mem | awk '{printf("%.2f", $3/$2 * 100.0)}')
if (( $(echo "$MEMORY_USAGE > 80" | bc -l) )); then
    echo "$DATE: WARNING - Memory usage is ${MEMORY_USAGE}%" >> $LOG_FILE
fi

# Check if services are running
if ! systemctl is-active --quiet edumanage; then
    echo "$DATE: ERROR - EduManage service is down" >> $LOG_FILE
fi

if ! systemctl is-active --quiet postgresql; then
    echo "$DATE: ERROR - PostgreSQL service is down" >> $LOG_FILE
fi
```

```bash
# Make executable and add to cron
chmod +x /home/edumanage/monitor.sh
(crontab -l 2>/dev/null; echo "*/5 * * * * /home/edumanage/monitor.sh") | crontab -
```

## 💾 Backup & Recovery

### 1. Database Backup Script
```bash
nano /home/edumanage/backup_db.sh
```

```bash
#!/bin/bash
# Database backup script

BACKUP_DIR="/home/edumanage/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="edumanage_prod"
DB_USER="edumanage_user"

# Create backup directory
mkdir -p $BACKUP_DIR

# Create database backup
pg_dump -U $DB_USER -h localhost $DB_NAME | gzip > $BACKUP_DIR/db_backup_$DATE.sql.gz

# Keep only last 30 days of backups
find $BACKUP_DIR -name "db_backup_*.sql.gz" -mtime +30 -delete

echo "Database backup completed: db_backup_$DATE.sql.gz"
```

### 2. Full System Backup
```bash
nano /home/edumanage/backup_full.sh
```

```bash
#!/bin/bash
# Full system backup script

BACKUP_DIR="/home/edumanage/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup application files
tar -czf $BACKUP_DIR/app_backup_$DATE.tar.gz \
    --exclude='*.pyc' \
    --exclude='__pycache__' \
    --exclude='node_modules' \
    --exclude='*.log' \
    /home/edumanage/app

# Backup uploads
tar -czf $BACKUP_DIR/uploads_backup_$DATE.tar.gz /home/edumanage/app/uploads

# Backup database
/home/edumanage/backup_db.sh

# Upload to cloud storage (optional)
# aws s3 cp $BACKUP_DIR/ s3://your-backup-bucket/ --recursive

echo "Full backup completed: $DATE"
```

```bash
# Make executable and schedule
chmod +x /home/edumanage/backup_*.sh

# Add to cron for daily backups
(crontab -l 2>/dev/null; echo "0 2 * * * /home/edumanage/backup_full.sh") | crontab -
```

## ⚡ Scaling & Performance

### 1. Database Optimization
```sql
-- PostgreSQL performance tuning
-- Add indexes for frequently queried columns

-- Students table
CREATE INDEX idx_students_school_class ON students(school_id, class_id);
CREATE INDEX idx_students_user_id ON students(user_id);

-- Attendance table
CREATE INDEX idx_attendance_student_date ON attendance(student_id, date);
CREATE INDEX idx_attendance_school_date ON attendance(school_id, date);

-- Grades table
CREATE INDEX idx_grades_student_subject ON grades(student_id, subject_id);

-- Fees table
CREATE INDEX idx_fees_student_status ON fees(student_id, status);
```

### 2. Redis Caching Setup
```python
# Add to backend configuration
REDIS_URL = "redis://localhost:6379/0"
CACHE_TYPE = "redis"
CACHE_REDIS_URL = REDIS_URL
CACHE_DEFAULT_TIMEOUT = 300
```

### 3. Load Balancer Configuration (Multiple Servers)
```nginx
# /etc/nginx/nginx.conf
upstream edumanage_cluster {
    server 192.168.1.10:5000 weight=3;
    server 192.168.1.11:5000 weight=2;
    server 192.168.1.12:5000 weight=1;
}

server {
    listen 443 ssl;
    server_name yourdomain.com;
    
    location /api/ {
        proxy_pass http://edumanage_cluster;
        # ... other proxy settings
    }
}
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Service Won't Start
```bash
# Check service status
sudo systemctl status edumanage

# Check logs
sudo journalctl -u edumanage -f

# Check application logs
tail -f /home/edumanage/app/logs/gunicorn_error.log
```

#### 2. Database Connection Issues
```bash
# Test database connection
sudo -u edumanage psql -h localhost -U edumanage_user -d edumanage_prod

# Check PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-13-main.log
```

#### 3. Permission Issues
```bash
# Fix file permissions
sudo chown -R edumanage:edumanage /home/edumanage/app
sudo chmod -R 755 /home/edumanage/app
sudo chmod -R 777 /home/edumanage/app/uploads
```

#### 4. SSL Certificate Issues
```bash
# Check certificate validity
sudo certbot certificates

# Renew certificate
sudo certbot renew --dry-run
```

### Performance Issues

#### 1. High CPU Usage
- Check for inefficient database queries
- Implement query optimization
- Add database indexes
- Scale horizontally

#### 2. High Memory Usage
- Monitor application memory usage
- Optimize Python memory usage
- Consider adding more RAM
- Implement Redis caching

#### 3. Slow Loading Times
- Enable Gzip compression
- Optimize frontend bundle size
- Use CDN for static assets
- Implement database query caching

### Database Maintenance

#### 1. Regular Maintenance
```bash
# PostgreSQL maintenance
sudo -u postgres psql edumanage_prod

-- Update table statistics
ANALYZE;

-- Reclaim storage space
VACUUM;

-- Full vacuum (during maintenance window)
VACUUM FULL;
```

#### 2. Database Monitoring
```sql
-- Check database size
SELECT pg_size_pretty(pg_database_size('edumanage_prod'));

-- Check table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Check slow queries
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;
```

## 📞 Support & Maintenance

### Regular Maintenance Tasks

#### Daily
- [ ] Check system health
- [ ] Verify backups completed
- [ ] Monitor error logs
- [ ] Check disk space

#### Weekly  
- [ ] Update system packages
- [ ] Review performance metrics
- [ ] Check SSL certificate status
- [ ] Verify external service integrations

#### Monthly
- [ ] Update application dependencies
- [ ] Review and rotate logs
- [ ] Perform security audit
- [ ] Test backup restoration

#### Quarterly
- [ ] Performance optimization review
- [ ] Security vulnerability assessment
- [ ] Capacity planning review
- [ ] Disaster recovery testing

### Getting Help

1. **Documentation**: Check this guide and README files
2. **Logs**: Always check application and system logs first
3. **Community**: Join our community forums
4. **Support**: Contact technical support for critical issues

---

## 🎉 Congratulations!

You have successfully deployed EduManage Ultimate School Management System! 

Your system is now ready to serve schools across Kenya and beyond. The platform provides:

- ✅ Complete multi-role authentication
- ✅ Comprehensive student management
- ✅ Advanced attendance tracking with QR codes
- ✅ Robust examination and grading system
- ✅ Integrated fee management
- ✅ Parent portal with real-time updates
- ✅ Multi-channel notifications (SMS, Email, WhatsApp)
- ✅ Library management system
- ✅ Event and calendar management
- ✅ Detailed reporting and analytics
- ✅ Multi-tenant support for SaaS deployment

### Next Steps

1. **Customize branding** for your target schools
2. **Set up monitoring** and alerting
3. **Train your support team** on the system
4. **Start onboarding schools** to your platform
5. **Collect feedback** and iterate on features

### Support

For technical support or feature requests, please contact our team or refer to the comprehensive documentation provided.

**Happy School Management! 🎓📚**