"""
Similarity filtering for removing duplicates and similar names
"""
from typing import List, Set, Dict
from difflib import SequenceMatcher
import re


def ratio(first: str, second: str) -> float:
    """Return a normalized similarity ratio without external dependencies."""
    return SequenceMatcher(None, first, second).ratio()


class SimilarityFilter:
    """Handles duplicate and similarity filtering"""
    
    def __init__(self):
        self.similarity_threshold = 0.75  # Levenshtein ratio threshold
        self.stored_names = set()
    
    def add_to_stored(self, names: List[str]):
        """Add names to stored set for future comparison"""
        self.stored_names.update([n.lower() for n in names])
    
    def is_similar_to_stored(self, name: str, threshold: float = None) -> bool:
        """Check if name is similar to any stored name"""
        if not self.stored_names:
            return False
        
        threshold = threshold or self.similarity_threshold
        name_lower = name.lower()
        
        # Check exact match first
        if name_lower in self.stored_names:
            return True
        
        # Check approximate matches
        for stored in self.stored_names:
            if ratio(name_lower, stored) >= threshold:
                return True
        
        return False
    
    def is_duplicate(self, name: str, existing_names: List[str], threshold: float = None) -> bool:
        """Check if name is a duplicate of any existing name"""
        threshold = threshold or self.similarity_threshold
        name_lower = name.lower()
        
        for existing in existing_names:
            if ratio(name_lower, existing.lower()) >= threshold:
                return True
        
        return False
    
    def filter_similar(self, names: List[str], threshold: float = None) -> List[str]:
        """Filter out names that are too similar to each other"""
        threshold = threshold or self.similarity_threshold
        filtered = []
        name_set = set()
        
        # Sort by length first (shorter names first tends to keep shorter names)
        sorted_names = sorted(names, key=len)
        
        for name in sorted_names:
            name_lower = name.lower()
            
            # Check if too similar to any already accepted name
            is_similar = False
            for accepted in name_set:
                if ratio(name_lower, accepted.lower()) >= threshold:
                    is_similar = True
                    break
            
            if not is_similar:
                filtered.append(name)
                name_set.add(name_lower)
        
        return filtered
    
    def normalize_for_comparison(self, name: str) -> str:
        """Normalize a name for better comparison"""
        # Remove common suffixes
        suffixes = ['tech', 'labs', 'works', 'ai', 'cloud', 'data']
        normalized = name.lower()
        for suffix in suffixes:
            if normalized.endswith(suffix):
                normalized = normalized[:-len(suffix)]
                break
        
        # Remove common prefixes
        prefixes = ['aero', 'astro', 'bio', 'cyber', 'data']
        for prefix in prefixes:
            if normalized.startswith(prefix):
                normalized = normalized[len(prefix):]
                break
        
        # Remove numbers and special characters
        normalized = re.sub(r'[^a-zA-Z]', '', normalized)
        
        return normalized.strip()
    
    def find_duplicate_groups(self, names: List[str], threshold: float = None) -> List[List[str]]:
        """Group similar names together"""
        threshold = threshold or self.similarity_threshold
        groups = []
        processed = set()
        
        for i, name1 in enumerate(names):
            if i in processed:
                continue
            
            group = [name1]
            processed.add(i)
            
            for j, name2 in enumerate(names[i+1:], start=i+1):
                if j in processed:
                    continue
                
                if ratio(name1.lower(), name2.lower()) >= threshold:
                    group.append(name2)
                    processed.add(j)
            
            if len(group) > 1:
                groups.append(group)
        
        return groups
    
    def get_best_from_group(self, group: List[str], scores: Dict[str, float]) -> str:
        """Get the best name from a group based on scores"""
        if not group:
            return None
        
        best = max(group, key=lambda x: scores.get(x, 0))
        return best