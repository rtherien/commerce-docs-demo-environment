#!/bin/bash
# Simple setup for Coveo Commerce Data Loader

set -e

echo "🚀 Setting up Coveo Commerce Data Loader..."

# Create Python virtual environment if it doesn't exist
if [ ! -d "coveo-env" ]; then
    echo "📦 Creating Python environment..."
    python3 -m venv coveo-env
fi

# Activate virtual environment
echo "⬇️  Installing required packages..."
source coveo-env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Create environment file from template
if [ ! -f ".env" ]; then
    echo "📝 Creating settings file..."
    cp .env.example .env
    echo ""
    echo "✅ Setup complete!"
    echo ""
    echo "🔧 Next steps:"
    echo "   1. Edit .env with your Coveo info: nano .env"
    echo "   2. Get your Coveo details from: https://platform.cloud.coveo.com/"
    echo "   3. Run: source coveo-env/bin/activate"
    echo "   4. Run: ./coveo-loader"
else
    echo "✅ Setup complete! Your .env file already exists."
fi

# Make loader executable
chmod +x coveo-loader