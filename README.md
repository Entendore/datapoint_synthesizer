# 🧬 Datapoint Synthesizer - Complete Project

A comprehensive, production-grade data synthesis platform for generating high-quality training data for neural networks.

## ✨ Features

### Core Synthesis
- **Structure-aware synthesis** - Learns patterns from examples
- **Multi-example learning** - Analyzes multiple examples for better patterns
- **Rule mining** - Auto-discovers implicit constraints
- **Novelty detection** - Prevents duplicate generation via embeddings
- **Semantic coherence** - Ensures generated data makes sense
- **Constraint system** - User-defined field relationships
- **Generation strategies** - Conservative, balanced, creative, adversarial

### Data Formats
- **RL**: SARS tuples, trajectories, DPO, KTO, ORPO, SimPO, Decision Transformer
- **NLP**: Classification, NER (BIO), summarization, sentiment, paraphrases
- **QA**: Multiple choice, true/false, wh-questions, multi-hop
- **CV**: Image classification, object detection, segmentation
- **Math**: Set theory, group theory, category theory structures

### Analysis
- **Data profiling** - Comprehensive statistical summaries
- **Statistical testing** - T-tests, Mann-Whitney, KS, normality, correlations
- **Bias detection** - Demographic parity, representation analysis
- **Benchmarking** - Quality metrics, A/B testing, baseline comparison

### Augmentation
- **Text augmentation** - Synonym replacement, back-translation, paraphrase
- **Image augmentation** - Geometric transforms, noise injection
- **Multi-modal** - Image, audio, video datapoint generation

### Export
- **Files**: JSONL, JSON, CSV, Parquet
- **Databases**: SQLite, MongoDB
- **ML Frameworks**: PyTorch Dataset, Hugging Face Dataset
- **API**: REST API via FastAPI

### Validation
- **JSON Schema** validation
- **Pydantic** model validation
- **Quality validation** with custom rules

### UI/UX
- **Professional GUI** with dark/light themes
- **Live preview** of generated data
- **Session management** - Save/load, undo/redo, auto-save
- **Template library** - Reusable data templates
- **Plugin system** - Extensible architecture
- **Keyboard shortcuts** - Ctrl+G, Ctrl+S, etc.

## 🚀 Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/datapoint-synthesizer.git
cd datapoint-synthesizer

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm
```

## 🎯 Usage

### GUI Mode
```bash
python main.py --mode gui
```

### CLI Mode
```bash
python main.py --mode cli --examples data.json --count 100 --output output --format jsonl
```

### API Mode
```bash
python main.py --mode api --port 8000
```

Then access the API at `http://localhost:8000/docs`

### Python API
```python
from core.synthesizer import DatapointSynthesizerV3
from core.strategies import Strategy

# Initialize
synth = DatapointSynthesizerV3(strategy=Strategy.BALANCED)

# Set examples
examples = [
    {"question": "What is the capital of France?", "answer": "Paris", "difficulty": "easy"},
    {"question": "What is the capital of Japan?", "answer": "Tokyo", "difficulty": "medium"},
]
synth.set_examples(examples)

# Generate
generated = synth.synthesize(n=100, ensure_novelty=True, add_explanations=True)

# Export
import json
with open("output.jsonl", "w") as f:
    for dp in generated:
        f.write(json.dumps(dp) + "\n")
```

## 📊 Example Output

**Input:**
```json
{"question": "What is the capital of France?", "answer": "Paris", "difficulty": "easy"}
```

**Generated:**
```json
{
  "question": "What is the capital of Japan?",
  "answer": "Tokyo",
  "difficulty": "medium",
  "explanation": "The answer to 'What is the capital of Japan?' is 'Tokyo'.",
  "_synthesis_id": "syn_0001",
  "_strategy": "balanced",
  "_novelty_similarity": 0.42
}
```

## 🏗️ Architecture

```
datapoint_synthesizer/
├── core/              # Core synthesis engine
├── formats/           # Data format generators
├── analysis/          # Analysis tools
├── augmentation/      # Data augmentation
├── export/            # Export system
├── validation/        # Validation system
├── plugins/           # Plugin system
├── gui/               # GUI system
└── templates/         # Template library
```

## 🧪 Testing

```bash
pytest tests/
```

## 📝 License

MIT License

## 🤝 Contributing

Contributions welcome! Please read CONTRIBUTING.md for details.
