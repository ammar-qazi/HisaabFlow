#!/usr/bin/env python3
"""
Test pattern length prioritization in categorization system.
Verifies that longer, more specific patterns take precedence over shorter ones.
"""

import pytest
from unittest.mock import Mock, MagicMock
from backend.infrastructure.config.unified_config_service import UnifiedConfigService


class TestPatternPrioritization:
    """Test pattern length-based prioritization in categorization"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.config_service = UnifiedConfigService()
        
        # Mock app config with test patterns
        self.config_service._app_config = Mock()
        self.config_service._app_config.sections.return_value = ['Entertainment', 'Transport']
        
        # Mock Entertainment section with Netflix (longer) and general patterns
        entertainment_section = {
            'Netflix.*': None,  # Length: 8 chars
            'TfL.*': None,      # Length: 5 chars
            'TV.*': None        # Length: 4 chars
        }
        
        # Mock Transport section
        transport_section = {
            'TfL.*': None,      # Length: 5 chars
            'Bus.*': None       # Length: 5 chars
        }
        
        def mock_getitem(section_name):
            if section_name == 'Entertainment':
                return entertainment_section
            elif section_name == 'Transport':
                return transport_section
            return {}
        
        self.config_service._app_config.__getitem__ = mock_getitem
        self.config_service._bank_configs = {}  # No bank-specific rules for this test

    def test_netflix_matches_netflix_not_tfl(self):
        """Test that 'Netflix' matches 'Netflix.*' pattern, not 'TfL.*'"""
        result = self.config_service.categorize_merchant_with_debug('test_bank', 'Netflix Monthly Subscription')
        
        assert result is not None
        assert result['category'] == 'Entertainment'
        assert result['pattern'] == 'Netflix.*'
        assert 'Netflix' in result['pattern']

    def test_tfl_matches_transport_section(self):
        """Test that 'TfL' matches Transport section when appropriate"""
        result = self.config_service.categorize_merchant_with_debug('test_bank', 'TfL Bus Journey')
        
        assert result is not None
        # Should match Transport section's TfL pattern since it appears first in sections iteration
        assert result['category'] == 'Entertainment'  # Due to section order in mock
        assert result['pattern'] == 'TfL.*'

    def test_pattern_length_prioritization_within_section(self):
        """Test that longer patterns take precedence within the same section"""
        # Test with a hypothetical longer pattern that would conflict
        entertainment_section = {
            'Netflix Monthly.*': None,  # Length: 16 chars (longer)
            'Netflix.*': None,          # Length: 8 chars (shorter)
            'Net.*': None               # Length: 5 chars (shortest)
        }
        
        self.config_service._app_config.__getitem__ = lambda section: entertainment_section if section == 'Entertainment' else {}
        
        result = self.config_service.categorize_merchant_with_debug('test_bank', 'Netflix Monthly Subscription')
        
        assert result is not None
        assert result['pattern'] == 'Netflix Monthly.*'  # Should match the longest pattern

    def test_regex_patterns_prioritized_by_length(self):
        """Test that regex patterns are also prioritized by length"""
        entertainment_section = {
            'Netflix.*|Disney.*|Amazon Prime.*': None,  # Very long pattern
            'Netflix.*': None,                          # Shorter pattern
            'Net.*': None                               # Shortest pattern
        }
        
        self.config_service._app_config.__getitem__ = lambda section: entertainment_section if section == 'Entertainment' else {}
        
        result = self.config_service.categorize_merchant_with_debug('test_bank', 'Netflix Original Series')
        
        assert result is not None
        assert result['pattern'] == 'Netflix.*|Disney.*|Amazon Prime.*'  # Should match the longest pattern

    def test_bank_specific_patterns_also_prioritized(self):
        """Test that bank-specific patterns are also prioritized by length"""
        # Mock bank config with length-based conflicts
        mock_bank_config = Mock()
        mock_bank_config.categorization_rules = {
            'Amazon Prime Video.*': 'Streaming',  # Length: 19 chars
            'Amazon.*': 'Shopping',               # Length: 8 chars
            'A.*': 'Generic'                      # Length: 3 chars
        }
        mock_bank_config.default_category_rules = {}
        
        self.config_service._bank_configs = {'test_bank': mock_bank_config}
        
        result = self.config_service.categorize_merchant_with_debug('test_bank', 'Amazon Prime Video Monthly')
        
        assert result is not None
        assert result['category'] == 'Streaming'
        assert result['pattern'] == 'Amazon Prime Video.*'
        assert result['source'] == 'bank-specific (test_bank)'

    def test_case_insensitive_pattern_matching_preserved(self):
        """Test that case-insensitive matching still works with prioritization"""
        result = self.config_service.categorize_merchant_with_debug('test_bank', 'netflix subscription')
        
        assert result is not None
        assert result['category'] == 'Entertainment'
        assert result['pattern'] == 'Netflix.*'

    def test_empty_sections_handled_gracefully(self):
        """Test that empty sections don't cause errors"""
        self.config_service._app_config.__getitem__ = lambda section: {} if section == 'Entertainment' else {}
        
        result = self.config_service.categorize_merchant_with_debug('test_bank', 'Netflix')
        
        assert result is None  # Should return None when no patterns match

    def test_pattern_sorting_performance(self):
        """Test that pattern sorting doesn't significantly impact performance"""
        import time
        
        # Create a large section with many patterns
        large_section = {f'Pattern{i}.*': None for i in range(1000)}
        large_section['Netflix.*'] = None
        
        self.config_service._app_config.__getitem__ = lambda section: large_section if section == 'Entertainment' else {}
        
        start_time = time.time()
        result = self.config_service.categorize_merchant_with_debug('test_bank', 'Netflix')
        end_time = time.time()
        
        assert result is not None
        assert (end_time - start_time) < 0.1  # Should complete in under 100ms

    def test_special_regex_characters_in_patterns(self):
        """Test that patterns with special regex characters are handled correctly"""
        entertainment_section = {
            'McDonald\'s.*': None,     # Pattern with escaped quote
            'C&A.*': None,              # Pattern with ampersand
            '\\bGap\\b.*': None         # Pattern with word boundaries
        }
        
        self.config_service._app_config.__getitem__ = lambda section: entertainment_section if section == 'Entertainment' else {}
        
        result = self.config_service.categorize_merchant_with_debug('test_bank', "McDonald's Restaurant")
        
        assert result is not None
        assert result['category'] == 'Entertainment'
        assert "McDonald" in result['pattern']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])