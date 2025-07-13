"""
Amount Format Detection and Analysis

Provides automatic detection of amount formats from sample data with confidence scoring.
"""

import re
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass
from .regional_formats import AmountFormat, RegionalFormatRegistry


@dataclass
class AmountFormatAnalysis:
    """Results of amount format analysis."""
    detected_format: AmountFormat
    confidence: float
    sample_count: int
    detected_patterns: Dict[str, int]
    problematic_samples: List[str]
    currency_symbols: List[str]


class AmountFormatDetector:
    """
    Detects amount formats from sample data using pattern analysis and confidence scoring.
    """
    
    def __init__(self):
        self.formats = RegionalFormatRegistry.get_all_formats()
        
        # Regex patterns for different components
        self.currency_pattern = re.compile(r'[₹$€£¥₩₪₨₦₡₵₴₸₽¢₮₰₱₲₭₼₾₺]|USD|EUR|GBP|JPY|CHF|CAD|AUD|SEK|NOK|DKK|PLN|CZK|HUF|RON|BGN|HRK|RUB|CNY|INR|KRW|SGD|THB|MYR|IDR|PHP|VND|BRL|ARS|MXN|CLP|COP|PEN|UYU|ZAR|EGP|TRY|ILS|AED|SAR|QAR|KWD|BHD|OMR|JOD')
        self.amount_pattern = re.compile(r'[-\(\)]*\s*\d{1,3}(?:[,.\s\']?\d{3})*(?:[,.]?\d{1,2})?\s*[-\(\)]*')
        
    def detect_format(self, amount_samples: List[str]) -> Tuple[AmountFormat, float]:
        """
        Detect amount format from samples with confidence score.
        
        Args:
            amount_samples: List of amount strings to analyze
            
        Returns:
            Tuple of (detected_format, confidence_score)
        """
        if not amount_samples:
            return RegionalFormatRegistry.AMERICAN, 0.0
        
        analysis = self.analyze_amount_column(amount_samples)
        return analysis.detected_format, analysis.confidence
    
    def analyze_amount_column(self, amount_samples: List[str]) -> AmountFormatAnalysis:
        """
        Comprehensive analysis of amount column data.
        
        Args:
            amount_samples: List of amount strings to analyze
            
        Returns:
            AmountFormatAnalysis with detailed results
        """
        if not amount_samples:
            return AmountFormatAnalysis(
                detected_format=RegionalFormatRegistry.AMERICAN,
                confidence=0.0,
                sample_count=0,
                detected_patterns={},
                problematic_samples=[],
                currency_symbols=[]
            )
        
        # Clean and filter samples
        cleaned_samples = self._clean_samples(amount_samples)
        currency_symbols = self._extract_currency_symbols(amount_samples)
        
        # Analyze patterns for each format
        format_scores = {}
        all_patterns = {}
        
        for format_name, format_obj in self.formats.items():
            score, patterns = self._score_format_against_samples(format_obj, cleaned_samples)
            format_scores[format_name] = score
            all_patterns[format_name] = patterns
        
        # Find best format
        best_format_name = max(format_scores.keys(), key=lambda k: format_scores[k])
        best_format = self.formats[best_format_name]
        best_score = format_scores[best_format_name]
        
        # Calculate confidence based on sample size and consistency
        confidence = self._calculate_confidence(best_score, len(cleaned_samples))
        
        # Find problematic samples
        problematic = self._find_problematic_samples(best_format, cleaned_samples)
        
        return AmountFormatAnalysis(
            detected_format=best_format,
            confidence=confidence,
            sample_count=len(cleaned_samples),
            detected_patterns=all_patterns[best_format_name],
            problematic_samples=problematic,
            currency_symbols=currency_symbols
        )
    
    def get_format_confidence(self, samples: List[str], format_type: AmountFormat) -> float:
        """
        Get confidence score for a specific format against samples.
        
        Args:
            samples: List of amount strings
            format_type: AmountFormat to test against
            
        Returns:
            Confidence score (0.0 to 1.0)
        """
        if not samples:
            return 0.0
        
        cleaned_samples = self._clean_samples(samples)
        score, _ = self._score_format_against_samples(format_type, cleaned_samples)
        return self._calculate_confidence(score, len(cleaned_samples))
    
    def _clean_samples(self, samples: List[str]) -> List[str]:
        """Clean and filter amount samples."""
        cleaned = []
        for sample in samples:
            if not sample or pd.isna(sample):
                continue
            
            # Convert to string and strip whitespace
            sample_str = str(sample).strip()
            if not sample_str:
                continue
            
            # Only include samples that look like amounts
            if self.amount_pattern.search(sample_str):
                cleaned.append(sample_str)
        
        return cleaned
    
    def _extract_currency_symbols(self, samples: List[str]) -> List[str]:
        """Extract currency symbols from samples."""
        symbols = set()
        for sample in samples:
            if not sample:
                continue
            matches = self.currency_pattern.findall(str(sample))
            symbols.update(matches)
        return list(symbols)
    
    def _score_format_against_samples(self, format_obj: AmountFormat, samples: List[str]) -> Tuple[float, Dict[str, int]]:
        """
        Score how well a format matches the samples.
        
        Returns:
            Tuple of (score, pattern_counts)
        """
        if not samples:
            return 0.0, {}
        
        pattern_counts = {
            'decimal_matches': 0,
            'thousand_matches': 0,
            'negative_matches': 0,
            'valid_parses': 0,
            'total_samples': len(samples)
        }
        
        for sample in samples:
            # Test decimal separator
            if self._test_decimal_separator(sample, format_obj.decimal_separator):
                pattern_counts['decimal_matches'] += 1
            
            # Test thousand separator
            if self._test_thousand_separator(sample, format_obj.thousand_separator):
                pattern_counts['thousand_matches'] += 1
            
            # Test negative style
            if self._test_negative_style(sample, format_obj.negative_style):
                pattern_counts['negative_matches'] += 1
            
            # Test if we can parse with this format
            if self._can_parse_with_format(sample, format_obj):
                pattern_counts['valid_parses'] += 1
        
        # Calculate overall score
        total_samples = len(samples)
        decimal_score = pattern_counts['decimal_matches'] / total_samples
        thousand_score = pattern_counts['thousand_matches'] / total_samples
        negative_score = pattern_counts['negative_matches'] / total_samples
        parse_score = pattern_counts['valid_parses'] / total_samples
        
        # Weighted average (parsing success is most important)
        overall_score = (
            parse_score * 0.4 +
            decimal_score * 0.3 +
            thousand_score * 0.2 +
            negative_score * 0.1
        )
        
        return overall_score, pattern_counts
    
    def _test_decimal_separator(self, sample: str, decimal_sep: str) -> bool:
        """Test if sample uses the expected decimal separator."""
        # Look for decimal pattern: digits + separator + 1-2 digits at end
        decimal_pattern = rf'\d{re.escape(decimal_sep)}\d{{1,2}}(?:\s*[\)\-]*)?\s*$'
        return bool(re.search(decimal_pattern, sample))
    
    def _test_thousand_separator(self, sample: str, thousand_sep: str) -> bool:
        """Test if sample uses the expected thousand separator."""
        if not thousand_sep:
            # For no separator, check that there are no thousand separators
            return not re.search(r'\d[,.\s\']\d{3}', sample)
        
        # Look for thousand separator pattern
        thousand_pattern = rf'\d{re.escape(thousand_sep)}\d{{3}}'
        return bool(re.search(thousand_pattern, sample))
    
    def _test_negative_style(self, sample: str, negative_style: str) -> bool:
        """Test if sample uses the expected negative style."""
        sample = sample.strip()
        
        if negative_style == "minus":
            return sample.startswith('-') or not self._is_negative_amount(sample)
        elif negative_style == "parentheses":
            return (sample.startswith('(') and sample.endswith(')')) or not self._is_negative_amount(sample)
        elif negative_style == "suffix":
            return sample.endswith('-') or not self._is_negative_amount(sample)
        
        return True
    
    def _is_negative_amount(self, sample: str) -> bool:
        """Check if sample represents a negative amount."""
        sample = sample.strip()
        return (sample.startswith('-') or 
                sample.startswith('(') or 
                sample.endswith('-') or
                sample.endswith(')'))
    
    def _can_parse_with_format(self, sample: str, format_obj: AmountFormat) -> bool:
        """Test if we can successfully parse the sample with this format."""
        try:
            # Remove currency symbols
            cleaned = self.currency_pattern.sub('', sample).strip()
            
            # Handle negative styles
            is_negative = False
            if format_obj.negative_style == "parentheses" and cleaned.startswith('(') and cleaned.endswith(')'):
                is_negative = True
                cleaned = cleaned[1:-1].strip()
            elif format_obj.negative_style == "minus" and cleaned.startswith('-'):
                is_negative = True
                cleaned = cleaned[1:].strip()
            elif format_obj.negative_style == "suffix" and cleaned.endswith('-'):
                is_negative = True
                cleaned = cleaned[:-1].strip()
            
            # Replace thousand separators with empty string
            if format_obj.thousand_separator:
                cleaned = cleaned.replace(format_obj.thousand_separator, '')
            
            # Replace decimal separator with period
            if format_obj.decimal_separator != '.':
                cleaned = cleaned.replace(format_obj.decimal_separator, '.')
            
            # Try to convert to float
            float(cleaned)
            return True
            
        except (ValueError, AttributeError):
            return False
    
    def _calculate_confidence(self, score: float, sample_count: int) -> float:
        """Calculate confidence based on score and sample size."""
        if sample_count == 0:
            return 0.0
        
        # Base confidence from score
        confidence = score
        
        # Adjust for sample size (more samples = higher confidence)
        if sample_count >= 10:
            size_bonus = 0.1
        elif sample_count >= 5:
            size_bonus = 0.05
        else:
            size_bonus = 0.0
        
        # Penalty for very few samples
        if sample_count < 3:
            confidence *= 0.8
        
        return min(1.0, confidence + size_bonus)
    
    def _find_problematic_samples(self, format_obj: AmountFormat, samples: List[str]) -> List[str]:
        """Find samples that don't parse well with the detected format."""
        problematic = []
        for sample in samples:
            if not self._can_parse_with_format(sample, format_obj):
                problematic.append(sample)
        return problematic


# Import pandas conditionally for isna function
try:
    import pandas as pd
except ImportError:
    # Fallback if pandas is not available
    class pd:
        @staticmethod
        def isna(value):
            return value is None or (isinstance(value, float) and str(value) == 'nan')