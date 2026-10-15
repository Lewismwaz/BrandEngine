"""
Filtering system for brand names
"""
import re
from typing import List, Set
from config import BLACKLIST


class NameFilter:
    """Filters names based on various criteria"""
    
    def __init__(self):
        self.blacklist = set(BLACKLIST)
        self.common_patterns = [
            r'^[0-9]',  # Starts with number
            r'[^a-zA-Z]',  # Contains special characters
            r'(.)\1{3,}',  # More than 3 repeated characters
        ]
        
        # Additional filters
        self.min_length = 3
        self.max_length = 15
    
    def pass_all_filters(self, name: str) -> bool:
        """Check if name passes all filters"""
        return (self.pass_min_length(name) and
                self.pass_max_length(name) and
                self.pass_blacklist(name) and
                self.pass_pattern_filter(name) and
                self.pass_character_filter(name))
    
    def pass_min_length(self, name: str) -> bool:
        """Check minimum length requirement"""
        return len(name) >= self.min_length
    
    def pass_max_length(self, name: str) -> bool:
        """Check maximum length requirement"""
        return len(name) <= self.max_length
    
    def pass_blacklist(self, name: str) -> bool:
        """Check if name is in blacklist"""
        name_lower = name.lower()
        
        # Check exact matches
        if name_lower in self.blacklist:
            return False
        
        # Check partial matches (blacklist word appears in name)
        for word in self.blacklist:
            if word in name_lower:
                return False
        
        return True
    
    def pass_pattern_filter(self, name: str) -> bool:
        """Check against pattern filters"""
        for pattern in self.common_patterns:
            if re.search(pattern, name):
                return False
        return True
    
    def pass_character_filter(self, name: str) -> bool:
        """Check character composition requirements"""
        # Must have at least one vowel
        if not re.search(r'[aeiou]', name.lower()):
            return False
        
        # Must have at least one consonant
        if not re.search(r'[bcdfghjklmnpqrstvwxyz]', name.lower()):
            return False
        
        # Check for proper capitalization (first letter uppercase, rest lowercase)
        if not (name[0].isupper() and name[1:].islower()):
            return False
        
        return True
    
    def add_to_blacklist(self, words: List[str]):
        """Add words to the blacklist"""
        self.blacklist.update([word.lower() for word in words])
    
    def remove_from_blacklist(self, words: List[str]):
        """Remove words from the blacklist"""
        for word in words:
            self.blacklist.discard(word.lower())