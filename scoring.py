"""
Scoring system for evaluating brand names
"""
import re
from typing import Dict, List
from phonetics import PhoneticEngine
from config import SCORING_WEIGHTS


class NameScorer:
    """Evaluates brand names based on multiple criteria"""
    
    def __init__(self):
        self.phonetic_engine = PhoneticEngine()
        self.weights = SCORING_WEIGHTS
        
        # Precompile regex patterns for speed
        self.vowel_pattern = re.compile(r'[aeiou]')
        self.consonant_pattern = re.compile(r'[bcdfghjklmnpqrstvwxyz]')
    
    def calculate_score(self, name: str, style: str = None) -> float:
        """
        Calculate overall score for a brand name
        Score ranges from 0-100
        """
        scores = {}
        
        # Individual scoring components
        scores['length'] = self._score_length(name)
        scores['phonetics'] = self._score_phonetics(name)
        scores['memorability'] = self._score_memorability(name)
        scores['brand_sound'] = self._score_brand_sound(name, style)
        scores['domain_availability'] = 100.0  # Default high, will be updated by domain checker
        
        # Calculate weighted average
        total_score = 0
        total_weight = 0
        
        for criterion, score in scores.items():
            weight = self.weights.get(criterion, 0.1)
            total_score += score * weight
            total_weight += weight
        
        if total_weight > 0:
            final_score = total_score / total_weight
        else:
            final_score = 0
        
        return max(0, min(100, final_score))
    
    def _score_length(self, name: str) -> float:
        """Score based on name length (optimal: 5-8 characters)"""
        length = len(name)
        
        if 5 <= length <= 8:
            return 100.0
        elif 4 <= length <= 9:
            return 80.0
        elif 3 <= length <= 10:
            return 60.0
        elif length < 3:
            return 40.0
        else:
            return max(0, 100 - (length - 8) * 5)  # Penalize for being too long
    
    def _score_phonetics(self, name: str) -> float:
        """Score based on phonetic appeal"""
        return self.phonetic_engine.evaluate_phonetics(name) * 100
    
    def _score_memorability(self, name: str) -> float:
        """Score how memorable the name is"""
        score = 50.0  # Base score
        
        # Unique letter combinations are more memorable
        unique_letters = len(set(name.lower()))
        if unique_letters >= 5:
            score += 20.0
        elif unique_letters >= 3:
            score += 10.0
        
        # Words that are easy to spell are more memorable
        if len(name) <= 10:
            score += 10.0
        
        # Names with common English patterns
        if any(pattern in name.lower() for pattern in ['ing', 'ion', 'ity']):
            score += 10.0
        
        # Penalize names with numbers or special characters
        if any(c.isdigit() or not c.isalnum() for c in name):
            score -= 20.0
        
        return max(0, min(100, score))
    
    def _score_brand_sound(self, name: str, style: str = None) -> float:
        """Score based on how it sounds as a brand"""
        score = 50.0
        name_lower = name.lower()
        
        # Modern tech sound
        modern_sounds = ['ix', 'ox', 'ax', 'ex', 'ux', 'ium', 'ora', 'aero', 'tech', 'labs']
        if any(sound in name_lower for sound in modern_sounds):
            score += 20.0
        
        # Professional sound (ends in certain ways)
        professional_endings = ['y', 'a', 'ic', 'ium', 'os', 'us']
        if any(name_lower.endswith(ending) for ending in professional_endings):
            score += 10.0
        
        # Unique but pronounceable
        if 4 <= len(name) <= 10:
            score += 10.0
        
        # Avoid common/overused patterns
        common_patterns = ['solutions', 'technologies', 'systems', 'global']
        if any(pattern in name_lower for pattern in common_patterns):
            score -= 20.0
        
        return max(0, min(100, score))
    
    def calculate_batch_scores(self, names: List[str], style: str = None) -> Dict[str, float]:
        """Calculate scores for multiple names at once"""
        return {name: self.calculate_score(name, style) for name in names}