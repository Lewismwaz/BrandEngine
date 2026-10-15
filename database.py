"""
Database operations for storing and managing generated brand names
"""
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import json

from config import DATABASE_PATH


class DatabaseManager:
    """Manages SQLite database operations for brand names"""
    
    def __init__(self):
        self.db_path = DATABASE_PATH
        self._initialize_database()
    
    def _initialize_database(self):
        """Create database tables if they don't exist"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Brands table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS brands (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    style TEXT,
                    score REAL,
                    domain_available TEXT,
                    domains_checked TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT
                )
            ''')
            
            # Indexes for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_brands_name ON brands(name)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_brands_score ON brands(score DESC)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_brands_domain ON brands(domain_available)')
            
            conn.commit()
    
    def add_brand(self, name: str, style: str = None, score: float = 0.0,
                  domain_available: str = None, domains_checked: List[str] = None,
                  metadata: Dict = None) -> bool:
        """Add a brand name to the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                domains_json = json.dumps(domains_checked) if domains_checked else None
                metadata_json = json.dumps(metadata) if metadata else None
                
                cursor.execute('''
                    INSERT OR IGNORE INTO brands 
                    (name, style, score, domain_available, domains_checked, metadata)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (name, style, score, domain_available, domains_json, metadata_json))
                
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Database error adding brand: {e}")
            return False
    
    def add_brands_batch(self, brands: List[Dict]) -> int:
        """Add multiple brands in batch for better performance"""
        if not brands:
            return 0
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Prepare data
                data = []
                for brand in brands:
                    data.append((
                        brand['name'],
                        brand.get('style'),
                        brand.get('score', 0.0),
                        brand.get('domain_available'),
                        json.dumps(brand.get('domains_checked', [])),
                        json.dumps(brand.get('metadata', {}))
                    ))
                
                cursor.executemany('''
                    INSERT OR IGNORE INTO brands 
                    (name, style, score, domain_available, domains_checked, metadata)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', data)
                
                conn.commit()
                return cursor.rowcount
        except sqlite3.Error as e:
            print(f"Database error adding brands batch: {e}")
            return 0
    
    def get_brands(self, limit: int = 100, offset: int = 0,
                   min_score: float = None, style: str = None,
                   domain_available: bool = None) -> List[Dict]:
        """Retrieve brands with optional filtering"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                query = "SELECT * FROM brands WHERE 1=1"
                params = []
                
                if min_score is not None:
                    query += " AND score >= ?"
                    params.append(min_score)
                
                if style:
                    query += " AND style = ?"
                    params.append(style)
                
                if domain_available is not None:
                    query += " AND domain_available = ?"
                    params.append('yes' if domain_available else 'no')
                
                query += " ORDER BY score DESC LIMIT ? OFFSET ?"
                params.extend([limit, offset])
                
                cursor.execute(query, params)
                results = cursor.fetchall()
                
                brands = []
                for row in results:
                    brand = dict(row)
                    if brand['domains_checked']:
                        brand['domains_checked'] = json.loads(brand['domains_checked'])
                    if brand['metadata']:
                        brand['metadata'] = json.loads(brand['metadata'])
                    brands.append(brand)
                
                return brands
        except sqlite3.Error as e:
            print(f"Database error getting brands: {e}")
            return []
    
    def search_brands(self, query: str, limit: int = 50) -> List[Dict]:
        """Search for brands by name"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM brands 
                    WHERE name LIKE ? 
                    ORDER BY score DESC LIMIT ?
                ''', (f'%{query}%', limit))
                
                results = cursor.fetchall()
                brands = []
                for row in results:
                    brand = dict(row)
                    if brand['domains_checked']:
                        brand['domains_checked'] = json.loads(brand['domains_checked'])
                    if brand['metadata']:
                        brand['metadata'] = json.loads(brand['metadata'])
                    brands.append(brand)
                
                return brands
        except sqlite3.Error as e:
            print(f"Database error searching brands: {e}")
            return []
    
    def delete_brand(self, name: str) -> bool:
        """Delete a brand from the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM brands WHERE name = ?', (name,))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Database error deleting brand: {e}")
            return False
    
    def clear_all(self) -> bool:
        """Clear all brands from the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM brands')
                conn.commit()
                return True
        except sqlite3.Error as e:
            print(f"Database error clearing brands: {e}")
            return False
    
    def get_stats(self) -> Dict:
        """Get database statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total count
                cursor.execute('SELECT COUNT(*) FROM brands')
                total = cursor.fetchone()[0]
                
                # Count by domain availability
                cursor.execute('''
                    SELECT domain_available, COUNT(*) FROM brands 
                    WHERE domain_available IS NOT NULL 
                    GROUP BY domain_available
                ''')
                domain_stats = dict(cursor.fetchall())
                
                # Average score
                cursor.execute('SELECT AVG(score) FROM brands')
                avg_score = cursor.fetchone()[0] or 0
                
                return {
                    'total': total,
                    'domain_stats': domain_stats,
                    'avg_score': avg_score
                }
        except sqlite3.Error as e:
            print(f"Database error getting stats: {e}")
            return {'total': 0, 'domain_stats': {}, 'avg_score': 0}