#!/bin/bash

echo "🔧 Setting up Datapoint Synthesizer..."

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Create necessary directories
mkdir -p datasets sessions plugins/custom

echo "✅ Setup complete!"
echo ""
echo "To activate the virtual environment:"
echo "  source venv/bin/activate"
echo ""
echo "To run the GUI:"
echo "  python main.py --mode gui"
echo ""
echo "To run the CLI:"
echo "  python main.py --mode cli --examples templates/builtin_templates.json"
echo ""
echo "To run the API:"
echo "  python main.py --mode api --port 8000"
