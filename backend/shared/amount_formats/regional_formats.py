"""
Regional Amount Format Definitions

Defines AmountFormat dataclass and regional format specifications for different
international number formatting conventions.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class AmountFormat:
    """
    Represents a specific amount formatting convention.
    
    Attributes:
        decimal_separator: Character used for decimal separation ("." or ",")
        thousand_separator: Character used for thousand grouping (",", ".", " ", "'", or "")
        negative_style: How negative numbers are represented ("minus", "parentheses", "suffix")
        currency_position: Where currency symbol appears ("prefix", "suffix", "none")
        grouping_pattern: List of digits for grouping ([3] standard, [3,2] Indian)
        name: Human-readable name for this format
        example: Example of formatted number using this format
    """
    decimal_separator: str
    thousand_separator: str
    negative_style: str = "minus"
    currency_position: str = "prefix"
    grouping_pattern: List[int] = field(default_factory=lambda: [3])
    name: str = ""
    example: str = ""
    
    def __post_init__(self):
        """Validate format parameters after initialization."""
        if self.decimal_separator not in [".", ","]:
            raise ValueError(f"Invalid decimal separator: {self.decimal_separator}")
        
        if self.thousand_separator not in ["", ",", ".", " ", "'"]:
            raise ValueError(f"Invalid thousand separator: {self.thousand_separator}")
        
        if self.negative_style not in ["minus", "parentheses", "suffix"]:
            raise ValueError(f"Invalid negative style: {self.negative_style}")
        
        if self.currency_position not in ["prefix", "suffix", "none"]:
            raise ValueError(f"Invalid currency position: {self.currency_position}")
        
        # Ensure decimal and thousand separators are different
        if self.decimal_separator == self.thousand_separator and self.thousand_separator != "":
            raise ValueError("Decimal and thousand separators cannot be the same")


class RegionalFormatRegistry:
    """
    Registry of predefined regional amount formats.
    
    Contains common international number formatting conventions used by
    different countries and regions.
    """
    
    AMERICAN = AmountFormat(
        decimal_separator=".",
        thousand_separator=",",
        negative_style="minus",
        currency_position="prefix",
        grouping_pattern=[3],
        name="American",
        example="$1,234.56"
    )
    
    EUROPEAN = AmountFormat(
        decimal_separator=",",
        thousand_separator=".",
        negative_style="minus",
        currency_position="suffix",
        grouping_pattern=[3],
        name="European",
        example="1.234,56 €"
    )
    
    SPACE_SEPARATED = AmountFormat(
        decimal_separator=",",
        thousand_separator=" ",
        negative_style="minus",
        currency_position="suffix",
        grouping_pattern=[3],
        name="Space Separated",
        example="1 234,56 €"
    )
    
    INDIAN = AmountFormat(
        decimal_separator=".",
        thousand_separator=",",
        negative_style="minus",
        currency_position="prefix",
        grouping_pattern=[3, 2],  # Last group is 3, others are 2
        name="Indian",
        example="₹1,23,456.78"
    )
    
    SWISS = AmountFormat(
        decimal_separator=".",
        thousand_separator="'",
        negative_style="minus",
        currency_position="prefix",
        grouping_pattern=[3],
        name="Swiss",
        example="CHF 1'234.56"
    )
    
    NO_SEPARATOR = AmountFormat(
        decimal_separator=".",
        thousand_separator="",
        negative_style="minus",
        currency_position="prefix",
        grouping_pattern=[],
        name="No Separator",
        example="$1234.56"
    )
    
    PARENTHESES_NEGATIVE = AmountFormat(
        decimal_separator=".",
        thousand_separator=",",
        negative_style="parentheses",
        currency_position="prefix",
        grouping_pattern=[3],
        name="Parentheses Negative",
        example="($1,234.56)"
    )
    
    @classmethod
    def get_all_formats(cls) -> Dict[str, AmountFormat]:
        """Get all predefined formats as a dictionary."""
        return {
            "american": cls.AMERICAN,
            "european": cls.EUROPEAN,
            "space_separated": cls.SPACE_SEPARATED,
            "indian": cls.INDIAN,
            "swiss": cls.SWISS,
            "no_separator": cls.NO_SEPARATOR,
            "parentheses_negative": cls.PARENTHESES_NEGATIVE
        }
    
    @classmethod
    def get_format_by_name(cls, name: str) -> AmountFormat:
        """Get format by name, case-insensitive."""
        formats = cls.get_all_formats()
        return formats.get(name.lower())
    
    @classmethod
    def get_format_names(cls) -> List[str]:
        """Get list of all format names."""
        return list(cls.get_all_formats().keys())
    
    @classmethod
    def is_valid_format_name(cls, name: str) -> bool:
        """Check if a format name is valid."""
        return name.lower() in cls.get_all_formats()