"""
Custom phonetic engine for generating brandable names
"""
import random
from typing import List, Set
import re
from difflib import SequenceMatcher


class PhoneticEngine:
    """Generates phonetically appealing names"""
    
    def __init__(self):
        # Phonetic patterns for different sounds
        self.consonants = 'bcdfghjklmnpqrstvwxyz'
        self.vowels = 'aeiou'
        self.all_letters = self.consonants + self.vowels
        
        # Common phonetic patterns (C = consonant, V = vowel)
        self.patterns = [
            'CVC', 'CVCC', 'CCVC', 'CVVC', 'CVCV',
            'VCCV', 'VCVC', 'CCVCC', 'CVCCV'
        ]
        
        # Common letter combinations that sound good
        self.phonemes = {
            'st': 'st', 'tr': 'tr', 'pl': 'pl', 'gr': 'gr', 'cr': 'cr',
            'br': 'br', 'fr': 'fr', 'pr': 'pr', 'str': 'str', 'spl': 'spl',
            'chr': 'kr', 'ph': 'f', 'gh': 'g', 'ck': 'k'
        }
        
        # Words that sound modern/tech
        self.modern_sounds = ['ix', 'ox', 'ax', 'ex', 'ux', 'ium', 'ora', 'aero']
    
    def generate_syllable(self) -> str:
        """Generate a single syllable"""
        pattern = random.choice(self.patterns)
        syllable = []
        
        for char in pattern:
            if char == 'C':
                syllable.append(random.choice(self.consonants))
            elif char == 'V':
                syllable.append(random.choice(self.vowels))
        
        return ''.join(syllable)
    
    def generate_word(self, min_syllables: int = 2, max_syllables: int = 4) -> str:
        """Generate a phonetic word"""
        num_syllables = random.randint(min_syllables, max_syllables)
        word = []
        
        for i in range(num_syllables):
            syllable = self.generate_syllable()
            word.append(syllable)
        
        return ''.join(word)
    
    def generate_compound(self, prefix: str, suffix: str) -> str:
        """Combine prefix and suffix with phonetic consideration"""
        # Ensure smooth transition between prefix and suffix
        if prefix[-1].lower() in self.vowels and suffix[0].lower() in self.vowels:
            # Both end/start with vowels - add a consonant
            connector = random.choice(self.consonants)
            return prefix + connector + suffix
        elif prefix[-1].lower() in self.consonants and suffix[0].lower() in self.consonants:
            # Both end/start with consonants - add a vowel
            connector = random.choice(self.vowels)
            return prefix + connector + suffix
        else:
            return prefix + suffix
    
    def generate_abstract_name(self, length: int = 8) -> str:
        """Generate an abstract name with random phonetics"""
        name = []
        last_was_vowel = False
        last_char = ''
        
        for i in range(length):
            if not last_char:
                char = random.choice(self.all_letters)
            elif last_was_vowel:
                char = random.choice(self.consonants)
                last_was_vowel = False
            else:
                char = random.choice(self.vowels)
                last_was_vowel = True
            
            name.append(char)
            last_char = char
        
        # Capitalize first letter
        return ''.join(name).capitalize()
    
    def generate_name_from_style(self, style: str, **kwargs) -> str:
        """Generate a name based on style"""
        if style == 'compound':
            prefix = kwargs.get('prefix', '')
            suffix = kwargs.get('suffix', '')
            if not prefix or not suffix:
                # Get from config
                from config import NAMING_STYLES
                prefixes = NAMING_STYLES['compound']['prefixes']
                suffixes = NAMING_STYLES['compound']['suffixes']
                prefix = random.choice(prefixes)
                suffix = random.choice(suffixes)
            return self.generate_compound(prefix, suffix)
        
        elif style == 'abstract':
            length = kwargs.get('length', random.randint(5, 8))
            return self.generate_abstract_name(length)
        
        elif style == 'animal':
            from config import NAMING_STYLES
            animals = NAMING_STYLES['animal']['words']
            animal = random.choice(animals)
            # Add suffix or prefix for variation
            if random.random() > 0.5:
                suffix = random.choice(['', 'Tech', 'Labs', 'Works', 'AI', 'Cloud', 'Data'])
                return animal + suffix
            return animal
        
        elif style == 'nature':
            from config import NAMING_STYLES
            words = NAMING_STYLES['nature']['words']
            word = random.choice(words)
            # Add suffix or prefix for variation
            if random.random() > 0.5:
                suffix = random.choice(['', 'Tech', 'Labs', 'Works', 'AI', 'Cloud', 'Data'])
                return word + suffix
            return word
        
        else:  # mixed/random
            styles = ['compound', 'abstract', 'animal', 'nature']
            selected_style = random.choice(styles)
            return self.generate_name_from_style(selected_style)
    
    def evaluate_phonetics(self, name: str) -> float:
        """
        Evaluate how phonetically appealing a name is
        Returns score from 0-1
        """
        score = 0.0
        name_lower = name.lower()
        
        # Check for vowel-consonant balance (good names have mix)
        vowels = sum(1 for c in name_lower if c in self.vowels)
        consonants = sum(1 for c in name_lower if c in self.consonants)
        if vowels > 0 and consonants > 0:
            ratio = min(vowels, consonants) / max(vowels, consonants)
            score += ratio * 0.3
        
        # Check for common phonetic patterns (easy to pronounce)
        for pattern in self.patterns:
            if pattern.lower() in name_lower:
                score += 0.1
        
        # Check for modern tech sound
        for sound in self.modern_sounds:
            if sound in name_lower:
                score += 0.05
        
        # Penalize for awkward combinations
        awkward = ['x', 'z', 'q']  # Too many rare letters
        rare_count = sum(1 for c in name_lower if c in awkward)
        if rare_count > 2:
            score -= 0.1 * (rare_count - 2)
        
        # Penalize for very long or very short names
        if len(name) < 3:
            score -= 0.2
        elif len(name) > 12:
            score -= 0.1
        
        # Penalize for repeated letters
        if len(set(name_lower)) < len(name_lower) * 0.5:
            score -= 0.1
        
        # Normalize score between 0 and 1
        return max(0.0, min(1.0, score + 0.3))
    
    def is_phonetically_similar(self, name1: str, name2: str, threshold: float = 0.7) -> bool:
        """
        Check if two names are phonetically similar
        Uses Levenshtein ratio on phonetic representations
        """
        # Simple phonetic reduction (just for comparison)
        def reduce_phonetic(s: str) -> str:
            s = s.lower()
            # Replace similar sounds
            replacements = {
                'ph': 'f', 'ck': 'k', 'ch': 'k', 'sh': 's',
                'th': 't', 'qu': 'kw', 'x': 'ks', 'z': 's'
            }
            for pattern, replacement in replacements.items():
                s = s.replace(pattern, replacement)
            return s
        
        reduced1 = reduce_phonetic(name1)
        reduced2 = reduce_phonetic(name2)
        
        return SequenceMatcher(None, reduced1, reduced2).ratio() >= threshold