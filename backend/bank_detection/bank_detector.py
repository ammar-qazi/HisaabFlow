"""
Bank detector for identifying bank type from CSV files
"""
import re
from typing import Dict, List, Optional, Tuple, Any
from .config_manager import BankConfigManager

class BankDetectionResult:
    """Result of bank detection analysis"""
    
    def __init__(self, bank_name: str, confidence: float, reasons: List[str]):
        self.bank_name = bank_name
        self.confidence = confidence
        self.reasons = reasons
        self.is_confident = confidence >= 0.7
    
    def __str__(self):
        return f"BankDetectionResult(bank={self.bank_name}, confidence={self.confidence:.2f}, reasons={self.reasons})"

class BankDetector:
    """Detects bank type from CSV files using content signatures and header analysis"""
    
    def __init__(self, config_manager: BankConfigManager = None):
        self.config_manager = config_manager or BankConfigManager()
        self.detection_patterns = self.config_manager.get_detection_patterns()
        
        print(f"🔍 BankDetector initialized with {len(self.detection_patterns)} bank patterns")
    
    def detect_bank(self, filename: str, csv_content: str, headers: List[str]) -> BankDetectionResult:
        """
        Detect bank type from filename, content, and headers
        
        Args:
            filename: Name of the CSV file
            csv_content: Raw CSV content (first few lines)
            headers: List of CSV headers
            
        Returns:
            BankDetectionResult with bank name and confidence score
        """
        print(f"🔍 Detecting bank for file: {filename}")
        print(f"📄 Headers found: {headers}")
        print(f"📖 Content preview: {csv_content[:200]}...")
        
        candidates = []
        
        for bank_name, patterns in self.detection_patterns.items():
            confidence, reasons = self._calculate_confidence(filename, csv_content, headers, patterns)
            
            if confidence > 0:
                candidates.append(BankDetectionResult(bank_name, confidence, reasons))
                print(f"🏦 {bank_name}: confidence={confidence:.2f}, reasons={reasons}")
        
        # Sort by confidence (highest first)
        candidates.sort(key=lambda x: x.confidence, reverse=True)
        
        if candidates:
            best_match = candidates[0]
            print(f"🎯 Best match: {best_match}")
            return best_match
        else:
            print(f"❓ No bank detected, using unknown")
            return BankDetectionResult('unknown', 0.0, ['No patterns matched'])
    
    def _calculate_confidence(self, filename: str, content: str, headers: List[str], 
                            patterns: Dict[str, Any]) -> Tuple[float, List[str]]:
        """Calculate confidence score for a bank pattern"""
        confidence = 0.0
        reasons = []
        
        # 1. Filename pattern matching (20% weight)
        filename_score = self._check_filename_patterns(filename, patterns.get('filename_patterns', []))
        if filename_score > 0:
            confidence += filename_score * 0.2
            reasons.append(f"filename_match({filename_score:.1f})")
        
        # 2. Content signature matching (40% weight)
        content_score = self._check_content_signatures(content, patterns.get('content_signatures', []))
        if content_score > 0:
            confidence += content_score * 0.4
            reasons.append(f"content_signature({content_score:.1f})")
        
        # 3. Header matching (40% weight)
        header_score = self._check_header_patterns(headers, patterns.get('required_headers', []))
        if header_score > 0:
            confidence += header_score * 0.4
            reasons.append(f"header_match({header_score:.1f})")
        
        return confidence, reasons
    
    def _check_filename_patterns(self, filename: str, patterns: List[str]) -> float:
        """Check if filename matches any patterns"""
        filename_lower = filename.lower()
        
        for pattern in patterns:
            if pattern.lower() in filename_lower:
                return 1.0
        
        return 0.0
    
    def _check_content_signatures(self, content: str, signatures: List[str]) -> float:
        """Check if content contains bank-specific signatures"""
        if not signatures:
            return 0.0
            
        content_lower = content.lower()
        matches = 0
        
        for signature in signatures:
            if signature.lower() in content_lower:
                matches += 1
        
        # Return percentage of signatures found
        return matches / len(signatures)
    
    def _check_header_patterns(self, headers: List[str], required_headers: List[str]) -> float:
        """Check if headers match required patterns"""
        if not required_headers or not headers:
            return 0.0
        
        headers_lower = [h.lower().strip() for h in headers]
        matches = 0
        
        for required in required_headers:
            required_lower = required.lower().strip()
            
            # Exact match
            if required_lower in headers_lower:
                matches += 1
                continue
            
            # Partial match (for compound headers)
            for header in headers_lower:
                if required_lower in header or header in required_lower:
                    matches += 1
                    break
        
        # Return percentage of required headers found
        return matches / len(required_headers)
    
    def detect_bank_from_data(self, filename: str, data_rows: List[Dict[str, Any]]) -> BankDetectionResult:
        """
        Detect bank from parsed CSV data
        
        Args:
            filename: Name of the CSV file
            data_rows: List of parsed CSV rows as dictionaries
            
        Returns:
            BankDetectionResult
        """
        if not data_rows:
            return BankDetectionResult('unknown', 0.0, ['No data provided'])
        
        # Extract headers from first row
        headers = list(data_rows[0].keys())
        
        # Create content string from data values for signature matching
        content_parts = []
        for i, row in enumerate(data_rows[:5]):  # Check first 5 rows
            content_parts.extend(str(value) for value in row.values() if value)
            if i >= 4:  # Limit content for performance
                break
        
        content = ' '.join(content_parts)
        
        return self.detect_bank(filename, content, headers)
    
    def get_available_banks(self) -> List[str]:
        """Get list of available bank names"""
        return self.config_manager.get_available_banks()
