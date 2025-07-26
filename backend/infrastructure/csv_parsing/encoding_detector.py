"""
Encoding detection utilities for CSV files
"""
import codecs
import os
from typing import Dict, List, Optional

# Attempt to import chardet
try:
    import chardet
except ImportError:
    chardet = None
    print("[WARNING]  chardet library not found. Encoding detection will rely solely on the internal heuristic chain.")


class EncodingDetector:
    """Detects file encoding with confidence scoring"""
    
    def __init__(self):
        # Encoding fallback chain with priorities
        # UTF-16 is placed early for files with distinct UTF-16 BOMs.
        # windows-1252 is common and often a good fallback.
        self.encoding_chain = [
            'utf-16',        # Handles UTF-16 LE/BE with BOM
            'utf-8-sig',     # UTF-8 with BOM
            'utf-8',         # Standard UTF-8
            'windows-1252',  # Common in Windows environments (Python's cp1252)
            'iso-8859-1',    # Latin-1
            'ascii'          # Basic ASCII
        ]
        self.chardet_available = chardet is not None
        # Thresholds
        self.HIGH_CONFIDENCE_THRESHOLD = 0.80
        # If chardet's guess, after being tested by _test_encoding, meets this, we accept it.
        self.CHARDET_TESTED_ACCEPTANCE_THRESHOLD = 0.70 
    
    def detect_encoding(self, file_path: str, sample_size: int = 8192) -> Dict:
        """
        Detect file encoding with confidence scoring
        
        Args:
            file_path: Path to the CSV file
            sample_size: Number of bytes to sample for detection
            
        Returns:
            dict: {
                'encoding': str,
                'confidence': float,
                'bom_detected': bool,
                'attempted_encodings': list
            }
        """
        print(f" Detecting encoding for file: {file_path}")
        
        attempted_encodings = []

        # Step 1: Try chardet if available
        if self.chardet_available:
            try:
                with open(file_path, 'rb') as f_raw:
                    sample_bytes = f_raw.read(sample_size)

                if not sample_bytes:
                    # Handle empty file scenario early if possible
                    # _test_encoding will also handle this, but good to note
                    print(f"   ℹ File is empty or sample is empty.")
                    # Fall through to manual chain which might assign a default for empty files
                else:
                    chardet_raw_result = chardet.detect(sample_bytes)
                    chardet_enc = chardet_raw_result['encoding']
                    chardet_conf = chardet_raw_result['confidence']

                    if chardet_enc:
                        chardet_enc_norm = chardet_enc.lower()
                        # Python's 'utf-8-sig' handles the BOM, chardet might report 'utf-8' for BOM'd file
                        # or sometimes 'UTF-8-SIG'. We prefer 'utf-8-sig' if a BOM is present.
                        # Our _is_bom_present will verify actual BOM.
                        
                        print(f"    Chardet guess: {chardet_enc_norm} (raw confidence: {chardet_conf:.2f})")

                        try:
                            # Test chardet's suggestion using our _test_encoding for consistent confidence
                            # and to ensure Python recognizes the encoding alias.
                            effective_confidence = self._test_encoding(file_path, chardet_enc_norm, sample_size)
                            attempted_encodings.append({
                                'encoding': chardet_enc_norm,
                                'confidence': effective_confidence,
                                'source': 'chardet_tested',
                                'error': None
                            })
                            print(f"   [SUCCESS] Chardet guess '{chardet_enc_norm}' tested: confidence {effective_confidence:.2f}")
                            if effective_confidence >= self.CHARDET_TESTED_ACCEPTANCE_THRESHOLD:
                                bom_detected = self._is_bom_present(file_path, chardet_enc_norm)
                                print(f"   Using chardet's suggestion '{chardet_enc_norm}' (BOM: {bom_detected})")
                                return {
                                    'encoding': chardet_enc_norm,
                                    'confidence': effective_confidence,
                                    'bom_detected': bom_detected,
                                    'attempted_encodings': attempted_encodings
                                }
                        except Exception as e_test_chardet:
                            error_msg = f"Chardet guess '{chardet_enc_norm}' failed _test_encoding: {str(e_test_chardet)}"
                            print(f"   [ERROR]  {error_msg}")
                            attempted_encodings.append({
                                'encoding': chardet_enc_norm, 'confidence': 0.0,
                                'source': 'chardet_tested', 'error': error_msg
                            })
                    else: # chardet_enc is None
                        print(f"   ℹ Chardet could not determine encoding (confidence: {chardet_conf:.2f}).")
                        attempted_encodings.append({
                            'encoding': None, 'confidence': 0.0, 'source': 'chardet',
                            'error': 'Chardet returned no encoding'})
            except FileNotFoundError: # Should be caught by the caller (UnifiedCSVParser)
                raise
            except Exception as e_chardet_global:
                error_msg = f"Error during chardet processing: {str(e_chardet_global)}"
                print(f"   [ERROR]  {error_msg}")
                attempted_encodings.append({
                    'encoding': None, 'confidence': 0.0, 'source': 'chardet',
                    'error': error_msg
                })

        # Step 2: Try each encoding in the fallback chain
        print(f"   ℹ Trying manual encoding chain...")
        for encoding_name in self.encoding_chain:
            try:
                confidence = self._test_encoding(file_path, encoding_name, sample_size)
                attempted_encodings.append({
                    'encoding': encoding_name, 'confidence': confidence,
                    'source': 'manual_chain', 'error': None
                })
                print(f"   [SUCCESS] Manual '{encoding_name}': confidence {confidence:.2f}")
                
                if confidence >= self.HIGH_CONFIDENCE_THRESHOLD:
                    bom_detected = self._is_bom_present(file_path, encoding_name)
                    print(f"   Using manual encoding '{encoding_name}' (BOM: {bom_detected})")
                    return {
                        'encoding': encoding_name, 'confidence': confidence,
                        'bom_detected': bom_detected, 'attempted_encodings': attempted_encodings
                    }
            except Exception as e_manual: # Should be rare as _test_encoding handles most
                error_msg = f"Error testing manual encoding '{encoding_name}': {str(e_manual)}"
                print(f"   [ERROR]  {error_msg}")
                attempted_encodings.append({
                    'encoding': encoding_name, 'confidence': 0.0,
                    'source': 'manual_chain', 'error': error_msg
                })
        
        # Step 3: If no encoding had high confidence, use the best one found from all attempts
        if attempted_encodings:
            valid_attempts = [att for att in attempted_encodings if att['encoding'] is not None and att['confidence'] > 0.0]
            if valid_attempts:
                best_attempt = max(valid_attempts, key=lambda x: x['confidence'])
                chosen_encoding = best_attempt['encoding']
                bom_detected = self._is_bom_present(file_path, chosen_encoding)
                print(f"    Best encoding from all attempts: '{chosen_encoding}' (confidence: {best_attempt['confidence']:.2f}, BOM: {bom_detected})")
                return {
                    'encoding': chosen_encoding,
                    'confidence': best_attempt['confidence'],
                    'bom_detected': bom_detected,
                    'attempted_encodings': attempted_encodings
                }
        
        # Step 4: Last resort fallback
        print("[WARNING] No encoding detection succeeded, falling back to utf-8")
        bom_detected_fallback = self._is_bom_present(file_path, 'utf-8') # Unlikely for plain utf-8
        return {
            'encoding': 'utf-8',
            'confidence': 0.1,
            'bom_detected': bom_detected_fallback,
            'attempted_encodings': attempted_encodings
        }
    
    def _test_encoding(self, file_path: str, encoding: str, sample_size: int) -> float:
        """Test an encoding and return confidence score"""
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read(sample_size)

            if not content:
                # Check if the file is actually empty
                try:
                    if os.path.getsize(file_path) == 0:
                        return 0.7 # Moderately confident for an empty file
                except OSError: # pragma: no cover
                    pass # File size check failed, proceed with low confidence
                return 0.1 # Low confidence if sample is empty but file might not be

            # Basic confidence metrics
            confidence = 0.5  # Base confidence for successful read
            
            # Check for CSV-like content patterns
            csv_indicators = [',', '"', '\n', '\r']
            if len(content) > 0: # Avoid division by zero for very small content
                csv_score = sum(content.count(indicator) for indicator in csv_indicators)
                # Normalize score by content length and number of indicators
                confidence += min((csv_score / len(content)) * 0.5, 0.3) # Max 0.3 bonus
            
            # Penalty for replacement characters (indicates encoding issues)
            if '\ufffd' in content:
                confidence -= 0.4
            
            # Bonus for clean ASCII-printable content
            if len(content) > 0:
                printable_chars = sum(1 for c in content if c.isprintable() or c.isspace())
                printable_ratio = printable_chars / len(content)
                confidence += printable_ratio * 0.2
            
            return max(0.0, min(confidence, 1.0)) # Ensure confidence is between 0 and 1
            
        except UnicodeDecodeError:
            return 0.0
        except FileNotFoundError: # Re-raise, should be handled by caller or detect_encoding
            raise
        except Exception: # Catch other potential errors during open/read
            return 0.0

    def _is_bom_present(self, file_path: str, detected_encoding_name: str) -> bool:
        """
        Checks if a BOM is likely present by inspecting the first few bytes of the file,
        relevant to the detected encoding.
        """
        normalized_encoding = detected_encoding_name.lower()
        try:
            with open(file_path, 'rb') as f_raw:
                if normalized_encoding == 'utf-8-sig':
                    # Check if the file actually started with a UTF-8 BOM
                    return f_raw.read(3) == codecs.BOM_UTF8
                elif normalized_encoding in ['utf-16', 'utf-16-le', 'utf-16-be']:
                    # Check for UTF-16 BOM (LE or BE)
                    start_bytes = f_raw.read(2)
                    return start_bytes == codecs.BOM_UTF16_LE or start_bytes == codecs.BOM_UTF16_BE
        except IOError: # Or more specific file errors
            return False # Failed to read for BOM check
        return False
