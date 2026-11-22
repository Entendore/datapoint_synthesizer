"""
Image augmentation strategies
"""

import random
from typing import Dict, List, Tuple


class ImageAugmenter:
    """Image augmentation strategies."""
    
    def apply_geometric_transforms(self, image_data: Dict) -> Dict:
        """Applies geometric transformations."""
        augmented = image_data.copy()
        
        # Random rotation
        augmented['rotation'] = random.uniform(-15, 15)
        
        # Random scaling
        augmented['scale'] = random.uniform(0.8, 1.2)
        
        # Random flip
        augmented['flip_horizontal'] = random.choice([True, False])
        augmented['flip_vertical'] = random.choice([True, False])
        
        return augmented
    
    def apply_color_transforms(self, image_data: Dict) -> Dict:
        """Applies color transformations."""
        augmented = image_data.copy()
        
        augmented['brightness'] = random.uniform(0.8, 1.2)
        augmented['contrast'] = random.uniform(0.8, 1.2)
        augmented['saturation'] = random.uniform(0.8, 1.2)
        
        return augmented
    
    def add_noise(self, image_data: Dict, noise_type: str = "gaussian") -> Dict:
        """Adds noise to image."""
        augmented = image_data.copy()
        augmented['noise_type'] = noise_type
        augmented['noise_level'] = random.uniform(0.01, 0.1)
        return augmented
