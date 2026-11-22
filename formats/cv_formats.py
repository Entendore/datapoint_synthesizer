"""
Computer vision format generators
"""

import random
from typing import Dict, List
from dataclasses import dataclass, field, asdict


@dataclass
class ImageDatapoint:
    image_path: str
    label: str
    bbox: List[int] = field(default_factory=list)
    segmentation: List = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)
    embedding: List[float] = field(default_factory=list)
    
    def to_dict(self):
        return asdict(self)


class CVFormatGenerator:
    """Generates CV data formats."""
    
    def generate_image_classification(self, n: int, labels: List[str] = None) -> List[Dict]:
        if labels is None:
            labels = ["cat", "dog", "bird", "car", "tree"]
        
        datapoints = []
        for i in range(n):
            dp = ImageDatapoint(
                image_path=f"image_{i:04d}.jpg",
                label=random.choice(labels),
                bbox=[10, 20, 100, 150],
                metadata={"generated": True, "index": i}
            )
            datapoints.append(dp.to_dict())
        
        return datapoints
    
    def generate_object_detection(self, n: int) -> List[Dict]:
        datapoints = []
        for i in range(n):
            datapoints.append({
                "format": "object_detection",
                "image_path": f"image_{i:04d}.jpg",
                "objects": [
                    {
                        "label": random.choice(["cat", "dog", "person"]),
                        "bbox": [random.randint(0, 100), random.randint(0, 100),
                                random.randint(100, 200), random.randint(100, 200)],
                        "confidence": random.uniform(0.5, 1.0)
                    }
                ]
            })
        
        return datapoints
