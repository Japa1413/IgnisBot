#!/bin/bash
# IgnisBot VPS Deployment Script
# This script sets up IgnisBot on a Linux VPS for 24/7 operation

set -e

echo "=== IgnisBot VPS Deployment ==="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}ERROR: Please run as root (use sudo)${NC}"
    exit 1
fi

# Get installation directory
INSTALL_DIR="/opt/ignisbot"
SERVICE_USER="ignisbot"

echo -e "${YELLOW}Installation directory: ${INSTALL_DIR}${NC}"
echo ""

# Update system
echo -e "${GREEN}[1/8] Updating system packages...${NC}"
apt-get update
apt-get install -y python3 python3-pip python3-venv git curl

# Create service user
echo -e "${GREEN}[2/8] Creating service user...${NC}"
if ! id "$SERVICE_USER" &>/dev/null; then
    useradd -r -s /bin/false -d "$INSTALL_DIR" "$SERVICE_USER"
fi

# Create installation directory
echo -e "${GREEN}[3/8] Creating installation directory...${NC}"
mkdir -p "$INSTALL_DIR"
mkdir -p "$INSTALL_DIR/logs"
chown -R "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR"

# Clone or copy bot files
echo -e "${GREEN}[4/8] Setting up bot files...${NC}"
if [ -d ".git" ]; then
    # If running from git repo, copy files
    cp -r . "$INSTALL_DIR/"
    rm -rf "$INSTALL_DIR/.git"
else
    echo -e "${YELLOW}Please ensure bot files are in the current directory${NC}"
    exit 1
fi

# Set permissions
chown -R "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR"

# Create virtual environment
echo -e "${GREEN}[5/8] Creating Python virtual environment...${NC}"
sudo -u "$SERVICE_USER" python3 -m venv "$INSTALL_DIR/venv"

# Install dependencies
echo -e "${GREEN}[6/8] Installing Python dependencies...${NC}"
sudo -u "$SERVICE_USER" "$INSTALL_DIR/venv/bin/pip" install --upgrade pip
sudo -u "$SERVICE_USER" "$INSTALL_DIR/venv/bin/pip" install -r "$INSTALL_DIR/requirements.txt"

# Create systemd service
echo -e "${GREEN}[7/8] Creating systemd service...${NC}"
cat > /etc/systemd/system/ignisbot.service << EOF
[Unit]
Description=IgnisBot Discord Bot
After=network.target

[Service]
Type=simple
User=$SERVICE_USER
WorkingDirectory=$INSTALL_DIR
Environment="PATH=$INSTALL_DIR/venv/bin"
ExecStart=$INSTALL_DIR/venv/bin/python $INSTALL_DIR/ignis_main.py
Restart=always
RestartSec=10
StandardOutput=append:$INSTALL_DIR/logs/ignisbot.log
StandardError=append:$INSTALL_DIR/logs/ignisbot.log

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
systemctl daemon-reload

# Enable service
echo -e "${GREEN}[8/8] Enabling service...${NC}"
systemctl enable ignisbot.service

echo ""
echo -e "${GREEN}=== Installation Complete ===${NC}"
echo ""
echo "Next steps:"
echo "1. Copy your .env file to $INSTALL_DIR/.env"
echo "2. Set proper permissions: chown $SERVICE_USER:$SERVICE_USER $INSTALL_DIR/.env"
echo "3. Start the service: systemctl start ignisbot"
echo "4. Check status: systemctl status ignisbot"
echo "5. View logs: journalctl -u ignisbot -f"
echo ""

