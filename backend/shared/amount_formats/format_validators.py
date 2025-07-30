"""
Format Validation Logic

Provides validation capabilities for amount formats and parsed values.
"""

import re
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass
from .regional_formats import AmountFormat, RegionalFormatRegistry


@dataclass
class ValidationResult:
    """Results of format validation."""
    is_valid: bool
    confidence: float
    errors: List[str]
    warnings: List[str]
    sample_successes: int
    sample_failures: int
    failed_samples: List[str]


class FormatValidator:
    """
    Validates amount formats and provides validation results with detailed feedback.
    """
    
    def __init__(self):
        self.currency_pattern = re.compile(r'[₹$€£¥₩₪₨₦₡₵₴₸₽¢₮₰₱₲₭₼₾₺]|USD|EUR|GBP|JPY|CHF|CAD|AUD|SEK|NOK|DKK|PLN|CZK|HUF|RON|BGN|HRK|RUB|CNY|INR|KRW|SGD|THB|MYR|IDR|PHP|VND|BRL|ARS|MXN|CLP|COP|PEN|UYU|ZAR|EGP|TRY|ILS|AED|SAR|QAR|KWD|BHD|OMR|JOD')
    
    def validate_format(self, format_obj: AmountFormat) -> ValidationResult:
        """
        Validate an AmountFormat object for internal consistency.
        
        Args:
            format_obj: AmountFormat to validate
            
        Returns:
            ValidationResult with validation details
        """
        errors = []
        warnings = []
        
        # Validate separators
        if format_obj.decimal_separator not in [".", ","]:
            errors.append(f"Invalid decimal separator: '{format_obj.decimal_separator}'")
        
        if format_obj.thousand_separator not in ["", ",", ".", " ", "'"]:
            errors.append(f"Invalid thousand separator: '{format_obj.thousand_separator}'")
        
        # Check for separator conflicts
        if (format_obj.decimal_separator == format_obj.thousand_separator and 
            format_obj.thousand_separator != ""):
            errors.append("Decimal and thousand separators cannot be the same")
        
        # Validate negative style
        if format_obj.negative_style not in ["minus", "parentheses", "suffix"]:
            errors.append(f"Invalid negative style: '{format_obj.negative_style}'")
        
        # Validate currency position
        if format_obj.currency_position not in ["prefix", "suffix", "none"]:
            errors.append(f"Invalid currency position: '{format_obj.currency_position}'")
        
        # Validate grouping pattern
        if not isinstance(format_obj.grouping_pattern, list):
            errors.append("Grouping pattern must be a list")
        elif format_obj.grouping_pattern:
            for group in format_obj.grouping_pattern:
                if not isinstance(group, int) or group <= 0:
                    errors.append(f"Invalid grouping value: {group}")
        
        # Warnings for unusual configurations
        if format_obj.thousand_separator == "" and format_obj.grouping_pattern:
            warnings.append("Grouping pattern specified but no thousand separator defined")
        
        if format_obj.decimal_separator == "," and format_obj.thousand_separator == ".":
            warnings.append("European format detected - ensure this is intended")
        
        confidence = 1.0 if not errors else 0.0
        if warnings:
            confidence *= 0.9
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            confidence=confidence,
            errors=errors,
            warnings=warnings,
            sample_successes=0,
            sample_failures=0,
            failed_samples=[]
        )
    
    def validate_format_with_samples(self, format_obj: AmountFormat, samples: List[str]) -> ValidationResult:
        """
        Validate format against sample data.
        
        Args:
            format_obj: AmountFormat to validate
            samples: List of sample amount strings
            
        Returns:
            ValidationResult with detailed validation results
        """
        # First validate the format itself
        format_validation = self.validate_format(format_obj)
        if not format_validation.is_valid:
            return format_validation
        
        if not samples:
            return ValidationResult(
                is_valid=True,
                confidence=0.5,  # Lower confidence without samples
                errors=[],
                warnings=["No samples provided for validation"],
                sample_successes=0,
                sample_failures=0,
                failed_samples=[]
            )
        
        # Clean samples
        cleaned_samples = self._clean_samples(samples)
        
        # Test each sample
        successes = 0
        failures = 0
        failed_samples = []
        errors = format_validation.errors.copy()
        warnings = format_validation.warnings.copy()
        
        for sample in cleaned_samples:
            try:
                parsed_value = self.parse_amount_with_format(sample, format_obj)
                if parsed_value is not None:
                    successes += 1
                else:
                    failures += 1
                    failed_samples.append(sample)
            except Exception as e:
                failures += 1
                failed_samples.append(f"{sample} (Error: {str(e)})")
        
        total_samples = len(cleaned_samples)
        success_rate = successes / total_samples if total_samples > 0 else 0
        
        # Add validation warnings/errors based on success rate
        if success_rate < 0.5:
            errors.append(f"Low success rate: {success_rate:.1%} of samples parsed successfully")
        elif success_rate < 0.8:
            warnings.append(f"Moderate success rate: {success_rate:.1%} of samples parsed successfully")
        
        # Calculate confidence
        confidence = success_rate
        if total_samples < 5:
            confidence *= 0.8  # Lower confidence with few samples
        if warnings:
            confidence *= 0.9
        
        is_valid = len(errors) == 0 and success_rate >= 0.5
        
        return ValidationResult(
            is_valid=is_valid,
            confidence=confidence,
            errors=errors,
            warnings=warnings,
            sample_successes=successes,
            sample_failures=failures,
            failed_samples=failed_samples
        )
    
    def parse_amount_with_format(self, amount_str: str, format_obj: AmountFormat) -> Optional[float]:
        """
        Parse an amount string using the specified format.
        
        Args:
            amount_str: String representation of amount
            format_obj: AmountFormat to use for parsing
            
        Returns:
            Parsed float value or None if parsing fails
        """
        if not amount_str or amount_str.strip() == "":
            return None
        
        try:
            # Convert to string and clean
            cleaned = str(amount_str).strip()
            
            # Remove currency symbols
            cleaned = self.currency_pattern.sub('', cleaned).strip()
            
            # Handle negative styles and positive signs
            is_negative = False
            if format_obj.negative_style == "parentheses":
                if cleaned.startswith('(') and cleaned.endswith(')'):
                    is_negative = True
                    cleaned = cleaned[1:-1].strip()
            elif format_obj.negative_style == "minus":
                if cleaned.startswith('-'):
                    is_negative = True
                    cleaned = cleaned[1:].strip()
            elif format_obj.negative_style == "suffix":
                if cleaned.endswith('-'):
                    is_negative = True
                    cleaned = cleaned[:-1].strip()
            
            # Handle positive signs (remove them)
            if cleaned.startswith('+'):
                cleaned = cleaned[1:].strip()
            
            # Remove thousand separators
            if format_obj.thousand_separator:
                cleaned = cleaned.replace(format_obj.thousand_separator, '')
            
            # Handle decimal separator
            if format_obj.decimal_separator != '.':
                # Only replace the last occurrence (rightmost decimal separator)
                parts = cleaned.rsplit(format_obj.decimal_separator, 1)
                if len(parts) == 2:
                    cleaned = parts[0] + '.' + parts[1]
            
            # Remove any remaining whitespace
            cleaned = re.sub(r'\s+', '', cleaned)
            
            # Validate the result looks like a number
            if not re.match(r'^-?\d*\.?\d+$', cleaned):
                return None
            
            # Convert to float
            value = float(cleaned)
            
            # Apply negative if needed
            if is_negative:
                value = -value
            
            return value
            
        except (ValueError, AttributeError, TypeError):
            return None
    
    def validate_amount_string(self, amount_str: str, format_obj: AmountFormat) -> Dict[str, Any]:
        """
        Validate a single amount string against a format.
        
        Args:
            amount_str: Amount string to validate
            format_obj: AmountFormat to validate against
            
        Returns:
            Dictionary with validation details
        """
        result = {
            'original': amount_str,
            'is_valid': False,
            'parsed_value': None,
            'errors': [],
            'detected_features': {}
        }
        
        if not amount_str or amount_str.strip() == "":
            result['errors'].append("Empty or whitespace-only string")
            return result
        
        # Detect features
        features = self._detect_amount_features(amount_str)
        result['detected_features'] = features
        
        # Check format compatibility
        compatibility_errors = self._check_format_compatibility(features, format_obj)
        result['errors'].extend(compatibility_errors)
        
        # Try to parse
        parsed_value = self.parse_amount_with_format(amount_str, format_obj)
        result['parsed_value'] = parsed_value
        result['is_valid'] = parsed_value is not None and len(compatibility_errors) == 0
        
        return result
    
    def _clean_samples(self, samples: List[str]) -> List[str]:
        """Clean and filter sample data."""
        cleaned = []
        for sample in samples:
            if sample and str(sample).strip():
                cleaned.append(str(sample).strip())
        return cleaned
    
    def _detect_amount_features(self, amount_str: str) -> Dict[str, Any]:
        """Detect features of an amount string."""
        features = {
            'has_currency': bool(self.currency_pattern.search(amount_str)),
            'currency_symbols': self.currency_pattern.findall(amount_str),
            'has_thousands_comma': ',' in amount_str,
            'has_thousands_period': False,
            'has_thousands_space': False,
            'has_thousands_apostrophe': "'" in amount_str,
            'decimal_separator': None,
            'negative_style': None,
            'apparent_grouping': []
        }
        
        # Check for thousand separators
        if re.search(r'\d\.\d{3}', amount_str):
            features['has_thousands_period'] = True
        if re.search(r'\d\s\d{3}', amount_str):
            features['has_thousands_space'] = True
        
        # Detect decimal separator (rightmost separator with 1-2 digits after)
        decimal_match = re.search(r'[.,](\d{1,2})(?:\s*[\)\-]*)?\s*$', amount_str)
        if decimal_match:
            # Find the actual separator
            separator_match = re.search(r'([.,])' + re.escape(decimal_match.group(1)) + r'(?:\s*[\)\-]*)?\s*$', amount_str)
            if separator_match:
                features['decimal_separator'] = separator_match.group(1)
        
        # Detect negative style
        amount_stripped = amount_str.strip()
        if amount_stripped.startswith('-'):
            features['negative_style'] = 'minus'
        elif amount_stripped.startswith('(') and amount_stripped.endswith(')'):
            features['negative_style'] = 'parentheses'
        elif amount_stripped.endswith('-'):
            features['negative_style'] = 'suffix'
        
        return features
    
    def _check_format_compatibility(self, features: Dict[str, Any], format_obj: AmountFormat) -> List[str]:
        """Check if detected features are compatible with format."""
        errors = []
        
        # Check decimal separator
        if features['decimal_separator'] and features['decimal_separator'] != format_obj.decimal_separator:
            errors.append(f"Decimal separator mismatch: found '{features['decimal_separator']}', expected '{format_obj.decimal_separator}'")
        
        # Check thousand separators
        thousand_sep = format_obj.thousand_separator
        if thousand_sep == ',' and not features['has_thousands_comma']:
            pass  # OK, not required to have thousands
        elif thousand_sep == '.' and not features['has_thousands_period']:
            pass  # OK, not required to have thousands
        elif thousand_sep == ' ' and not features['has_thousands_space']:
            pass  # OK, not required to have thousands
        elif thousand_sep == "'" and not features['has_thousands_apostrophe']:
            pass  # OK, not required to have thousands
        
        # Check for conflicting thousand separators
        if thousand_sep != ',' and features['has_thousands_comma']:
            errors.append(f"Unexpected comma as thousand separator (expected '{thousand_sep}')")
        if thousand_sep != '.' and features['has_thousands_period']:
            errors.append(f"Unexpected period as thousand separator (expected '{thousand_sep}')")
        if thousand_sep != ' ' and features['has_thousands_space']:
            errors.append(f"Unexpected space as thousand separator (expected '{thousand_sep}')")
        if thousand_sep != "'" and features['has_thousands_apostrophe']:
            errors.append(f"Unexpected apostrophe as thousand separator (expected '{thousand_sep}')")
        
        # Check negative style
        if features['negative_style'] and features['negative_style'] != format_obj.negative_style:
            errors.append(f"Negative style mismatch: found '{features['negative_style']}', expected '{format_obj.negative_style}'")
        
        return errors