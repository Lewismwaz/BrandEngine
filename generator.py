"""
Core name generation logic with multiple styles and filtering
"""
import random
import threading
import time
from typing import List, Dict, Optional, Callable
from queue import Queue
from concurrent.futures import ThreadPoolExecutor, as_completed

from phonetics import PhoneticEngine
from scoring import NameScorer
from filters import NameFilter
from similarity import SimilarityFilter
from config import NAMING_STYLES


class NameGenerator:
    """Main name generation engine"""
    
    def __init__(self):
        self.phonetic_engine = PhoneticEngine()
        self.scorer = NameScorer()
        self.filter = NameFilter()
        self.similarity_filter = SimilarityFilter()
        self.is_generating = False
        self.generated_count = 0
        
    def generate_names(self, style: str = 'mixed', count: int = 100,
                       min_length: int = 3, max_length: int = 12,
                       progress_callback: Callable = None) -> List[Dict]:
        """
        Generate brand names with specified parameters
        
        Args:
            style: naming style ('compound', 'abstract', 'animal', 'nature', 'mixed')
            count: number of names to generate
            min_length: minimum name length
            max_length: maximum name length
            progress_callback: function to call with progress updates
        
        Returns:
            List of brand dictionaries with name and metadata
        """
        self.is_generating = True
        self.generated_count = 0
        brands = []
        
        # Use thread pool for parallel generation
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = []
            batch_size = min(10, count)
            batches = (count + batch_size - 1) // batch_size
            
            for batch in range(batches):
                batch_count = min(batch_size, count - len(brands))
                future = executor.submit(
                    self._generate_batch,
                    style, batch_count, min_length, max_length
                )
                futures.append(future)
            
            for i, future in enumerate(as_completed(futures)):
                try:
                    batch_names = future.result()
                    brands.extend(batch_names)
                    self.generated_count += len(batch_names)
                    
                    if progress_callback:
                        progress = (i + 1) / len(futures) * 100
                        progress_callback(progress, self.generated_count)
                except Exception as e:
                    print(f"Error generating batch: {e}")
        
        self.is_generating = False
        return brands
    
    def _generate_batch(self, style: str, count: int,
                        min_length: int, max_length: int) -> List[Dict]:
        """Generate a batch of names"""
        batch = []
        attempts = 0
        max_attempts = count * 5  # Prevent infinite loops
        
        while len(batch) < count and attempts < max_attempts:
            attempts += 1
            
            # Generate a name
            if style == 'mixed':
                styles = ['compound', 'abstract', 'animal', 'nature']
                selected_style = random.choice(styles)
            else:
                selected_style = style
            
            name = self.phonetic_engine.generate_name_from_style(selected_style)
            
            # Check length constraints
            if not (min_length <= len(name) <= max_length):
                continue
            
            # Check if name passes filters
            if not self.filter.pass_all_filters(name):
                continue
            
            # Score the name
            score = self.scorer.calculate_score(name, selected_style)
            
            # Add to batch
            brand = {
                'name': name,
                'style': selected_style,
                'score': score,
                'length': len(name)
            }
            batch.append(brand)
        
        return batch
    
    def generate_from_seed(self, seed_words: List[str], count: int = 50) -> List[Dict]:
        """Generate names based on seed words"""
        brands = []
        
        for seed in seed_words:
            if len(brands) >= count:
                break
            
            # Clean and process seed
            seed_clean = ''.join(c for c in seed if c.isalpha())
            if len(seed_clean) < 2:
                continue
            
            # Generate variations
            variations = self._generate_variations(seed_clean, count - len(brands))
            brands.extend(variations)
        
        return brands
    
    def _generate_variations(self, seed: str, count: int) -> List[Dict]:
        """Generate variations of a seed word"""
        variations = []
        seed_lower = seed.lower()
        
        # Create variations by adding prefixes/suffixes
        prefixes = ['Aero', 'Astro', 'Bio', 'Cyber', 'Data', 'Eco', 'Electro', 'Fusion',
                   'Gen', 'Geo', 'Hydra', 'Infra', 'Juno', 'Meta', 'Neon', 'Omni', 'Penta',
                   'Quant', 'Radia', 'Solar', 'Terra', 'Ultra', 'Velo', 'Vortex', 'Zen']
        
        suffixes = ['Byte', 'Core', 'Dex', 'Edge', 'Flow', 'Grid', 'Hub', 'Ion', 'Jet',
                   'Kin', 'Lens', 'Mesh', 'Nex', 'Orb', 'Pulse', 'Rift', 'Sync', 'Tron',
                   'Unity', 'Vault', 'Wave', 'Zen', 'Ark', 'Bit', 'Cloud', 'Dynamo']
        
        for i in range(count):
            # Randomly choose variation type
            variation_type = random.choice(['prefix', 'suffix', 'modified'])
            
            if variation_type == 'prefix' and prefixes:
                prefix = random.choice(prefixes)
                name = prefix + seed_lower.capitalize()
            elif variation_type == 'suffix' and suffixes:
                suffix = random.choice(suffixes)
                name = seed_lower.capitalize() + suffix
            else:
                # Modify the seed
                modified = self._modify_word(seed_lower)
                name = modified.capitalize()
            
            # Score the variation
            score = self.scorer.calculate_score(name, 'seed_variation')
            
            variations.append({
                'name': name,
                'style': 'seed_variation',
                'score': score,
                'length': len(name),
                'seed': seed
            })
        
        return variations
    
    def _modify_word(self, word: str) -> str:
        """Apply random modifications to a word"""
        modifications = [
            lambda w: w.replace('a', 'ae') if 'a' in w else w,
            lambda w: w.replace('e', 'eo') if 'e' in w else w,
            lambda w: w.replace('i', 'io') if 'i' in w else w,
            lambda w: w.replace('o', 'oa') if 'o' in w else w,
            lambda w: w.replace('u', 'ua') if 'u' in w else w,
            lambda w: w + random.choice(['ium', 'ora', 'ex', 'ix']),
            lambda w: random.choice(['x', 'z']) + w,
            lambda w: w + random.choice(['x', 'z']),
            lambda w: w.replace('ck', 'x') if 'ck' in w else w,
            lambda w: w.replace('er', 'ir') if 'er' in w else w,
        ]
        
        # Apply 1-2 random modifications
        num_mods = random.randint(1, 2)
        modified = word
        for _ in range(num_mods):
            mod = random.choice(modifications)
            modified = mod(modified)
        
        return modified
    
    def stop_generation(self):
        """Stop the generation process"""
        self.is_generating = False