"""
Export functionality for generated brand names
"""
import csv
import importlib
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict
from config import EXPORTS_DIR


class Exporter:
    """Export brands to various formats"""
    
    def __init__(self):
        self.exports_dir = EXPORTS_DIR
        self.exports_dir.mkdir(exist_ok=True)
    
    def export_to_csv(self, brands: List[Dict], filename: str = None) -> str:
        """Export brands to CSV format"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"brands_{timestamp}.csv"
        
        filepath = self.exports_dir / filename
        
        # Prepare data for CSV
        fieldnames = ['name', 'style', 'score', 'length', 'domain_available', 
                     'domains_checked', 'created_at', 'metadata']
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            
            for brand in brands:
                # Flatten nested structures for CSV
                row = brand.copy()
                if 'domains_checked' in row and isinstance(row['domains_checked'], list):
                    row['domains_checked'] = ', '.join(row['domains_checked'])
                if 'metadata' in row and isinstance(row['metadata'], dict):
                    row['metadata'] = json.dumps(row['metadata'])
                writer.writerow(row)
        
        return str(filepath)
    
    def export_to_json(self, brands: List[Dict], filename: str = None) -> str:
        """Export brands to JSON format"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"brands_{timestamp}.json"
        
        filepath = self.exports_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(brands, f, indent=2, default=str)
        
        return str(filepath)
    
    def export_to_excel(self, brands: List[Dict], filename: str = None) -> str:
        """Export brands to Excel format"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"brands_{timestamp}.xlsx"
        
        filepath = self.exports_dir / filename
        
        # Load the optional dependency only when Excel export is requested.
        try:
            workbook_class = importlib.import_module('openpyxl').Workbook
        except ImportError as exc:
            raise RuntimeError(
                'Excel export requires the openpyxl package. '
                'Install it with: pip install openpyxl'
            ) from exc

        workbook = workbook_class()
        worksheet = workbook.active
        worksheet.title = 'Brands'

        columns = list(dict.fromkeys(key for brand in brands for key in brand))
        worksheet.append(columns)

        for brand in brands:
            row = []
            for column in columns:
                value = brand.get(column)
                if isinstance(value, (list, dict)):
                    value = json.dumps(value)
                row.append(value)
            worksheet.append(row)

        workbook.save(filepath)
        
        return str(filepath)
    
    def export_filtered(self, brands: List[Dict], min_score: float = 0,
                        domain_available: bool = None, format: str = 'csv') -> str:
        """Export filtered brands"""
        filtered = brands.copy()
        
        if min_score > 0:
            filtered = [b for b in filtered if b.get('score', 0) >= min_score]
        
        if domain_available is not None:
            filtered = [b for b in filtered if b.get('domain_available') == 
                       ('yes' if domain_available else 'no')]
        
        if format == 'csv':
            return self.export_to_csv(filtered)
        elif format == 'json':
            return self.export_to_json(filtered)
        elif format == 'excel':
            return self.export_to_excel(filtered)
        else:
            raise ValueError(f"Unsupported format: {format}")