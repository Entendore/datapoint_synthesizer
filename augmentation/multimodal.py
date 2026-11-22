"""
Multi-modal data generation
"""

import random
from typing import Dict, List
from dataclasses import dataclass, field, asdict

import numpy as np


@dataclass
class ImageDatapoint:
    image_path: str
    label: str
    bbox: List[int] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)
    embedding: List[float] = field(default_factory=list)
    
    def to_dict(self):
        return asdict(self)


@dataclass
class AudioDatapoint:
    audio_path: str
    transcript: str
    language: str = "en"
    duration: float = 0.0
    sample_rate: int = 16000
    metadata: Dict = field(default_factory=dict)
    embedding: List[float] = field(default_factory=list)
    
    def to_dict(self):
        return asdict(self)


@dataclass
class VideoDatapoint:
    video_path: str
    caption: str
    duration: float = 0.0
    fps: int = 30
    metadata: Dict = field(default_factory=dict)
    embedding: List[float] = field(default_factory=list)
    
    def to_dict(self):
        return asdict(self)


class MultiModalGenerator:
    """Generates multi-modal datapoints."""
    
    def generate_image_dataset(self, n: int, labels: List[str] = None) -> List[Dict]:
        if labels is None:
            labels = ["cat", "dog", "bird", "car", "tree"]
        
        datapoints = []
        for i in range(n):
            dp = ImageDatapoint(
                image_path=f"synthetic_image_{i:04d}.jpg",
                label=random.choice(labels),
                bbox=[10, 20, 100, 150],
                metadata={"generated": True, "index": i},
                embedding=np.random.randn(512).tolist()
            )
            datapoints.append(dp.to_dict())
        
        return datapoints
    
    def generate_audio_dataset(self, n: int, languages: List[str] = None) -> List[Dict]:
        if languages is None:
            languages = ["en", "es", "fr", "de", "zh"]
        
        datapoints = []
        for i in range(n):
            dp = AudioDatapoint(
                audio_path=f"synthetic_audio_{i:04d}.wav",
                transcript=f"Sample transcript {i}",
                language=random.choice(languages),
                duration=random.uniform(1.0, 10.0),
                sample_rate=16000,
                metadata={"generated": True, "index": i},
                embedding=np.random.randn(256).tolist()
            )
            datapoints.append(dp.to_dict())
        
        return datapoints
    
    def generate_video_dataset(self, n: int) -> List[Dict]:
        datapoints = []
        for i in range(n):
            dp = VideoDatapoint(
                video_path=f"synthetic_video_{i:04d}.mp4",
                caption=f"Video caption {i}",
                duration=random.uniform(5.0, 60.0),
                fps=30,
                metadata={"generated": True, "index": i},
                embedding=np.random.randn(1024).tolist()
            )
            datapoints.append(dp.to_dict())
        
        return datapoints
