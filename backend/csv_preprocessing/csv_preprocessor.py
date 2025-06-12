"""
Generic CSV Preprocessor - Bank-Agnostic CSV Sanitization
Handles universal CSV structural issues before parsing, regardless of bank
"""
from typing import Dict, List, Optional
import csv
import re
import os
from io import StringIO

class GenericCSVPreprocessor:
    """
    Bank-agnostic CSV preprocessor that fixes common CSV structural issues
    
    Issues handled:
    1. Multiline fields within quotes (any bank can have this)
    2. BOM characters and encoding issues
    3. Malformed quotes and escaping
    4. Inconsistent line endings
    5. Empty rows and basic metadata cleanup
    6. Quote normalization
    """
    
    def __init__(self):
        self.debug = True
        
    def preprocess_csv(self, file_path: str, encoding: str = 'utf-8') -> Dict:
        """
        Generic CSV preprocessing that works for any bank
        
        Returns:
        {
            'success': bool,
            'processed_file_path': str,
            'original_rows': int,
            'processed_rows': int, 
            'issues_fixed': List[str],
            'warnings': List[str]
        }
        """
        print(f"\n🔧 GENERIC CSV PREPROCESSING")
        print(f"   📂 Input file: {file_path}")
        
        issues_fixed = []
        warnings = []
        
        try:
            # Step 1: Read raw file content
            raw_content = self._read_raw_content(file_path, encoding)
            original_line_count = len(raw_content.splitlines())
            
            # Step 2: Fix encoding and BOM issues
            cleaned_content = self._fix_encoding_issues(raw_content, issues_fixed)
            
            # Step 3: Normalize line endings
            cleaned_content = self._normalize_line_endings(cleaned_content, issues_fixed)
            
            # Step 4: Fix multiline fields (the main issue)
            cleaned_content = self._fix_multiline_fields(cleaned_content, issues_fixed)
            
            # Step 5: Clean up empty rows and basic structure
            cleaned_content = self._cleanup_structure(cleaned_content, issues_fixed)
            
            # Step 6: Validate and count final rows
            final_lines = cleaned_content.splitlines()
            processed_row_count = len([line for line in final_lines if line.strip()])
            
            # Step 7: Save processed file
            processed_file_path = self._create_temp_file(file_path, '_cleaned')
            self._write_content(processed_file_path, cleaned_content, encoding)
            
            print(f"   ✅ Generic preprocessing complete:")
            print(f"      📊 Original lines: {original_line_count}")
            print(f"      📊 Processed lines: {processed_row_count}")
            print(f"      🔧 Issues fixed: {len(issues_fixed)}")
            
            for issue in issues_fixed:
                print(f"         - {issue}")
            
            return {
                'success': True,
                'processed_file_path': processed_file_path,
                'original_rows': original_line_count,
                'processed_rows': processed_row_count,
                'issues_fixed': issues_fixed,
                'warnings': warnings
            }
            
        except Exception as e:
            print(f"   ❌ Generic preprocessing failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'processed_file_path': file_path,  # Fallback to original
                'original_rows': 0,
                'processed_rows': 0,
                'issues_fixed': issues_fixed,
                'warnings': warnings + [f'Preprocessing failed: {str(e)}']
            }
    
    def _read_raw_content(self, file_path: str, encoding: str = 'utf-8') -> str:
        """Read file with proper encoding handling"""
        try:
            # Try UTF-8 with BOM first
            if encoding == 'utf-8':
                encoding = 'utf-8-sig'
            
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            # Fallback to different encodings
            for fallback_encoding in ['utf-8', 'latin-1', 'cp1252']:
                try:
                    with open(file_path, 'r', encoding=fallback_encoding) as f:
                        return f.read()
                except UnicodeDecodeError:
                    continue
            raise Exception("Could not decode file with any common encoding")
    
    def _fix_encoding_issues(self, content: str, issues_fixed: List[str]) -> str:
        """Fix BOM and encoding issues"""
        original_content = content
        
        # Remove BOM if present
        if content.startswith('\ufeff'):
            content = content[1:]
            issues_fixed.append("Removed BOM character")
        
        # Fix common encoding issues
        replacements = {
            '\u00a0': ' ',  # Non-breaking space
            '\u2013': '-',  # En dash
            '\u2014': '--', # Em dash
            '\u2018': "'",  # Left single quote
            '\u2019': "'",  # Right single quote
            '\u201c': '"',  # Left double quote
            '\u201d': '"',  # Right double quote
        }
        
        for bad_char, good_char in replacements.items():
            if bad_char in content:
                content = content.replace(bad_char, good_char)
                issues_fixed.append(f"Fixed encoding character: {bad_char} → {good_char}")
        
        return content
    
    def _normalize_line_endings(self, content: str, issues_fixed: List[str]) -> str:
        """Normalize line endings to \n"""
        if '\r\n' in content:
            content = content.replace('\r\n', '\n')
            issues_fixed.append("Normalized Windows line endings")
        elif '\r' in content:
            content = content.replace('\r', '\n')
            issues_fixed.append("Normalized Mac line endings")
        
        return content
    
    def _fix_multiline_fields(self, content: str, issues_fixed: List[str]) -> str:
        """
        Fix multiline fields within quotes - the main issue!
        
        This handles cases like:
        "Some text
        continuation line",other,fields
        
        Which should be: "Some text continuation line",other,fields
        """
        lines = content.splitlines()
        if len(lines) <= 1:
            return content
        
        fixed_lines = []
        i = 0
        multiline_fixes = 0
        
        while i < len(lines):
            current_line = lines[i]
            
            # Check if this line has unmatched quotes (indicating multiline field)
            if self._has_unmatched_quotes(current_line):
                # Collect lines until quotes are matched
                collected_lines = [current_line]
                j = i + 1
                
                while j < len(lines) and self._has_unmatched_quotes(''.join(collected_lines)):
                    collected_lines.append(lines[j])
                    j += 1
                
                if len(collected_lines) > 1:
                    # Merge multiline field into single line
                    merged_line = self._merge_multiline_field(collected_lines)
                    fixed_lines.append(merged_line)
                    multiline_fixes += 1
                    i = j
                else:
                    # No multiline issue, keep as is
                    fixed_lines.append(current_line)
                    i += 1
            else:
                # Normal line, keep as is
                fixed_lines.append(current_line)
                i += 1
        
        if multiline_fixes > 0:
            issues_fixed.append(f"Fixed {multiline_fixes} multiline fields")
        
        return '\n'.join(fixed_lines)
    
    def _has_unmatched_quotes(self, text: str) -> bool:
        """Check if text has unmatched quotes"""
        # Count quotes that are not escaped
        quote_count = 0
        escaped = False
        
        for char in text:
            if char == '\\':
                escaped = not escaped
            elif char == '"' and not escaped:
                quote_count += 1
            else:
                escaped = False
        
        return quote_count % 2 != 0
    
    def _merge_multiline_field(self, lines: List[str]) -> str:
        """Merge multiline field into single CSV line"""
        # Join lines with space, preserving the CSV structure
        merged = ' '.join(line.strip() for line in lines if line.strip())
        
        # Clean up extra spaces
        merged = re.sub(r'\s+', ' ', merged)
        
        return merged
    
    def _cleanup_structure(self, content: str, issues_fixed: List[str]) -> str:
        """Clean up empty rows and basic structural issues"""
        lines = content.splitlines()
        original_count = len(lines)
        
        # Remove completely empty lines
        non_empty_lines = [line for line in lines if line.strip()]
        
        # Remove lines that are just commas or whitespace
        cleaned_lines = []
        for line in non_empty_lines:
            stripped = line.strip()
            if stripped and not re.match(r'^[,\s]*$', stripped):
                cleaned_lines.append(line)
        
        empty_removed = original_count - len(cleaned_lines)
        if empty_removed > 0:
            issues_fixed.append(f"Removed {empty_removed} empty/whitespace rows")
        
        return '\n'.join(cleaned_lines)
    
    def _create_temp_file(self, original_path: str, suffix: str = '_cleaned') -> str:
        """Create temporary file path for processed CSV"""
        dir_path = os.path.dirname(original_path)
        filename = os.path.basename(original_path)
        name, ext = os.path.splitext(filename)
        return os.path.join(dir_path, f"{name}{suffix}{ext}")
    
    def _write_content(self, file_path: str, content: str, encoding: str = 'utf-8') -> None:
        """Write content to file"""
        with open(file_path, 'w', encoding=encoding, newline='') as f:
            f.write(content)


# Backward compatibility wrapper
class CSVPreprocessor:
    """Wrapper class for backward compatibility"""
    
    def __init__(self):
        self.generic_preprocessor = GenericCSVPreprocessor()
    
    def preprocess_csv(self, file_path: str, bank_type: str, encoding: str = 'utf-8') -> Dict:
        """
        Bank-agnostic preprocessing (bank_type parameter ignored)
        """
        print(f"🔧 Using bank-agnostic CSV preprocessing (bank_type '{bank_type}' ignored)")
        return self.generic_preprocessor.preprocess_csv(file_path, encoding)
