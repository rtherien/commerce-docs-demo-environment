#!/bin/bash

# Setup script for Coveo Commerce API Loader
# This script sets up the development environment

set -e

echo "🚀 Setting up Coveo Commerce API Loader..."

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Create virtual environment if it doesn't exist
if [ ! -d "coveo-env" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv coveo-env
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source coveo-env/bin/activate

# Install core dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create config if it doesn't exist
if [ ! -f "config.json" ]; then
    if [ -f "config.template.json" ]; then
        echo "⚙️  Creating config.json from template..."
        cp config.template.json config.json
        echo "📝 Please edit config.json with your Coveo credentials"
    else
        echo "⚠️  No config template found. Please create config.json manually."
    fi
else
    echo "✅ Configuration file exists"
fi

# Make CLI script executable
chmod +x coveo-loader

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Edit config.json with your Coveo credentials"
echo "2. Activate the environment: source coveo-env/bin/activate"
echo "3. Run the loader: ./coveo-loader --help"
echo ""