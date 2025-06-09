#!/bin/bash

# Application Deployment Script
# Run this AFTER server provisioning is complete

set -euo pipefail

# Configuration
APP_REPO="${APP_REPO:-https://github.com/dhanvsagar/feedback-app.git}"
APP_NAME="${APP_NAME:-feedback-app}"
APP_DOMAIN="${APP_DOMAIN:-feedback.dhanvsagar.com}"
SSL_EMAIL="${SSL_EMAIL:-dhanvsagar@gmail.com}"
DEPLOY_USER="${DEPLOY_USER:-deploy}"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date '+%H:%M:%S')]${NC} $*"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $*"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $*"
}

error() {
    echo -e "${RED}[ERROR]${NC} $*"
}

APP_DIR="/home/$DEPLOY_USER/apps/$APP_NAME"
cd "$APP_DIR"

log "Starting application deployment in: $(pwd)"

#  Set up environment file
log "Step 2: Setting up environment configuration..."
if [[ -f ".env.example" && ! -f ".env" ]]; then
    cp .env.example .env
    info "Created .env file from .env.example"
    warn "Please edit .env file with your actual configuration:"
    warn "  nano .env"
    echo
    read -p "Press Enter after you've configured the .env file..."
elif [[ ! -f ".env" ]]; then
    warn "No .env.example found. Creating basic .env file..."
    cat > .env << EOF
# Database Configuration
POSTGRES_DB=feedback_db
POSTGRES_USER=feedback_user
POSTGRES_PASSWORD=change_this_password

# Application Configuration
DATABASE_URL=postgresql://feedback_user:change_this_password@postgres:5432/feedback_db

# Asana Integration (optional)
ASANA_API_TOKEN=your_asana_token_here
ASANA_PROJECT_ID=your_project_id_here
EOF
    warn "Created basic .env file. Please edit it with your actual configuration:"
    warn "  nano .env"
    echo
    read -p "Press Enter after you've configured the .env file..."
else
    info ".env file already exists"
fi

# Set up SSL if domain is not localhost
log "Step 3: SSL Certificate Setup..."
if [[ "$APP_DOMAIN" != "localhost" && "$APP_DOMAIN" != "127.0.0.1" ]]; then
    info "Setting up SSL certificate for domain: $APP_DOMAIN"
    
    # Check if certbot is installed
    if ! command -v certbot &> /dev/null; then
        info "Installing certbot..."
        sudo apt update
        sudo apt install -y certbot python3-certbot-nginx
    fi
    
    
    # Start basic services first (without nginx initially)
    info "Starting database and app services..."
    docker-compose up -d postgres fastapi
    
    # Wait for services to be ready
    sleep 10
    
    # Try to start nginx (might fail initially without SSL)
    docker-compose up -d nginx || warn "Nginx failed to start (expected without SSL certificates)"

    # Generate SSL certificate
    info "Generating SSL certificate..."
    if sudo certbot certonly \
        --webroot \
        --webroot-path="$(pwd)/data/certbot/www" \
        --email "$SSL_EMAIL" \
        --agree-tos \
        --no-eff-email \
        -d "$APP_DOMAIN"; then
        
        info "SSL certificate generated successfully"
               
        # Restart nginx with certificates
        docker-compose restart nginx
        
        # Set up auto-renewal cron job
        info "Setting up SSL certificate auto-renewal..."
        (crontab -l 2>/dev/null || true; \
            echo "0 3 * * * certbot renew --quiet && cd $APP_DIR && docker-compose restart nginx") | crontab -
        
    else
        error "SSL certificate generation failed"
        warn "Continuing with HTTP only..."
    fi
else
    info "Skipping SSL setup for localhost/development"
fi

# Step 4: Deploy the application
log "Step 4: Deploying application with Docker Compose..."
info "Building and starting all services..."

# Build and start all services
docker-compose up -d --build

# Wait a moment for services to start
sleep 5

# Check service status
log "Checking service status..."
docker-compose ps

# Step 5: Verify deployment
log "Step 5: Verifying deployment..."

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    info "Services are running"
else
    error "Some services failed to start"
    docker-compose logs
    exit 1
fi


log "Deployment script completed successfully!"