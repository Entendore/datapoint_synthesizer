"""
File export module
"""

import json
from typing import Dict, List


class FileExporter:
    """Exports datapoints to various file formats."""
    
    def export_jsonl(self, datapoints: List[Dict], path: str):
        with open(path, 'w', encoding='utf-8') as f:
            for dp in datapoints:
                f.write(json.dumps(dp, ensure_ascii=False) + '\n')
    
    def export_json(self, datapoints: List[Dict], path: str):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(datapoints, f, indent=2, ensure_ascii=False)
    
    def export_csv(self, datapoints: List[Dict], path: str):
        import pandas as pd
        df = pd.json_normalize(datapoints)
        df.to_csv(path, index=False)
    
    def export_parquet(self, datapoints: List[Dict], path: str):
        import pandas as pd
        df = pd.json_normalize(datapoints)
        df.to_parquet(path)
