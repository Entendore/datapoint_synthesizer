#!/usr/bin/env python3
"""
Datapoint Synthesizer - Complete Project
Main entry point for GUI, CLI, and API modes
"""

import sys
import argparse
import json
from pathlib import Path


def run_gui():
    """Launches the GUI application."""
    from PySide6.QtWidgets import QApplication
    from gui.main_window import SynthesizerMainWindow
    from gui.theme_manager import ThemeManager
    
    app = QApplication(sys.argv)
    app.setApplicationName("Datapoint Synthesizer")
    app.setApplicationVersion("3.0.0")
    
    ThemeManager.apply_theme(app, "dark")
    
    window = SynthesizerMainWindow()
    window.show()
    
    sys.exit(app.exec())


def run_cli(args):
    """Runs CLI mode."""
    from core.synthesizer import DatapointSynthesizerV3
    from core.strategies import Strategy
    
    synthesizer = DatapointSynthesizerV3(strategy=Strategy[args.strategy.upper()])
    
    examples = []
    if args.examples:
        with open(args.examples, 'r') as f:
            if args.examples.endswith('.jsonl'):
                examples = [json.loads(line) for line in f if line.strip()]
            else:
                examples = json.load(f)
                if isinstance(examples, dict):
                    examples = [examples]
    
    if not examples:
        print("❌ No examples provided. Use --examples <file>")
        return
    
    synthesizer.set_examples(examples)
    
    print(f"🔄 Generating {args.count} datapoints...")
    generated = synthesizer.synthesize(
        n=args.count,
        ensure_novelty=not args.no_novelty,
        validate=not args.no_validate,
        add_explanations=args.explanations
    )
    
    output_path = args.output or "synthesized_data"
    
    if args.format == "jsonl":
        with open(f"{output_path}.jsonl", 'w', encoding='utf-8') as f:
            for dp in generated:
                f.write(json.dumps(dp, ensure_ascii=False) + '\n')
    elif args.format == "json":
        with open(f"{output_path}.json", 'w', encoding='utf-8') as f:
            json.dump(generated, f, indent=2, ensure_ascii=False)
    elif args.format == "csv":
        import pandas as pd
        df = pd.json_normalize(generated)
        df.to_csv(f"{output_path}.csv", index=False)
    
    print(f"✅ Generated {len(generated)} datapoints → {output_path}.{args.format}")


def run_api(args):
    """Runs the REST API server."""
    from export.api_server import start_server
    start_server(host=args.host, port=args.port)


def main():
    parser = argparse.ArgumentParser(
        description="🧬 Datapoint Synthesizer - Complete Project",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --mode gui
  %(prog)s --mode cli --examples data.json --count 100 --output output
  %(prog)s --mode api --port 8000
        """
    )
    
    parser.add_argument("--mode", choices=["gui", "cli", "api"], default="gui",
                       help="Run mode: gui, cli, or api")
    
    # CLI options
    parser.add_argument("--examples", help="Path to example JSON/JSONL file")
    parser.add_argument("--count", type=int, default=10, help="Number of datapoints")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--format", choices=["jsonl", "json", "csv"], default="jsonl")
    parser.add_argument("--strategy", default="balanced",
                       choices=["conservative", "balanced", "creative", "adversarial"])
    parser.add_argument("--no-novelty", action="store_true", help="Disable novelty detection")
    parser.add_argument("--no-validate", action="store_true", help="Disable validation")
    parser.add_argument("--explanations", action="store_true", help="Add explanations")
    
    # API options
    parser.add_argument("--host", default="0.0.0.0", help="API host")
    parser.add_argument("--port", type=int, default=8000, help="API port")
    
    args = parser.parse_args()
    
    if args.mode == "gui":
        run_gui()
    elif args.mode == "cli":
        run_cli(args)
    elif args.mode == "api":
        run_api(args)


if __name__ == "__main__":
    main()
