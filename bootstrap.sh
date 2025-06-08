
#!/bin/bash

# Ansible Bootstrap Script

set -euo pipefail

# Configuration
REPO_URL="${REPO_URL:-https://github.com/dhanvsagar/feedback-app.git}"
SETUP_DIR="$HOME/server-setup"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date '+%H:%M:%S')]${NC} $*"
}

error() {
    echo -e "${RED}[ERROR]${NC} $*"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
    error "Don't run as root. Use a user with sudo privileges."
    exit 1
fi

# Install Ansible if not present
if ! command -v ansible &> /dev/null; then
    log "Installing Ansible..."
    sudo apt update
    sudo apt install -y git curl
    
    if sudo apt install -y ansible 2>/dev/null; then
        log "Ansible installed via apt"
    fi
    
    # Verify installation
    if ! command -v ansible &> /dev/null; then
        # Try to fix PATH for pipx
        export PATH="$HOME/.local/bin:$PATH"
        if ! command -v ansible &> /dev/null; then
            error "Ansible installation verification failed"
            exit 1
        fi
    fi
fi

log "Ansible version: $(ansible --version | head -1)"

# Clone or update repository
log "Getting setup files from: $REPO_URL"
if [[ -d "$SETUP_DIR" ]]; then
    cd "$SETUP_DIR" && git pull
else
    git clone "$REPO_URL" "$SETUP_DIR"
    cd "$SETUP_DIR"
fi

cd ansible

# Install Ansible requirements if file exists
if [[ -f "requirements.yml" ]]; then
    log "Installing Ansible requirements..."
    ansible-galaxy install -r requirements.yml
fi


# Run the playbook
log "Running server setup..."
ansible-playbook -i inventory/hosts.yml site.yml --ask-become-pass "$@"

log "Setup completed! Files are in: $SETUP_DIR"