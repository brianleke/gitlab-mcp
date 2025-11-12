#!/bin/bash
# Setup script for GitLab MCP Server

echo "Setting up GitLab MCP Server..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env file from env.example..."
    cp env.example .env
    echo ""
    echo "⚠️  Please edit .env and add your GitLab token:"
    echo "   GITLAB_TOKEN=your_personal_access_token_here"
    echo ""
    echo "Get your token from: https://gitlab.com/-/user_settings/personal_access_tokens"
else
    echo "✓ .env file already exists"
fi

echo ""
echo "Setup complete!"
echo ""
echo "To run the server:"
echo "  python server.py"
echo ""
echo "To test the connection, make sure GITLAB_TOKEN is set in .env"

