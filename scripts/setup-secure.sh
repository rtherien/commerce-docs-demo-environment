#!/bin/bash
# Secure setup script for Coveo Commerce API Loader

set -e

echo "🔐 Setting up secure Coveo Commerce API Loader environment..."

# Create Python virtual environment if it doesn't exist
if [ ! -d "coveo-env" ]; then
    echo "🐍 Creating Python virtual environment..."
    python3 -m venv coveo-env
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source coveo-env/bin/activate

# Install dependencies
echo "⬇️  Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create environment file from template
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file with your actual Coveo credentials!"
    echo "   Use: nano .env"
    echo ""
    echo "🔍 Find your credentials at:"
    echo "   https://platform.cloud.coveo.com/"
    echo "   Organization ID: Administration Console"
    echo "   Source ID: Sources section"
    echo "   Access Token: API Keys section"
else
    echo "✅ .env file already exists"
fi

# Make loader executable
chmod +x coveo-loader

echo ""
echo "✅ Setup complete!"
echo ""
echo "🔧 Next steps:"
echo "   1. Edit .env with your credentials: nano .env"
echo "   2. Activate environment: source coveo-env/bin/activate"
echo "   3. Run loader: ./coveo-loader"
echo ""
echo "🔐 Security notes:"
echo "   ✅ .env file is ignored by git"
echo "   ✅ Credentials loaded from environment variables"
echo "   ✅ No API keys stored in code"