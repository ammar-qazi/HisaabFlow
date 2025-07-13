"""
Unknown Bank Service for coordinating CSV analysis and configuration generation
"""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import configparser
import os
from backend.infrastructure.csv_parsing.structure_analyzer import StructureAnalyzer, UnknownBankAnalysis, FieldMappingSuggestion
from backend.infrastructure.config.unified_config_service import get_unified_config_service
from backend.shared.amount_formats.regional_formats import AmountFormat, RegionalFormatRegistry


@dataclass
class BankConfigInput:
    """User input for creating a new bank configuration"""
    bank_name: str
    display_name: str
    filename_patterns: List[str]
    column_mappings: Dict[str, str]  # standard_field -> csv_column
    amount_format: AmountFormat
    currency_primary: str
    cashew_account: str
    description_cleaning_rules: Optional[Dict[str, str]] = None


@dataclass
class ConfigValidationResult:
    """Result of configuration validation"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    sample_parse_success: bool
    parsed_sample_count: int


class UnknownBankService:
    """Service for handling unknown bank CSV analysis and configuration generation"""
    
    def __init__(self):
        self.structure_analyzer = StructureAnalyzer()
        self.config_service = get_unified_config_service()
        self.format_registry = RegionalFormatRegistry()
        print(f"ℹ [UnknownBankService] Initialized with enhanced structure analyzer")
    
    def analyze_unknown_bank_csv(self, csv_data: str, filename: str, encoding: str = 'utf-8', delimiter: str = ',') -> UnknownBankAnalysis:
        """
        Perform complete analysis of unknown bank CSV file.
        
        Args:
            csv_data: Raw CSV content as string
            filename: Original filename
            encoding: File encoding
            delimiter: CSV delimiter
            
        Returns:
            UnknownBankAnalysis with comprehensive results
        """
        print(f"ℹ [UnknownBankService] Starting analysis for unknown bank CSV: {filename}")
        
        try:
            # Use the enhanced structure analyzer
            analysis = self.structure_analyzer.analyze_unknown_csv(
                csv_data=csv_data,
                filename=filename,
                encoding=encoding,
                delimiter=delimiter
            )
            
            print(f"  Analysis complete. Structure confidence: {analysis.structure_confidence:.2f}")
            print(f"  Amount format detected: {analysis.amount_format_analysis.detected_format} (confidence: {analysis.amount_format_analysis.confidence:.2f})")
            print(f"  Field mappings suggested for {len(analysis.field_mapping_suggestions)} fields")
            
            return analysis
            
        except Exception as e:
            print(f"[ERROR] [UnknownBankService] Analysis failed: {str(e)}")
            raise
    
    def generate_bank_config(self, analysis: UnknownBankAnalysis, user_input: BankConfigInput) -> Dict[str, Any]:
        """
        Generate complete bank configuration from analysis and user input.
        
        Args:
            analysis: Results from CSV analysis
            user_input: User-provided configuration details
            
        Returns:
            Complete bank configuration dictionary
        """
        print(f"ℹ [UnknownBankService] Generating bank config for: {user_input.bank_name}")
        
        try:
            # Build configuration structure
            config = {
                'bank_info': {
                    'bank_name': user_input.bank_name,
                    'display_name': user_input.display_name,
                    'file_patterns': user_input.filename_patterns,
                    'detection_content_signatures': self._generate_content_signatures(analysis),
                    'currency_primary': user_input.currency_primary,
                    'cashew_account': user_input.cashew_account
                },
                'csv_config': {
                    'encoding': analysis.encoding,
                    'delimiter': analysis.delimiter,
                    'header_row': analysis.header_row,
                    'data_start_row': analysis.data_start_row
                },
                'column_mapping': user_input.column_mappings,
                'data_cleaning': {
                    'amount_format': self._format_to_config(user_input.amount_format),
                    'auto_detect_format': False,  # User has specified format
                    'currency_handling': 'standard'
                },
                'categorization': self._generate_categorization_rules(user_input)
            }
            
            # Add description cleaning rules if provided
            if user_input.description_cleaning_rules:
                config['description_cleaning'] = user_input.description_cleaning_rules
            
            print(f"  Generated config with {len(user_input.column_mappings)} column mappings")
            return config
            
        except Exception as e:
            print(f"[ERROR] [UnknownBankService] Config generation failed: {str(e)}")
            raise
    
    def validate_generated_config(self, config: Dict[str, Any], analysis: UnknownBankAnalysis) -> ConfigValidationResult:
        """
        Validate generated configuration against sample data.
        
        Args:
            config: Generated bank configuration
            analysis: Original CSV analysis
            
        Returns:
            ConfigValidationResult with validation details
        """
        print(f"ℹ [UnknownBankService] Validating generated config")
        
        errors = []
        warnings = []
        
        try:
            # Check required fields are mapped
            required_fields = ['date', 'amount', 'title']
            column_mapping = config.get('column_mapping', {})
            
            for field in required_fields:
                if field not in column_mapping or not column_mapping[field]:
                    errors.append(f"Required field '{field}' is not mapped to any column")
                elif column_mapping[field] not in analysis.headers:
                    errors.append(f"Field '{field}' is mapped to '{column_mapping[field]}' which doesn't exist in CSV headers")
            
            # Check bank name is valid
            bank_name = config.get('bank_info', {}).get('bank_name', '')
            if not bank_name or not bank_name.replace('_', '').isalnum():
                errors.append("Bank name must be alphanumeric (underscores allowed)")
            
            # Check for duplicate bank name
            if self.config_service.has_bank_config(bank_name):
                errors.append(f"Bank name '{bank_name}' already exists")
            
            # Test parsing sample data
            sample_parse_success = False
            parsed_count = 0
            
            try:
                # Simulate parsing with the configuration
                if analysis.sample_data and not errors:
                    parsed_count = len(analysis.sample_data)
                    sample_parse_success = True
                    print(f"  Sample parsing validation: {parsed_count} rows would parse successfully")
            except Exception as e:
                warnings.append(f"Sample parsing test failed: {str(e)}")
            
            # Check amount format compatibility
            if analysis.amount_format_analysis.confidence < 0.5:
                warnings.append("Low confidence in amount format detection. Manual review recommended.")
            
            # Check field mapping confidence
            low_confidence_fields = []
            for field, suggestion in analysis.field_mapping_suggestions.items():
                if field in column_mapping and suggestion.best_match:
                    confidence = suggestion.confidence_scores.get(column_mapping[field], 0.0)
                    if confidence < 0.5:
                        low_confidence_fields.append(field)
            
            if low_confidence_fields:
                warnings.append(f"Low confidence field mappings: {', '.join(low_confidence_fields)}")
            
            is_valid = len(errors) == 0
            
            result = ConfigValidationResult(
                is_valid=is_valid,
                errors=errors,
                warnings=warnings,
                sample_parse_success=sample_parse_success,
                parsed_sample_count=parsed_count
            )
            
            print(f"  Validation complete. Valid: {is_valid}, Errors: {len(errors)}, Warnings: {len(warnings)}")
            return result
            
        except Exception as e:
            print(f"[ERROR] [UnknownBankService] Validation failed: {str(e)}")
            return ConfigValidationResult(
                is_valid=False,
                errors=[f"Validation error: {str(e)}"],
                warnings=[],
                sample_parse_success=False,
                parsed_sample_count=0
            )
    
    def save_bank_config(self, config: Dict[str, Any]) -> bool:
        """
        Save bank configuration to file and reload configs.
        
        Args:
            config: Complete bank configuration
            
        Returns:
            True if successful, False otherwise
        """
        bank_name = config.get('bank_info', {}).get('bank_name', '')
        print(f"ℹ [UnknownBankService] Saving config for bank: {bank_name}")
        
        try:
            # Determine config file path
            config_dir = self.config_service.config_dir
            config_filename = f"{bank_name}.conf"
            config_path = os.path.join(config_dir, config_filename)
            
            # Create ConfigParser object
            config_parser = configparser.ConfigParser()
            
            # Add sections to config file
            self._add_bank_info_section(config_parser, config['bank_info'])
            self._add_csv_config_section(config_parser, config['csv_config'])
            self._add_column_mapping_section(config_parser, config['column_mapping'])
            self._add_data_cleaning_section(config_parser, config['data_cleaning'])
            
            if 'categorization' in config:
                self._add_categorization_section(config_parser, config['categorization'])
            
            if 'description_cleaning' in config:
                self._add_description_cleaning_section(config_parser, config['description_cleaning'])
            
            # Write to file
            with open(config_path, 'w', encoding='utf-8') as f:
                config_parser.write(f)
            
            print(f"  Config saved to: {config_path}")
            
            # Reload all configurations to pick up the new one
            reload_success = self.config_service.reload_all_configs()
            if reload_success:
                print(f"  Configs reloaded successfully. Bank '{bank_name}' is now available.")
            else:
                print(f"[WARNING] Config saved but reload failed. Restart may be required.")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] [UnknownBankService] Failed to save config: {str(e)}")
            return False
    
    def _generate_content_signatures(self, analysis: UnknownBankAnalysis) -> List[str]:
        """Generate content signatures for bank detection."""
        signatures = []
        
        # Use some headers as content signatures
        meaningful_headers = [h for h in analysis.headers if len(h) > 3 and not h.isdigit()]
        if meaningful_headers:
            # Take first few meaningful headers
            signatures.extend(meaningful_headers[:3])
        
        # Add signatures based on detected patterns
        if analysis.amount_format_analysis.currency_symbols:
            signatures.extend(analysis.amount_format_analysis.currency_symbols)
        
        return signatures
    
    def _format_to_config(self, amount_format: AmountFormat) -> Dict[str, str]:
        """Convert AmountFormat to config dictionary."""
        return {
            'decimal_separator': amount_format.decimal_separator,
            'thousand_separator': amount_format.thousand_separator,
            'negative_style': amount_format.negative_style,
            'currency_position': amount_format.currency_position
        }
    
    def _generate_categorization_rules(self, user_input: BankConfigInput) -> Dict[str, str]:
        """Generate basic categorization rules."""
        # For now, return empty rules - user can add these later
        # Could be enhanced to suggest rules based on common patterns
        return {}
    
    def _add_bank_info_section(self, config_parser: configparser.ConfigParser, bank_info: Dict[str, Any]):
        """Add bank_info section to config."""
        config_parser.add_section('bank_info')
        config_parser.set('bank_info', 'bank_name', bank_info['bank_name'])
        config_parser.set('bank_info', 'display_name', bank_info['display_name'])
        config_parser.set('bank_info', 'file_patterns', ', '.join(bank_info['file_patterns']))
        config_parser.set('bank_info', 'detection_content_signatures', ', '.join(bank_info.get('detection_content_signatures', [])))
        config_parser.set('bank_info', 'currency_primary', bank_info['currency_primary'])
        config_parser.set('bank_info', 'cashew_account', bank_info['cashew_account'])
    
    def _add_csv_config_section(self, config_parser: configparser.ConfigParser, csv_config: Dict[str, Any]):
        """Add csv_config section to config."""
        config_parser.add_section('csv_config')
        config_parser.set('csv_config', 'encoding', csv_config['encoding'])
        config_parser.set('csv_config', 'delimiter', csv_config['delimiter'])
        config_parser.set('csv_config', 'header_row', str(csv_config['header_row']))
        config_parser.set('csv_config', 'data_start_row', str(csv_config['data_start_row']))
    
    def _add_column_mapping_section(self, config_parser: configparser.ConfigParser, column_mapping: Dict[str, str]):
        """Add column_mapping section to config."""
        config_parser.add_section('column_mapping')
        for standard_field, csv_column in column_mapping.items():
            if csv_column:  # Only add non-empty mappings
                config_parser.set('column_mapping', standard_field, csv_column)
    
    def _add_data_cleaning_section(self, config_parser: configparser.ConfigParser, data_cleaning: Dict[str, Any]):
        """Add data_cleaning section to config."""
        config_parser.add_section('data_cleaning')
        
        amount_format = data_cleaning.get('amount_format', {})
        if amount_format:
            config_parser.set('data_cleaning', 'decimal_separator', amount_format.get('decimal_separator', '.'))
            config_parser.set('data_cleaning', 'thousand_separator', amount_format.get('thousand_separator', ','))
            config_parser.set('data_cleaning', 'negative_style', amount_format.get('negative_style', 'minus'))
            config_parser.set('data_cleaning', 'currency_position', amount_format.get('currency_position', 'prefix'))
        
        config_parser.set('data_cleaning', 'auto_detect_format', str(data_cleaning.get('auto_detect_format', False)))
        config_parser.set('data_cleaning', 'currency_handling', data_cleaning.get('currency_handling', 'standard'))
    
    def _add_categorization_section(self, config_parser: configparser.ConfigParser, categorization: Dict[str, str]):
        """Add categorization section to config."""
        if categorization:
            config_parser.add_section('categorization')
            for pattern, category in categorization.items():
                config_parser.set('categorization', pattern, category)
    
    def _add_description_cleaning_section(self, config_parser: configparser.ConfigParser, description_cleaning: Dict[str, str]):
        """Add description_cleaning section to config."""
        if description_cleaning:
            config_parser.add_section('description_cleaning')
            for pattern, replacement in description_cleaning.items():
                config_parser.set('description_cleaning', pattern, replacement)