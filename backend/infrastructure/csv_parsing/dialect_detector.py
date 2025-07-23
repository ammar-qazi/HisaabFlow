"""
CSV dialect detection utilities
"""
import csv
import io
from typing import Dict, List, Optional, Tuple
from .exceptions import DialectDetectionError

class DialectDetector:
    """Detects CSV dialect parameters with confidence scoring"""
    
    def __init__(self):
        self.delimiter_candidates = [',', ';', '\t', '|', ':']
        self.quote_candidates = ['"', "'"]
        self.quoting_modes = [
            csv.QUOTE_ALL,        # Quote all fields (Forint Bank style)
            csv.QUOTE_MINIMAL,    # Quote only when necessary 
            csv.QUOTE_NONNUMERIC, # Quote non-numeric fields
            csv.QUOTE_NONE        # No quoting
        ]
    
    def detect_dialect(self, file_path: str, encoding: str, sample_lines: int = 10) -> Dict:
        """
        Detect CSV dialect parameters
        
        Args:
            file_path: Path to the CSV file
            encoding: File encoding to use
            sample_lines: Number of lines to analyze
            
        Returns:
            dict: {
                'delimiter': str,
                'quotechar': str, 
                'quoting': int,
                'skipinitialspace': bool,
                'confidence': float,
                'line_terminator': str,
                'detected_patterns': dict
            }
        """
        print(f" Detecting CSV dialect for file: {file_path}")
        
        try:
            # Read sample content
            with open(file_path, 'r', encoding=encoding) as f:
                lines = []
                for i, line in enumerate(f):
                    lines.append(line.rstrip('\r\n'))
                    if i >= sample_lines - 1:
                        break
            
            if not lines:
                raise DialectDetectionError("No lines found in file", file_path)
            
            print(f"   [DATA] Analyzing {len(lines)} sample lines")
            
            # Detect delimiter
            delimiter_result = self._detect_delimiter(lines)
            print(f"   [SUCCESS] Delimiter: '{delimiter_result['delimiter']}' (confidence: {delimiter_result['confidence']:.2f})")
            
            # Detect quote character and quoting mode
            quote_result = self._detect_quoting(lines, delimiter_result['delimiter'])
            print(f"   [SUCCESS] Quoting: char='{quote_result['quotechar']}', mode={quote_result['quoting']} (confidence: {quote_result['confidence']:.2f})")
            
            # Detect line terminator
            line_terminator = self._detect_line_terminator(file_path, encoding)
            print(f"   [SUCCESS] Line terminator: {repr(line_terminator)}")
            
            # Calculate overall confidence
            overall_confidence = (delimiter_result['confidence'] + quote_result['confidence']) / 2
            
            return {
                'delimiter': delimiter_result['delimiter'],
                'quotechar': quote_result['quotechar'],
                'quoting': quote_result['quoting'],
                'skipinitialspace': True,  # Generally safe default
                'confidence': overall_confidence,
                'line_terminator': line_terminator,
                'detected_patterns': {
                    'delimiter_analysis': delimiter_result,
                    'quote_analysis': quote_result
                }
            }
            
        except Exception as e:
            print(f"[ERROR]  Dialect detection failed: {str(e)}")
            # Return safe defaults
            return {
                'delimiter': ',',
                'quotechar': '"',
                'quoting': csv.QUOTE_MINIMAL,
                'skipinitialspace': True,
                'confidence': 0.1,
                'line_terminator': '\n',
                'detected_patterns': {'error': str(e)}
            }
    
    def _detect_delimiter(self, lines: List[str]) -> Dict:
        """Detect the most likely delimiter"""
        delimiter_scores = {}
        
        for delimiter in self.delimiter_candidates:
            score = 0
            consistent_count = 0
            field_counts = []
            
            for line in lines:
                if not line.strip():
                    continue
                    
                # Count delimiter occurrences
                delimiter_count = line.count(delimiter)
                field_counts.append(delimiter_count + 1)  # +1 for field count
                
                if delimiter_count > 0:
                    score += delimiter_count
            
            # Bonus for consistent field counts across lines
            if field_counts:
                most_common_count = max(set(field_counts), key=field_counts.count)
                consistency_ratio = field_counts.count(most_common_count) / len(field_counts)
                score *= (1 + consistency_ratio)
            
            delimiter_scores[delimiter] = score
        
        # Find best delimiter
        if delimiter_scores:
            best_delimiter = max(delimiter_scores, key=delimiter_scores.get)
            max_score = delimiter_scores[best_delimiter]
            total_score = sum(delimiter_scores.values())
            confidence = max_score / total_score if total_score > 0 else 0.1
        else:
            best_delimiter = ','
            confidence = 0.1
        
        return {
            'delimiter': best_delimiter,
            'confidence': min(confidence, 1.0),
            'scores': delimiter_scores
        }
    
    def _detect_quoting(self, lines: List[str], delimiter: str) -> Dict:
        """Detect quote character and quoting mode"""
        quote_char_scores = {}
        
        for quote_char in self.quote_candidates:
            score = 0
            
            for line in lines:
                if not line.strip():
                    continue
                    
                # Count quote occurrences
                quote_count = line.count(quote_char)
                
                # Check if quotes are properly paired
                if quote_count > 0 and quote_count % 2 == 0:
                    score += quote_count
                    
                    # Bonus for quotes around delimiter-containing fields
                    fields = line.split(delimiter)
                    for field in fields:
                        if (field.startswith(quote_char) and field.endswith(quote_char) and 
                            delimiter in field[1:-1]):
                            score += 5  # Strong indicator
            
            quote_char_scores[quote_char] = score
        
        # Determine best quote character
        best_quote_char = '"'  # Default
        quote_confidence = 0.5
        
        if quote_char_scores:
            best_quote_char = max(quote_char_scores, key=quote_char_scores.get)
            max_score = quote_char_scores[best_quote_char]
            if max_score > 0:
                quote_confidence = min(max_score / (len(lines) * 10), 1.0)  # Normalize
        
        # Detect quoting mode by analyzing field patterns
        quoting_mode = self._detect_quoting_mode(lines, delimiter, best_quote_char)
        
        return {
            'quotechar': best_quote_char,
            'quoting': quoting_mode,
            'confidence': quote_confidence,
            'scores': quote_char_scores
        }
    
    def _detect_quoting_mode(self, lines: List[str], delimiter: str, quote_char: str) -> int:
        """Detect the quoting mode used in the CSV"""
        quote_all_lines = 0
        total_lines = 0
        
        for line in lines:
            if not line.strip():
                continue
            
            total_lines += 1
            line = line.strip()
            
            # Check if this looks like a quote-all line
            # Strategy: try to parse with both quote modes and see which works better
            
            # Method 1: Pattern matching - look for consistent "field","field" pattern
            if line.startswith(quote_char):
                # Count actual quoted fields by looking for quote-delimiter-quote or quote-end patterns
                import re
                # Pattern: "something" followed by delimiter or end of line
                quoted_field_pattern = quote_char + r'[^"]*' + quote_char + r'(?:' + re.escape(delimiter) + r'|$)'
                quoted_fields = len(re.findall(quoted_field_pattern, line))
                
                # Count total fields by splitting (but be careful with empty trailing fields)
                fields = line.split(delimiter)
                non_empty_trailing = len([f for f in fields if f.strip()])
                
                # If most/all fields are quoted, this suggests quote-all
                if quoted_fields >= max(4, non_empty_trailing * 0.8):  # At least 80% of fields quoted
                    quote_all_lines += 1
                    print(f"    Line {total_lines}: {quoted_fields} quoted fields detected as quote-all pattern")
        
        if total_lines == 0:
            return csv.QUOTE_MINIMAL
        
        quote_all_ratio = quote_all_lines / total_lines
        
        if quote_all_ratio >= 0.75:  # 75%+ of lines follow quote-all pattern
            print(f"   Quote-all pattern detected (ratio: {quote_all_ratio:.2f})")
            return csv.QUOTE_ALL
        else:
            print(f"    Selective quoting detected (quote-all ratio: {quote_all_ratio:.2f})")
            return csv.QUOTE_MINIMAL
    
    def _detect_line_terminator(self, file_path: str, encoding: str) -> str:
        """Detect line terminator style including non-standard patterns"""
        try:
            # Read a larger sample to better detect line endings
            with open(file_path, 'rb') as f:
                sample = f.read(8192)  # Increased sample size
            
            if not sample:
                return '\n'  # Safe default for empty files
            
            # Count different line ending patterns, including non-standard ones
            line_ending_counts = {
                b'\r\r': sample.count(b'\r\r'),      # Non-standard double CR
                b'\r\n': sample.count(b'\r\n'),      # Windows CRLF
                b'\n\r': sample.count(b'\n\r'),      # Reverse CRLF (rare)
                b'\n': 0,                            # Unix LF (calculated below)
                b'\r': 0                             # Mac CR (calculated below)
            }
            
            # Calculate standalone LF and CR counts (excluding compound patterns)
            lf_total = sample.count(b'\n')
            cr_total = sample.count(b'\r')
            
            # Subtract compound patterns to get standalone counts
            line_ending_counts[b'\n'] = (lf_total - 
                                       line_ending_counts[b'\r\n'] - 
                                       line_ending_counts[b'\n\r'])
            
            line_ending_counts[b'\r'] = (cr_total - 
                                       line_ending_counts[b'\r\n'] - 
                                       line_ending_counts[b'\n\r'] - 
                                       (line_ending_counts[b'\r\r'] * 2))  # Double CR uses 2 CR chars
            
            # Find the most common line ending pattern
            max_count = 0
            detected_pattern = b'\n'  # Default fallback
            
            for pattern, count in line_ending_counts.items():
                if count > max_count:
                    max_count = count
                    detected_pattern = pattern
            
            # Convert bytes pattern to string
            line_terminator_map = {
                b'\r\r': '\r\r',    # Non-standard double CR
                b'\r\n': '\r\n',    # Windows CRLF
                b'\n\r': '\n\r',    # Reverse CRLF
                b'\n': '\n',        # Unix LF
                b'\r': '\r'         # Mac CR
            }
            
            result = line_terminator_map.get(detected_pattern, '\n')
            
            # Log the detection results for debugging
            print(f"       Line ending analysis:")
            for pattern, count in line_ending_counts.items():
                if count > 0:
                    pattern_name = line_terminator_map.get(pattern, str(pattern))
                    print(f"         {repr(pattern_name)}: {count} occurrences")
            
            print(f"       Selected line terminator: {repr(result)} ({max_count} occurrences)")
            
            return result
            
        except Exception as e:
            print(f"       [WARNING] Line terminator detection failed: {e}, using default")
            return '\n'  # Safe default
