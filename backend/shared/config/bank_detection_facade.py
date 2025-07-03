"""
Bank Detection Facade for Unified Config Service
Maintains backward compatibility with existing BankConfigManager interface
"""
import os
import configparser
from typing import Dict, List, Optional, Any
from .unified_config_service import get_unified_config_service


class BankDetectionFacade:
    """
    Facade that adapts UnifiedConfigService to the existing BankConfigManager interface
    Maintains 100% backward compatibility during migration
    """
    
    def __init__(self, config_dir: str = None):
        self.unified_service = get_unified_config_service(config_dir)
        self.config_dir = self.unified_service.config_dir
        
        # For backward compatibility, expose these attributes
        self._bank_configs = {}
        self._detection_patterns = {}
        self._load_legacy_format()
    
    def _load_legacy_format(self):
        """Load configurations in legacy format for backward compatibility"""
        for bank_name in self.unified_service.list_banks():
            bank_config = self.unified_service.get_bank_config(bank_name)
            if bank_config:
                # Convert to legacy configparser format
                config = configparser.ConfigParser()
                
                # Bank info section
                config['bank_info'] = {
                    'bank_name': bank_config.name,
                    'display_name': bank_config.display_name,
                    'cashew_account': bank_config.cashew_account,
                    'file_patterns': ', '.join(bank_config.detection_info.filename_patterns),
                    'detection_content_signatures': ', '.join(bank_config.detection_info.content_signatures),
                    'expected_headers': ', '.join(bank_config.detection_info.required_headers)
                }
                
                # CSV config section
                config['csv_config'] = {
                    'delimiter': bank_config.csv_config.delimiter,
                    'encoding': bank_config.csv_config.encoding,
                    'has_header': str(bank_config.csv_config.has_header)
                }
                
                # Column mapping section
                config['column_mapping'] = bank_config.column_mapping
                
                # Account mapping section (for multi-currency banks)
                if bank_config.account_mapping:
                    config['account_mapping'] = bank_config.account_mapping
                
                # Store in legacy format
                self._bank_configs[bank_name] = config
                self._detection_patterns[bank_name] = {
                    'bank_name': bank_config.name,
                    'display_name': bank_config.display_name,
                    'content_signatures': bank_config.detection_info.content_signatures,
                    'required_headers': bank_config.detection_info.required_headers,
                    'filename_patterns': bank_config.detection_info.filename_patterns,
                    'confidence_weight': bank_config.detection_info.confidence_weight
                }
    
    def load_all_configs(self):
        """Load all bank configuration files (legacy interface)"""
        # This is handled automatically in __init__, but kept for compatibility
        self._load_legacy_format()
        print(f"[BUILD] BankConfigManager initialized with config_dir: {self.config_dir}")
    
    def get_bank_config(self, bank_name: str) -> Optional[configparser.ConfigParser]:
        """Get bank configuration in legacy ConfigParser format"""
        return self._bank_configs.get(bank_name)
    
    def get_detection_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Get detection patterns in legacy format"""
        return self._detection_patterns.copy()
    
    def get_available_banks(self) -> List[str]:
        """Get list of available bank names"""
        return self.unified_service.list_banks()
    
    def get_column_mapping(self, bank_name: str) -> Dict[str, str]:
        """Get column mapping for bank"""
        return self.unified_service.get_column_mapping(bank_name)
    
    def get_csv_config(self, bank_name: str) -> Dict[str, Any]:
        """Get CSV configuration for bank in legacy format"""
        csv_config = self.unified_service.get_csv_config(bank_name)
        if not csv_config:
            return {}
        
        return {
            'delimiter': csv_config.delimiter,
            'quote_char': csv_config.quote_char,
            'encoding': csv_config.encoding,
            'has_header': csv_config.has_header,
            'skip_rows': csv_config.skip_rows
        }
    
    def detect_header_row(self, file_path: str, bank_name: str = None, encoding: str = 'utf-8') -> Dict[str, Any]:
        """
        Detect header row in CSV file
        This method uses the original logic but with unified config service
        """
        try:
            # If bank_name provided, get its expected headers
            expected_headers = []
            if bank_name:
                bank_config = self.unified_service.get_bank_config(bank_name)
                if bank_config:
                    expected_headers = bank_config.detection_info.required_headers
            
            # Read first few rows to detect header
            with open(file_path, 'r', encoding=encoding) as file:
                import csv
                reader = csv.reader(file)
                rows = []
                for i, row in enumerate(reader):
                    rows.append(row)
                    if i >= 10:  # Read first 10 rows max
                        break
            
            if not rows:
                return {
                    'success': False,
                    'error': 'No rows found in CSV file',
                    'header_row': 0, 
                    'confidence': 0.0, 
                    'detected_headers': []
                }
            
            # Analyze rows to find header
            best_header_row = 0
            best_confidence = 0.0
            best_headers = rows[0] if rows else []
            
            for row_index, row in enumerate(rows):
                confidence = self._calculate_header_confidence(row, expected_headers)
                if confidence > best_confidence:
                    best_confidence = confidence
                    best_header_row = row_index
                    best_headers = row
            
            return {
                'success': True,
                'header_row': best_header_row,
                'confidence': best_confidence,
                'detected_headers': best_headers,
                'data_start_row': best_header_row + 1
            }
            
        except Exception as e:
            print(f"[ERROR] [BankDetectionFacade] Header detection failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'header_row': 0, 
                'confidence': 0.0, 
                'detected_headers': []
            }
    
    def _calculate_header_confidence(self, row: List[str], expected_headers: List[str]) -> float:
        """Calculate confidence that a row is a header row"""
        if not row:
            return 0.0
        
        confidence = 0.0
        
        # Check for expected headers
        if expected_headers:
            row_lower = [cell.lower() for cell in row]
            for expected in expected_headers:
                if expected.lower() in row_lower:
                    confidence += 10.0
        
        # Check for common header patterns
        header_keywords = ['date', 'amount', 'description', 'balance', 'transaction', 'payment', 'currency']
        row_text = ' '.join(row).lower()
        for keyword in header_keywords:
            if keyword in row_text:
                confidence += 5.0
        
        # Prefer rows with more non-empty, non-numeric cells
        non_numeric_count = 0
        for cell in row:
            cell_clean = cell.strip()
            if cell_clean and not self._is_numeric(cell_clean):
                non_numeric_count += 1
        
        confidence += non_numeric_count * 2.0
        
        return confidence
    
    def _is_numeric(self, value: str) -> bool:
        """Check if a string represents a numeric value"""
        try:
            float(value.replace(',', '').replace('$', '').replace('€', '').replace('£', ''))
            return True
        except ValueError:
            return False