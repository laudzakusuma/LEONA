"""
Production deployment script for LEONA
"""

PRODUCTION_DEPLOY_SCRIPT = """#!/bin/bash

# LEONA Production Deployment Script
# This script sets up LEONA for production use

set -e

echo "╔════════════════════════════════════════════╗"
echo "║    LEONA Production Deployment Script      ║"
echo "╚════════════════════════════════════════════╝"

# Configuration
DEPLOY_USER=${DEPLOY_USER:-leona}
DEPLOY_DIR=${DEPLOY_DIR:-/opt/leona}
SERVICE_NAME=${SERVICE_NAME:-leona}
DOMAIN=${DOMAIN:-leona.local}

# Colors for output
RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
NC='\\033[0m' # No Color

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   log_error "This script must be run as root"
   exit 1
fi

# 1. System preparation
log_info "Preparing system..."

# Update system
apt-get update
apt-get upgrade -y

# Install dependencies
apt-get install -y \\
    python3.10 python3.10-venv python3-pip \\
    nginx certbot python3-certbot-nginx \\
    supervisor \\
    postgresql postgresql-contrib \\
    redis-server \\
    ffmpeg \\
    build-essential \\
    git \\
    ufw

# 2. Create deployment user
log_info "Creating deployment user..."

if ! id "$DEPLOY_USER" &>/dev/null; then
    useradd -m -s /bin/bash $DEPLOY_USER
    usermod -aG sudo $DEPLOY_USER
fi

# 3. Setup directory structure
log_info "Setting up directory structure..."

mkdir -p $DEPLOY_DIR
mkdir -p $DEPLOY_DIR/logs
mkdir -p $DEPLOY_DIR/data
mkdir -p $DEPLOY_DIR/backups

# Clone or update repository
if [ -d "$DEPLOY_DIR/.git" ]; then
    cd $DEPLOY_DIR
    git pull
else
    git clone https://github.com/yourusername/leona.git $DEPLOY_DIR
fi

chown -R $DEPLOY_USER:$DEPLOY_USER $DEPLOY_DIR

# 4. Setup Python environment
log_info "Setting up Python environment..."

cd $DEPLOY_DIR
sudo -u $DEPLOY_USER python3.10 -m venv venv
sudo -u $DEPLOY_USER ./venv/bin/pip install --upgrade pip
sudo -u $DEPLOY_USER ./venv/bin/pip install -r requirements.txt

# 5. Setup database
log_info "Setting up PostgreSQL database..."

# Create database and user
sudo -u postgres psql <<EOF
CREATE USER leona WITH PASSWORD 'secure_password_here';
CREATE DATABASE leona_db OWNER leona;
GRANT ALL PRIVILEGES ON DATABASE leona_db TO leona;
EOF

# 6. Configure environment
log_info "Configuring environment..."

cat > $DEPLOY_DIR/.env <<EOF
# Production Environment Variables
LEONA_ENV=production
LEONA_HOST=0.0.0.0
LEONA_PORT=8000
DATABASE_URL=postgresql://leona:secure_password_here@localhost/leona_db
REDIS_URL=redis://localhost:6379
SECRET_KEY=$(openssl rand -hex 32)
MODEL_PATH=$DEPLOY_DIR/data/models/model.gguf
LOG_LEVEL=INFO
WORKERS=4
EOF

chown $DEPLOY_USER:$DEPLOY_USER $DEPLOY_DIR/.env
chmod 600 $DEPLOY_DIR/.env

# 7. Download models
log_info "Downloading AI models..."
sudo -u $DEPLOY_USER $DEPLOY_DIR/venv/bin/python $DEPLOY_DIR/scripts/download_models.py --auto

# 8. Setup Nginx
log_info "Configuring Nginx..."

cat > /etc/nginx/sites-available/leona <<EOF
upstream leona_backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name $DOMAIN;
    
    # Redirect to HTTPS
    return 301 https://\\$server_name\\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name $DOMAIN;
    
    # SSL configuration (will be managed by certbot)
    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    
    # Logging
    access_log /var/log/nginx/leona_access.log;
    error_log /var/log/nginx/leona_error.log;
    
    # WebSocket support
    location /ws/ {
        proxy_pass http://leona_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \\$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \\$host;
        proxy_set_header X-Real-IP \\$remote_addr;
        proxy_set_header X-Forwarded-For \\$proxy_add_x_forwarded_for;
        proxy_read_timeout 86400;
    }
    
    # API and static files
    location / {
        proxy_pass http://leona_backend;
        proxy_set_header Host \\$host;
        proxy_set_header X-Real-IP \\$remote_addr;
        proxy_set_header X-Forwarded-For \\$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \\$scheme;
    }
    
    # Static files
    location /static/ {
        alias $DEPLOY_DIR/frontend/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
EOF

ln -sf /etc/nginx/sites-available/leona /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx

# 9. Setup Supervisor
log_info "Configuring Supervisor..."

cat > /etc/supervisor/conf.d/leona.conf <<EOF
[program:leona]
command=$DEPLOY_DIR/venv/bin/gunicorn backend.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 127.0.0.1:8000
directory=$DEPLOY_DIR
user=$DEPLOY_USER
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=$DEPLOY_DIR/logs/leona.log
environment=PATH="$DEPLOY_DIR/venv/bin",PYTHONPATH="$DEPLOY_DIR"
EOF

supervisorctl reread
supervisorctl update
supervisorctl start leona

# 10. Setup firewall
log_info "Configuring firewall..."

ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80
ufw allow 443
ufw --force enable

# 11. Setup SSL certificate
log_info "Setting up SSL certificate..."

if [ "$DOMAIN" != "leona.local" ]; then
    certbot --nginx -d $DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN
fi

# 12. Setup monitoring
log_info "Setting up monitoring..."

# Install Prometheus
wget https://github.com/prometheus/prometheus/releases/latest/download/prometheus-*.linux-amd64.tar.gz
tar xvf prometheus-*.tar.gz
mv prometheus-*/prometheus /usr/local/bin/
mv prometheus-*/promtool /usr/local/bin/

# Create Prometheus service
cat > /etc/systemd/system/prometheus.service <<EOF
[Unit]
Description=Prometheus
After=network.target

[Service]
Type=simple
User=prometheus
Group=prometheus
ExecStart=/usr/local/bin/prometheus \\
    --config.file=/etc/prometheus/prometheus.yml \\
    --storage.tsdb.path=/var/lib/prometheus/

[Install]
WantedBy=multi-user.target
EOF

# 13. Setup backup
log_info "Setting up automated backups..."

cat > /etc/cron.d/leona-backup <<EOF
# Daily backup at 3 AM
0 3 * * * $DEPLOY_USER /usr/bin/python3 $DEPLOY_DIR/scripts/backup.py
EOF

# 14. Performance tuning
log_info "Applying performance optimizations..."

# Increase system limits
cat >> /etc/security/limits.conf <<EOF
$DEPLOY_USER soft nofile 65536
$DEPLOY_USER hard nofile 65536
$DEPLOY_USER soft nproc 32768
$DEPLOY_USER hard nproc 32768
EOF

# Optimize kernel parameters
cat >> /etc/sysctl.conf <<EOF
# Network optimizations
net.core.rmem_max = 134217728
net.core.wmem_max = 134217728
net.ipv4.tcp_rmem = 4096 87380 134217728
net.ipv4.tcp_wmem = 4096 65536 134217728
net.core.netdev_max_backlog = 5000
net.ipv4.tcp_congestion_control = bbr

# File system
fs.file-max = 2097152
EOF

sysctl -p

# 15. Health check
log_info "Running health check..."

sleep 5
if curl -f http://localhost/api/status > /dev/null 2>&1; then
    log_info "✅ LEONA is running successfully!"
else
    log_error "❌ LEONA health check failed"
    exit 1
fi

# Final message
echo ""
echo "╔════════════════════════════════════════════╗"
echo "║      ✅ LEONA Production Deployment        ║"
echo "║              Complete!                     ║"
echo "╚════════════════════════════════════════════╝"
echo ""
echo "🌐 Access LEONA at: https://$DOMAIN"
echo "📊 Monitoring at: http://$DOMAIN:9090 (Prometheus)"
echo "📝 Logs at: $DEPLOY_DIR/logs/"
echo ""
echo "⚡ Quick Commands:"
echo "  Start:   supervisorctl start leona"
echo "  Stop:    supervisorctl stop leona"
echo "  Restart: supervisorctl restart leona"
echo "  Status:  supervisorctl status leona"
echo "  Logs:    tail -f $DEPLOY_DIR/logs/leona.log"
echo ""
echo "✨ LEONA - Always One Call Away"
"""