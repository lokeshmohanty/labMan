#!/bin/bash

echo "🚀 Setting up LabMan v2 Backend..."

cd "$(dirname "$0")"

# Install dependencies
echo "📦 Installing dependencies..."
pip install tomli
uv pip install -e .

# Initialize database
echo "🗄️  Initializing database..."
python init_db.py

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start the server, run:"
echo "  uvicorn app.main:app --reload --port 8000"
echo ""
echo "Or simply run: ./run.sh"
