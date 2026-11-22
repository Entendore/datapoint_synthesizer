"""
Text augmentation strategies
"""

import random
from typing import Dict, List


class TextAugmenter:
    """Advanced text augmentation strategies."""
    
    SYNONYM_DICT = {
        "good": ["excellent", "great", "fine", "superb"],
        "bad": ["terrible", "poor", "awful", "horrible"],
        "big": ["large", "huge", "enormous", "massive"],
        "small": ["tiny", "little", "miniature", "compact"],
        "fast": ["quick", "rapid", "swift", "speedy"],
        "slow": ["sluggish", "gradual", "unhurried", "leisurely"],
        "happy": ["joyful", "cheerful", "delighted", "pleased"],
        "sad": ["unhappy", "sorrowful", "melancholy", "gloomy"],
    }
    
    def synonym_replacement(self, text: str, n_replacements: int = 2) -> str:
        words = text.split()
        replaced = 0
        
        for i, word in enumerate(words):
            if replaced >= n_replacements:
                break
            
            word_lower = word.lower()
            if word_lower in self.SYNONYM_DICT:
                synonym = random.choice(self.SYNONYM_DICT[word_lower])
                if word.istitle():
                    synonym = synonym.title()
                words[i] = synonym
                replaced += 1
        
        return ' '.join(words)
    
    def back_translation(self, text: str) -> str:
        words = text.split()
        if len(words) > 5:
            middle = words[1:-1]
            random.shuffle(middle)
            words[1:-1] = middle
        return ' '.join(words)
    
    def paraphrase(self, text: str) -> str:
        paraphrases = [
            f"In other words, {text}",
            f"To put it differently, {text}",
            f"Essentially, {text}",
            f"Basically, {text}",
        ]
        return random.choice(paraphrases)
    
    def augment_datapoint(self, datapoint: Dict, strategies: List[str] = None) -> Dict:
        if strategies is None:
            strategies = ["synonym", "back_translation"]
        
        augmented = datapoint.copy()
        
        for strategy in strategies:
            for key, value in augmented.items():
                if isinstance(value, str):
                    if strategy == "synonym":
                        augmented[key] = self.synonym_replacement(value)
                    elif strategy == "back_translation":
                        augmented[key] = self.back_translation(value)
                    elif strategy == "paraphrase":
                        augmented[key] = self.paraphrase(value)
        
        augmented['_augmentation_strategies'] = strategies
        return augmented
    
    def augment_dataset(self, datapoints: List[Dict], n_augmentations: int = 3,
                       strategies: List[str] = None) -> List[Dict]:
        augmented_data = []
        
        for dp in datapoints:
            augmented_data.append(dp)
            
            for i in range(n_augmentations):
                aug_dp = self.augment_datapoint(dp, strategies)
                aug_dp['_augmentation_id'] = f"{dp.get('id', 'unknown')}_aug_{i}"
                augmented_data.append(aug_dp)
        
        return augmented_data
