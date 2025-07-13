"""
Format Registry

Provides a centralized registry for managing and accessing amount formats with utilities
for format lookup, conversion, and serialization.
"""

from typing import Dict, List, Optional, Any
from .regional_formats import AmountFormat, RegionalFormatRegistry
from .format_validators import FormatValidator
from .amount_format_detector import AmountFormatDetector


class FormatRegistry:
    """
    Centralized registry for amount formats with extended functionality.
    
    Provides utilities for format management, serialization, and conversion
    between different format representations.
    """
    
    def __init__(self):
        self.validator = FormatValidator()
        self.detector = AmountFormatDetector()
        self._custom_formats: Dict[str, AmountFormat] = {}
    
    @property
    def predefined_formats(self) -> Dict[str, AmountFormat]:
        """Get all predefined regional formats."""
        return RegionalFormatRegistry.get_all_formats()
    
    @property
    def all_formats(self) -> Dict[str, AmountFormat]:
        """Get all formats (predefined + custom)."""
        formats = self.predefined_formats.copy()
        formats.update(self._custom_formats)
        return formats
    
    def get_format(self, name: str) -> Optional[AmountFormat]:
        """
        Get format by name (case-insensitive).
        
        Args:
            name: Format name to lookup
            
        Returns:
            AmountFormat object or None if not found
        """
        name_lower = name.lower()
        
        # Check predefined formats first
        predefined = self.predefined_formats
        if name_lower in predefined:
            return predefined[name_lower]
        
        # Check custom formats
        if name_lower in self._custom_formats:
            return self._custom_formats[name_lower]
        
        return None
    
    def register_custom_format(self, name: str, format_obj: AmountFormat) -> bool:
        """
        Register a custom format.
        
        Args:
            name: Unique name for the format
            format_obj: AmountFormat object
            
        Returns:
            True if registered successfully, False if validation failed
        """
        # Validate the format
        validation = self.validator.validate_format(format_obj)
        if not validation.is_valid:
            print(f"[ERROR] Cannot register format '{name}': {'; '.join(validation.errors)}")
            return False
        
        # Register the format
        self._custom_formats[name.lower()] = format_obj
        print(f"[INFO] Registered custom format: {name}")
        return True
    
    def unregister_custom_format(self, name: str) -> bool:
        """
        Unregister a custom format.
        
        Args:
            name: Name of format to remove
            
        Returns:
            True if removed, False if not found
        """
        name_lower = name.lower()
        if name_lower in self._custom_formats:
            del self._custom_formats[name_lower]
            print(f"[INFO] Unregistered custom format: {name}")
            return True
        return False
    
    def get_format_names(self) -> List[str]:
        """Get list of all available format names."""
        return list(self.all_formats.keys())
    
    def detect_format_from_samples(self, samples: List[str]) -> Dict[str, Any]:
        """
        Detect format from sample data with detailed results.
        
        Args:
            samples: List of amount strings to analyze
            
        Returns:
            Dictionary with detection results
        """
        analysis = self.detector.analyze_amount_column(samples)
        
        return {
            'detected_format': analysis.detected_format,
            'format_name': self._get_format_name(analysis.detected_format),
            'confidence': analysis.confidence,
            'sample_count': analysis.sample_count,
            'patterns': analysis.detected_patterns,
            'problematic_samples': analysis.problematic_samples,
            'currency_symbols': analysis.currency_symbols
        }
    
    def validate_format_with_samples(self, format_name: str, samples: List[str]) -> Dict[str, Any]:
        """
        Validate a specific format against sample data.
        
        Args:
            format_name: Name of format to validate
            samples: Sample data to validate against
            
        Returns:
            Dictionary with validation results
        """
        format_obj = self.get_format(format_name)
        if not format_obj:
            return {
                'is_valid': False,
                'error': f"Format '{format_name}' not found"
            }
        
        validation = self.validator.validate_format_with_samples(format_obj, samples)
        
        return {
            'is_valid': validation.is_valid,
            'confidence': validation.confidence,
            'errors': validation.errors,
            'warnings': validation.warnings,
            'sample_successes': validation.sample_successes,
            'sample_failures': validation.sample_failures,
            'failed_samples': validation.failed_samples
        }
    
    def convert_format_to_dict(self, format_obj: AmountFormat) -> Dict[str, Any]:
        """
        Convert AmountFormat to dictionary for serialization.
        
        Args:
            format_obj: AmountFormat to convert
            
        Returns:
            Dictionary representation
        """
        return {
            'decimal_separator': format_obj.decimal_separator,
            'thousand_separator': format_obj.thousand_separator,
            'negative_style': format_obj.negative_style,
            'currency_position': format_obj.currency_position,
            'grouping_pattern': format_obj.grouping_pattern,
            'name': format_obj.name,
            'example': format_obj.example
        }
    
    def create_format_from_dict(self, format_dict: Dict[str, Any]) -> Optional[AmountFormat]:
        """
        Create AmountFormat from dictionary.
        
        Args:
            format_dict: Dictionary with format parameters
            
        Returns:
            AmountFormat object or None if invalid
        """
        try:
            return AmountFormat(
                decimal_separator=format_dict.get('decimal_separator', '.'),
                thousand_separator=format_dict.get('thousand_separator', ','),
                negative_style=format_dict.get('negative_style', 'minus'),
                currency_position=format_dict.get('currency_position', 'prefix'),
                grouping_pattern=format_dict.get('grouping_pattern', [3]),
                name=format_dict.get('name', ''),
                example=format_dict.get('example', '')
            )
        except (ValueError, TypeError) as e:
            print(f"[ERROR] Failed to create format from dict: {e}")
            return None
    
    def get_compatible_formats(self, samples: List[str], min_confidence: float = 0.5) -> List[Dict[str, Any]]:
        """
        Get all formats compatible with the given samples.
        
        Args:
            samples: Sample data to test against
            min_confidence: Minimum confidence threshold
            
        Returns:
            List of compatible formats with confidence scores
        """
        compatible = []
        
        for name, format_obj in self.all_formats.items():
            confidence = self.detector.get_format_confidence(samples, format_obj)
            if confidence >= min_confidence:
                compatible.append({
                    'name': name,
                    'format': format_obj,
                    'confidence': confidence
                })
        
        # Sort by confidence (highest first)
        compatible.sort(key=lambda x: x['confidence'], reverse=True)
        return compatible
    
    def suggest_format_for_samples(self, samples: List[str]) -> Dict[str, Any]:
        """
        Suggest the best format for given samples with alternatives.
        
        Args:
            samples: Sample data to analyze
            
        Returns:
            Dictionary with primary suggestion and alternatives
        """
        detection_result = self.detect_format_from_samples(samples)
        compatible_formats = self.get_compatible_formats(samples, min_confidence=0.3)
        
        return {
            'primary_suggestion': {
                'format': detection_result['detected_format'],
                'name': detection_result['format_name'],
                'confidence': detection_result['confidence']
            },
            'alternatives': compatible_formats[1:4],  # Top 3 alternatives
            'sample_analysis': {
                'total_samples': detection_result['sample_count'],
                'problematic_samples': detection_result['problematic_samples'],
                'detected_currencies': detection_result['currency_symbols']
            }
        }
    
    def _get_format_name(self, format_obj: AmountFormat) -> str:
        """Get the name of a format object."""
        # Check predefined formats
        for name, predefined_format in self.predefined_formats.items():
            if self._formats_equal(format_obj, predefined_format):
                return name
        
        # Check custom formats
        for name, custom_format in self._custom_formats.items():
            if self._formats_equal(format_obj, custom_format):
                return name
        
        # Return a generated name if not found
        return f"custom_{format_obj.decimal_separator}_{format_obj.thousand_separator}"
    
    def _formats_equal(self, format1: AmountFormat, format2: AmountFormat) -> bool:
        """Check if two formats are equal."""
        return (
            format1.decimal_separator == format2.decimal_separator and
            format1.thousand_separator == format2.thousand_separator and
            format1.negative_style == format2.negative_style and
            format1.currency_position == format2.currency_position and
            format1.grouping_pattern == format2.grouping_pattern
        )