"""
Bank configuration manager for loading and managing bank-specific configurations
"""
import os
import configparser
from typing import Dict, List, Optional, Any
import sys
import csv

class BankConfigManager:
    """Manages loading and caching of bank configurations"""
    
    def __init__(self, config_dir: str = None):
        if config_dir is None:
            # Try to get config directory through utility function first
            from backend.csv_parser.utils import get_config_dir_for_manager
            user_config_dir = get_config_dir_for_manager()
            
            if user_config_dir:
                self.config_dir = user_config_dir
            else:
                # Default to configs directory relative to backend
                backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                self.config_dir = os.path.join(os.path.dirname(backend_dir), 'configs')
        else:
            self.config_dir = config_dir
            
        self._bank_configs = {}
        self._detection_patterns = {}
        self.load_all_configs()
        
        print(f"[BUILD] BankConfigManager initialized with config_dir: {self.config_dir}")
    
    def load_all_configs(self):
        """Load all bank configuration files"""
        print(f" Loading bank configurations from: {self.config_dir}")

        if not os.path.exists(self.config_dir):
            print(f"[ERROR]  [bank_detection.BankConfigManager] Config directory not found: {self.config_dir}")
            return

        config_files = [f for f in os.listdir(self.config_dir) if f.endswith('.conf')]
        print(f" [bank_detection.BankConfigManager] Found .conf files: {config_files}")

        for config_file in config_files:
            print(f"ℹ [bank_detection.BankConfigManager] Attempting to load: {config_file}")
            if config_file == 'app.conf':  # Skip app config
                continue
                
            bank_name = config_file.replace('.conf', '')
            config_path = os.path.join(self.config_dir, config_file)
            
            try:
                config = self._load_config_file(config_path)
                print(f" [bank_detection.BankConfigManager] Successfully parsed {config_file}. Sections: {config.sections()}")
                self._bank_configs[bank_name] = config
                
                # Extract detection patterns
                detection_info = self._extract_detection_info(config, bank_name)
                self._detection_patterns[bank_name] = detection_info
                
                print(f"[SUCCESS] [bank_detection.BankConfigManager] Loaded config for bank: {bank_name}")
                
            except Exception as e:
                print(f"[ERROR]  [bank_detection.BankConfigManager] Error loading config {config_file}: {str(e)}")
    
    def _load_config_file(self, config_path: str) -> configparser.ConfigParser:
        """Load a single configuration file"""
        config = configparser.ConfigParser()
        config.optionxform = str  # Preserve case sensitivity
        config.read(config_path)
        return config
    
    def _extract_detection_info(self, config: configparser.ConfigParser, bank_name: str) -> Dict[str, Any]:
        """Extract detection patterns from configuration"""
        detection_info = {
            'bank_name': bank_name,
            'display_name': bank_name.title(),
            'content_signatures': [],
            'required_headers': [],
            'filename_patterns': [bank_name.lower()], # Default to bank_name itself, case-insensitive
            'confidence_weight': 1.0 # This seems to be a placeholder, BankDetector has its own weights
        }
        
        # Get bank info from [bank_info] section
        if config.has_section('bank_info'):
            bank_info_dict = dict(config['bank_info'])
            detection_info['display_name'] = bank_info_dict.get('name', bank_name).title()
            
            # Load filename patterns (both simple and regex)
            loaded_filename_patterns = []
            if 'file_patterns' in bank_info_dict:
                patterns = bank_info_dict['file_patterns'].split(',')
                loaded_filename_patterns.extend([p.strip().lower() for p in patterns if p.strip()])
            
            if 'filename_regex_patterns' in bank_info_dict:
                regex_patterns = bank_info_dict['filename_regex_patterns'].split(',')
                loaded_filename_patterns.extend([p.strip() for p in regex_patterns if p.strip()])
                print(f"ℹ [BankConfigManager] Added regex patterns for {bank_name}: {regex_patterns}")
            
            if loaded_filename_patterns:
                detection_info['filename_patterns'] = loaded_filename_patterns
            elif bank_name: # Fallback if no patterns specified in config, use bank_name
                 detection_info['filename_patterns'] = [bank_name.lower()]

            # Load content signatures from 'detection_content_signatures' field in [bank_info]
            detection_keywords_str = bank_info_dict.get('detection_content_signatures', '')
            if detection_keywords_str:
                content_signatures_from_config = [s.strip() for s in detection_keywords_str.split(',') if s.strip()]
                detection_info['content_signatures'] = content_signatures_from_config
                print(f"ℹ [BankConfigManager] For {bank_name}, using 'detection_content_signatures' from config: {content_signatures_from_config}")

        # Get required_headers from [csv_config] section's 'expected_headers'
        bank_specific_expected_headers = []
        if config.has_section('csv_config'):
            csv_cfg = dict(config['csv_config'])
            expected_headers_str = csv_cfg.get('expected_headers', '')
            if expected_headers_str:
                bank_specific_expected_headers = [h.strip() for h in expected_headers_str.split(',') if h.strip()]
                detection_info['required_headers'] = bank_specific_expected_headers
                print(f"ℹ [BankConfigManager] For {bank_name}, using 'expected_headers' for detection's required_headers: {bank_specific_expected_headers}")

        # Fallback for content_signatures if not provided by 'detection_content_signatures'
        if not detection_info['content_signatures']:
            fallback_signatures = [detection_info['display_name']] # Start with display name
            if bank_specific_expected_headers: # Add expected headers as content signatures
                fallback_signatures.extend(bank_specific_expected_headers)
            detection_info['content_signatures'] = list(set(fallback_signatures)) # Use set to remove duplicates
            print(f"ℹ [BankConfigManager] For {bank_name}, using fallback content_signatures (display_name + expected_headers): {detection_info['content_signatures']}")
        
        print(f" Detection info for {bank_name}: {detection_info}")
        return detection_info
    
    def get_bank_config(self, bank_name: str) -> Optional[configparser.ConfigParser]:
        """Get configuration for a specific bank"""
        return self._bank_configs.get(bank_name)
    
    def get_detection_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Get all detection patterns"""
        return self._detection_patterns
    
    def get_available_banks(self) -> List[str]:
        """Get list of available bank names"""
        return list(self._bank_configs.keys())
    
    def get_column_mapping(self, bank_name: str) -> Dict[str, str]:
        """Get column mapping for a specific bank"""
        config = self.get_bank_config(bank_name)
        if not config or not config.has_section('column_mapping'):
            return {}
            
        return dict(config['column_mapping'])
    
    def get_csv_config(self, bank_name: str) -> Dict[str, Any]:
        """Get CSV configuration for a specific bank"""
        config = self.get_bank_config(bank_name)
        if not config or not config.has_section('csv_config'):
            return {
                'header_row': 0,
                'data_start_row': 1,
                'header_detection_method': 'fixed',
                'expected_headers': []
            }
        
        csv_config = dict(config['csv_config'])
        
        # Parse header detection configuration
        header_row = int(csv_config.get('header_row', 0))
        data_start_row = int(csv_config.get('data_start_row', header_row + 1))
        header_detection_method = csv_config.get('header_detection_method', 'fixed')
        expected_headers = csv_config.get('expected_headers', '').split(',')
        expected_headers = [h.strip() for h in expected_headers if h.strip()]
        
        return {
            'header_row': header_row,
            'data_start_row': data_start_row,
            'header_detection_method': header_detection_method,
            'expected_headers': expected_headers,
            'start_row': int(csv_config.get('start_row', data_start_row)),
            'end_col': int(csv_config.get('end_col', 5)),
            'encoding': csv_config.get('encoding', 'utf-8')
        }
    
    def detect_header_row(self, file_path: str, bank_name: str = None, encoding: str = 'utf-8') -> Dict[str, Any]:
        """
        Detect header row location using bank-specific configuration
        
        Args:
            file_path: Path to CSV file
            bank_name: Bank name to use for detection (if None, tries to detect)
            encoding: File encoding
            
        Returns:
            Dict with header_row, data_start_row, and headers information
        """
        print(f" Detecting header row for file: {file_path}, Bank: {bank_name}")
        
        # Read first few lines to understand file structure
        try:
            lines = []
            with open(file_path, 'r', encoding=encoding, newline='') as f:
                reader = csv.reader(f)
                for i, row in enumerate(reader):
                    lines.append(row)
                    if i >= 20:  # Read first 20 lines for analysis
                        break
        except Exception as e:
            print(f"[ERROR]  Error reading file for header detection: {e}")
            return {'success': False, 'error': str(e), 'header_row': 0, 'data_start_row': 1, 'headers': []}
        
        if not lines:
            return {'success': False, 'error': 'No data found in file', 'header_row': 0, 'data_start_row': 1, 'headers': []}
        
        # If bank name provided, use bank-specific configuration
        if bank_name and bank_name in self._bank_configs:
            csv_config = self.get_csv_config(bank_name)
            header_row = csv_config['header_row']
            
            print(f" Using bank-specific header detection: header_row={header_row}")

            if header_row < len(lines):
                headers = [h.replace('\ufeff', '').strip() for h in lines[header_row]]
                expected_headers_from_conf = csv_config.get('expected_headers', [])
                
                # Validate if these headers match expected_headers from config
                if expected_headers_from_conf:
                    match_count = 0
                    temp_headers_lower = [h.lower() for h in headers]
                    for eh in expected_headers_from_conf:
                        # Allow partial match for robustness, e.g. "AMOUNT" in "TOTAL AMOUNT"
                        if any(eh.lower() in th_lower for th_lower in temp_headers_lower):
                            match_count += 1
                    
                    # Consider a match if at least 50% of expected headers are found
                    # or if there are few expected headers (e.g. 1 or 2), require all.
                    required_match_ratio = 0.5 if len(expected_headers_from_conf) > 2 else 1.0
                    
                    if (match_count / len(expected_headers_from_conf)) < required_match_ratio:
                        print(f"[WARNING] Configured header_row {header_row} for {bank_name} does not sufficiently match expected headers on the processed file.")
                        print(f"   Headers found: {headers[:5]}. Expected: {expected_headers_from_conf[:5]}. Match ratio: {match_count / len(expected_headers_from_conf):.2f} < {required_match_ratio:.2f}.")
                        # Do not return; fall through to auto-detection.
                    else:
                        print(f"   [SUCCESS] Configured header_row {header_row} matches expected headers for {bank_name}.")
                        return {
                            'success': True, 'header_row': header_row, 'data_start_row': csv_config['data_start_row'],
                            'headers': headers, 'method': 'bank_config_validated', 'bank_name': bank_name
                        }
                # If no expected_headers in config to verify against, or if validation passed, use the configured row.
                # This case is now handled by the 'else' in the block above if validation passes.
                # If no expected_headers, we assume the configured header_row is correct if within bounds.
                elif not expected_headers_from_conf: # No expected_headers to validate against
                    print(f"   No expected_headers in config for {bank_name} to validate against row {header_row}. Assuming correct.")
                    return {
                        'success': True, 'header_row': header_row, 'data_start_row': csv_config['data_start_row'],
                        'headers': headers, 'method': 'bank_config_unvalidated', 'bank_name': bank_name
                    }
            else:
                print(f"[WARNING] Configured header row {header_row} is beyond file length {len(lines)}")
        
        # Fallback: Auto-detect headers if bank-specific logic didn't return
        print(f" Falling back to auto-detection for header row in '{os.path.basename(file_path)}'...")
        return self._auto_detect_headers(lines)
    
    def _auto_detect_headers(self, lines: List[List[str]]) -> Dict[str, Any]:
        """Auto-detect header row by analyzing content patterns"""
        header_candidates = []
        financial_keywords = ['date', 'time', 'timestamp', 'amount', 'balance', 'description', 
                             'type', 'transaction', 'currency', 'reference', 'memo', 'note']
        
        for i, line in enumerate(lines[:15]):  # Check first 15 lines
            if not line:
                continue
                
            # Score this line as potential header
            score = 0
            reasons = []
            line_lower = [cell.lower().strip() for cell in line]
            
            # Check for financial keywords
            for cell in line_lower:
                for keyword in financial_keywords:
                    if keyword in cell:
                        score += 1
                        reasons.append(f"contains_{keyword}")
                        break
            
            # Bonus for all-text row, penalty for mostly numbers
            if all(not cell.replace('-', '').replace('.', '').replace(',', '').isdigit() 
                   for cell in line if cell.strip()):
                score += 2
                reasons.append("all_text")
            
            numeric_cells = sum(1 for cell in line if cell.strip() and 
                              cell.replace('-', '').replace('.', '').replace(',', '').isdigit())
            if numeric_cells > len(line) / 2:
                score -= 1
                reasons.append("mostly_numeric")
            
            if score > 0:
                header_candidates.append({
                    'row_index': i, 'score': score, 'headers': line, 'reasons': reasons
                })
                print(f"  Row {i}: score={score}, reasons={reasons}, content={line[:3]}")
        
        # Select best candidate or fallback
        if header_candidates:
            best_candidate = max(header_candidates, key=lambda x: x['score'])
            header_row = best_candidate['row_index']
            headers = [h.replace('\ufeff', '').strip() for h in best_candidate['headers']]
            print(f"Auto-detected headers at row {header_row}: {headers}")
            
            return {
                'success': True, 'header_row': header_row, 'data_start_row': header_row + 1,
                'headers': headers, 'method': 'auto_detect', 'score': best_candidate['score'],
                'reasons': best_candidate['reasons']
            }
        else:
            print(" No clear headers detected, defaulting to row 0")
            headers = [h.replace('\ufeff', '').strip() for h in lines[0]] if lines else []
            return {
                'success': True, 'header_row': 0, 'data_start_row': 1,
                'headers': headers, 'method': 'fallback'
            }
