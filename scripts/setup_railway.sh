#!/bin/bash
# Quick setup script for Railway deployment
# This script helps prepare your project for Railway

echo "=== IgnisBot Railway Setup ==="
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  WARNING: .env file not found!"
    echo "Please create a .env file with all required variables."
    echo ""
fi

# Check if Dockerfile exists
if [ ! -f "Dockerfile" ]; then
    echo "❌ ERROR: Dockerfile not found!"
    exit 1
fi

# Check if railway.json exists
if [ ! -f "railway.json" ]; then
    echo "⚠️  WARNING: railway.json not found!"
    echo "Creating default railway.json..."
    cat > railway.json << EOF
{
  "\$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile"
  },
  "deploy": {
    "startCommand": "python ignis_main.py",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
EOF
    echo "✅ Created railway.json"
fi

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Push your code to GitHub"
echo "2. Go to https://railway.app"
echo "3. Create a new project"
echo "4. Connect your GitHub repository"
echo "5. Add all environment variables from your .env file"
echo "6. Railway will automatically deploy!"
echo ""

