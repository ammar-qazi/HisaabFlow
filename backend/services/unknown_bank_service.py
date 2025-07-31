"""
Unknown Bank Service for coordinating CSV analysis and configuration generation
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import configparser
import os
from pandas.tseries.api import guess_datetime_format
from collections import Counter
from backend.infrastructure.csv_parsing.structure_analyzer import (
    StructureAnalyzer,
    UnknownBankAnalysis,
    FieldMappingSuggestion,
)
from backend.infrastructure.config.unified_config_service import (
    get_unified_config_service,
)
from backend.shared.amount_formats.regional_formats import (
    AmountFormat,
    RegionalFormatRegistry,
)


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
    date_format: Optional[str] = None  # Custom date format pattern
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

    def analyze_unknown_bank_csv(
        self, file_path: str, filename: str, header_row: Optional[int] = None
    ) -> UnknownBankAnalysis:
        """
        Perform complete analysis of unknown bank CSV file.

        Args:
            file_path: Path to the CSV file to analyze
            filename: Original filename

        Returns:
            UnknownBankAnalysis with comprehensive results
        """
        print(
            f"ℹ [UnknownBankService] Starting analysis for unknown bank CSV: {filename}"
        )
        print(f"ℹ [UnknownBankService] Header row parameter: {header_row}")

        try:
            # Use the UnifiedCSVParser to handle all file operations
            from backend.infrastructure.csv_parsing.unified_parser import (
                UnifiedCSVParser,
            )

            parser = UnifiedCSVParser()

            # This call will handle encoding, dialect, and parsing
            # For unknown bank analysis, we want to bypass UnifiedCSVParser's header detection
            # and get all raw rows to let StructureAnalyzer do proper header detection
            if header_row is None:
                # Initial upload - get all raw rows without header processing
                print(
                    f"🔍 [DEBUG] Getting all raw rows for StructureAnalyzer to analyze"
                )
                parsing_result = parser.parse_csv(
                    file_path, encoding=None, header_row=None, start_row=None
                )
            else:
                # Re-analysis with specific header row - use our calculations
                parser_header_row = header_row - 1  # Convert 1-based to 0-based
                start_row = parser_header_row + 1
                print(
                    f"🔍 [DEBUG] Using specific header_row: {header_row} -> parser_header_row={parser_header_row} -> start_row={start_row}"
                )
                parsing_result = parser.parse_csv(
                    file_path,
                    encoding=None,
                    header_row=parser_header_row,
                    start_row=start_row,
                )
            print(f"🔍 [DEBUG] Parsing result success: {parsing_result.get('success')}")

            if not parsing_result.get("success"):
                raise Exception(f"Parsing failed: {parsing_result.get('error')}")

            # Extract the parsed data and metadata for analysis
            raw_rows = parsing_result.get("raw_rows", [])
            # Get encoding from metadata if available, fallback to utf-8
            metadata = parsing_result.get("metadata", {})
            encoding_detection = metadata.get("encoding_detection", {})
            detected_encoding = encoding_detection.get("encoding", "utf-8")
            print(f"  DEBUG: UnknownBankService - Metadata: {metadata}")
            print(
                f"  DEBUG: UnknownBankService - Encoding detection: {encoding_detection}"
            )
            print(
                f"  DEBUG: UnknownBankService - Detected encoding: {detected_encoding}"
            )
            # Get delimiter from metadata
            dialect_detection = metadata.get("dialect_detection", {})
            detected_delimiter = dialect_detection.get("delimiter", ",")

            # Convert raw_rows to CSV data string for the structure analyzer
            # (maintaining compatibility with existing StructureAnalyzer interface)
            if raw_rows:
                import csv
                import io

                output = io.StringIO()
                writer = csv.writer(output, delimiter=detected_delimiter)
                for row in raw_rows:
                    writer.writerow(row)
                csv_data = output.getvalue()
            else:
                csv_data = ""

            # For unknown bank analysis, read the file directly to avoid parsing issues
            # that can occur with complex line terminators in UnifiedCSVParser
            if header_row is None:
                print(f"🔍 [DEBUG] Reading file directly for unknown bank analysis")
                with open(file_path, "r", encoding=detected_encoding) as f:
                    csv_data = f.read()
                # Pass header_row for auto-detection
                analyzer_header_row = header_row
            else:
                # When user specifies header_row, read file directly and pass the user's choice
                # This ensures the user's header row selection is respected
                print(
                    f"🔍 [DEBUG] Reading file directly to respect user's header row choice: {header_row}"
                )
                with open(file_path, "r", encoding=detected_encoding) as f:
                    csv_data = f.read()
                # Pass 1-based header_row directly to analyzer (it will convert to 0-based internally)
                analyzer_header_row = header_row
                print(
                    f"🔍 [DEBUG] Passing header_row {header_row} (1-based) to analyzer"
                )

            # Now, use the parsed data to perform the analysis
            analysis = self.structure_analyzer.analyze_unknown_csv(
                csv_data=csv_data,
                filename=filename,
                encoding=detected_encoding,
                delimiter=detected_delimiter,
                header_row=analyzer_header_row,
            )

            # Add date format detection using pandas
            date_format_info = self._detect_date_format(analysis)
            if date_format_info:
                # Store the detected format information in the analysis results
                if not hasattr(analysis, "additional_metadata"):
                    analysis.additional_metadata = {}
                analysis.additional_metadata["date_format_info"] = date_format_info
                print(f"  Date format detected: {date_format_info.get('detected_format')}")

            print(
                f"  DEBUG: UnknownBankService - Analysis object encoding: {analysis.encoding}"
            )
            print(
                f"  Analysis complete. Structure confidence: {analysis.structure_confidence:.2f}"
            )
            print(
                f"  Amount format detected: {analysis.amount_format_analysis.detected_format} (confidence: {analysis.amount_format_analysis.confidence:.2f})"
            )
            print(
                f"  Field mappings suggested for {len(analysis.field_mapping_suggestions)} fields"
            )

            return analysis

        except Exception as e:
            print(f"[ERROR] [UnknownBankService] Analysis failed: {str(e)}")
            raise

    def generate_bank_config(
        self, analysis: UnknownBankAnalysis, user_input: BankConfigInput
    ) -> Dict[str, Any]:
        """
        Generate complete bank configuration from analysis and user input.

        Args:
            analysis: Results from CSV analysis
            user_input: User-provided configuration details

        Returns:
            Complete bank configuration dictionary
        """
        print(
            f"ℹ [UnknownBankService] Generating bank config for: {user_input.bank_name}"
        )

        try:
            # Build configuration structure
            csv_config = {
                "encoding": analysis.encoding,
                "delimiter": analysis.delimiter,
                "header_row": analysis.header_row
                + 1,  # Convert to 1-based for config file
                "has_header": True,
                "skip_rows": 0,
            }

            # Add date format - prioritize user input over detected format
            if user_input.date_format:
                csv_config["date_format"] = user_input.date_format
            elif hasattr(
                analysis, "additional_metadata"
            ) and analysis.additional_metadata.get("date_format_info"):
                date_format_info = analysis.additional_metadata["date_format_info"]
                csv_config["date_format"] = date_format_info.get("detected_format")

            config = {
                "bank_info": {
                    "name": user_input.bank_name,
                    "display_name": user_input.display_name,
                    "file_patterns": user_input.filename_patterns,
                    "detection_content_signatures": self._generate_content_signatures(
                        analysis
                    ),
                    "expected_headers": analysis.headers,
                    "currency_primary": user_input.currency_primary,
                    "cashew_account": user_input.cashew_account,
                },
                "csv_config": csv_config,
                "column_mapping": user_input.column_mappings,
                "data_cleaning": {
                    "amount_format": self._format_to_config(user_input.amount_format),
                    "auto_detect_format": False,  # User has specified format
                    "currency_handling": "standard",
                },
                "categorization": self._generate_categorization_rules(user_input),
                "default_category_rules": self._generate_default_category_rules(),
                "outgoing_patterns": {},
                "incoming_patterns": {},
            }

            # Add description cleaning rules if provided
            if user_input.description_cleaning_rules:
                config["description_cleaning"] = user_input.description_cleaning_rules

            print(
                f"  Generated config with {len(user_input.column_mappings)} column mappings"
            )
            return config

        except Exception as e:
            print(f"[ERROR] [UnknownBankService] Config generation failed: {str(e)}")
            raise

    def validate_generated_config(
        self, config: Dict[str, Any], analysis: UnknownBankAnalysis
    ) -> ConfigValidationResult:
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
            column_mapping = config.get("column_mapping", {})

            # Always require date and title
            basic_required_fields = ["date", "title"]
            for field in basic_required_fields:
                if field not in column_mapping or not column_mapping[field]:
                    errors.append(
                        f"Required field '{field}' is not mapped to any column"
                    )
                elif column_mapping[field] not in analysis.headers:
                    errors.append(
                        f"Field '{field}' is mapped to '{column_mapping[field]}' which doesn't exist in CSV headers"
                    )

            # Check amount field requirements - either amount OR (debit and/or credit)
            has_amount = column_mapping.get("amount")
            has_debit = column_mapping.get("debit")
            has_credit = column_mapping.get("credit")

            if not has_amount and not has_debit and not has_credit:
                errors.append(
                    "At least one amount field must be mapped: either 'amount' or 'debit'/'credit'"
                )

            # Validate that mapped columns exist in headers
            for field in ["amount", "debit", "credit"]:
                if (
                    field in column_mapping
                    and column_mapping[field]
                    and column_mapping[field] not in analysis.headers
                ):
                    errors.append(
                        f"Field '{field}' is mapped to '{column_mapping[field]}' which doesn't exist in CSV headers"
                    )

            # Check bank name is valid
            bank_name = config.get("bank_info", {}).get("name", "")
            if not bank_name or not bank_name.replace("_", "").isalnum():
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
                    print(
                        f"  Sample parsing validation: {parsed_count} rows would parse successfully"
                    )
            except Exception as e:
                warnings.append(f"Sample parsing test failed: {str(e)}")

            # Check amount format compatibility
            if analysis.amount_format_analysis.confidence < 0.5:
                warnings.append(
                    "Low confidence in amount format detection. Manual review recommended."
                )

            # Check field mapping confidence
            low_confidence_fields = []
            for field, suggestion in analysis.field_mapping_suggestions.items():
                if field in column_mapping and suggestion.best_match:
                    confidence = suggestion.confidence_scores.get(
                        column_mapping[field], 0.0
                    )
                    if confidence < 0.5:
                        low_confidence_fields.append(field)

            if low_confidence_fields:
                warnings.append(
                    f"Low confidence field mappings: {', '.join(low_confidence_fields)}"
                )

            is_valid = len(errors) == 0

            result = ConfigValidationResult(
                is_valid=is_valid,
                errors=errors,
                warnings=warnings,
                sample_parse_success=sample_parse_success,
                parsed_sample_count=parsed_count,
            )

            print(
                f"  Validation complete. Valid: {is_valid}, Errors: {len(errors)}, Warnings: {len(warnings)}"
            )
            return result

        except Exception as e:
            print(f"[ERROR] [UnknownBankService] Validation failed: {str(e)}")
            return ConfigValidationResult(
                is_valid=False,
                errors=[f"Validation error: {str(e)}"],
                warnings=[],
                sample_parse_success=False,
                parsed_sample_count=0,
            )

    def save_bank_config(self, config: Dict[str, Any]) -> bool:
        """
        Save bank configuration to file and reload configs.

        Args:
            config: Complete bank configuration

        Returns:
            True if successful, False otherwise
        """
        # Handle both old (bank_name) and new (name) field formats
        bank_info = config.get("bank_info", {})
        bank_name = bank_info.get("name") or bank_info.get("bank_name", "")
        print(f"ℹ [UnknownBankService] Saving config for bank: {bank_name}")

        try:
            # Determine config file path
            config_dir = self.config_service.config_dir
            config_filename = f"{bank_name}.conf"
            config_path = os.path.join(config_dir, config_filename)

            # Create ConfigParser object
            config_parser = config_parser = configparser.ConfigParser(
                allow_no_value=True
            )

            # Add sections to config file
            self._add_bank_info_section(config_parser, config["bank_info"])
            self._add_csv_config_section(config_parser, config["csv_config"])
            self._add_column_mapping_section(config_parser, config["column_mapping"])
            self._add_data_cleaning_section(config_parser, config["data_cleaning"])

            if "categorization" in config:
                self._add_categorization_section(
                    config_parser, config["categorization"]
                )

            if "default_category_rules" in config:
                self._add_default_category_rules_section(
                    config_parser, config["default_category_rules"]
                )

            if "outgoing_patterns" in config:
                self._add_outgoing_patterns_section(
                    config_parser, config["outgoing_patterns"]
                )

            if "incoming_patterns" in config:
                self._add_incoming_patterns_section(
                    config_parser, config["incoming_patterns"]
                )

            if "description_cleaning" in config:
                self._add_description_cleaning_section(
                    config_parser, config["description_cleaning"]
                )

            # Write to file
            with open(config_path, "w", encoding="utf-8") as f:
                config_parser.write(f)

            print(f"  Config saved to: {config_path}")

            # Reload all configurations to pick up the new one
            reload_success = self.config_service.reload_all_configs(force=True)
            if reload_success:
                print(
                    f"  Configs reloaded successfully. Bank '{bank_name}' is now available."
                )
            else:
                print(
                    f"[WARNING] Config saved but reload failed. Restart may be required."
                )

            return True

        except Exception as e:
            print(f"[ERROR] [UnknownBankService] Failed to save config: {str(e)}")
            return False

    def _generate_content_signatures(self, analysis: UnknownBankAnalysis) -> List[str]:
        """Generate content signatures for bank detection."""
        signatures = []

        # Use some headers as content signatures
        meaningful_headers = [
            h for h in analysis.headers if len(h) > 3 and not h.isdigit()
        ]
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
            "decimal_separator": amount_format.decimal_separator,
            "thousand_separator": amount_format.thousand_separator,
            "negative_style": amount_format.negative_style,
            "currency_position": amount_format.currency_position,
        }

    def _generate_categorization_rules(
        self, user_input: BankConfigInput
    ) -> Dict[str, str]:
        """Generate basic categorization rules."""
        # For now, return empty rules - user can add these later
        # Could be enhanced to suggest rules based on common patterns
        return {}

    def _generate_default_category_rules(self) -> Dict[str, str]:
        """Generate basic default category rules for transaction classification."""
        return {"positive": "Income", "negative": "Expense", "zero": "Transfer"}

    def _add_bank_info_section(
        self, config_parser: configparser.ConfigParser, bank_info: Dict[str, Any]
    ):
        """Add bank_info section to config."""
        config_parser.add_section("bank_info")
        # Handle both old (bank_name) and new (name) field formats
        name = bank_info.get("name") or bank_info.get("bank_name", "")
        config_parser.set("bank_info", "name", name)
        config_parser.set("bank_info", "display_name", bank_info["display_name"])
        config_parser.set(
            "bank_info", "file_patterns", ", ".join(bank_info["file_patterns"])
        )
        config_parser.set(
            "bank_info",
            "detection_content_signatures",
            ", ".join(bank_info.get("detection_content_signatures", [])),
        )
        if "expected_headers" in bank_info:
            config_parser.set(
                "bank_info",
                "expected_headers",
                ", ".join(bank_info["expected_headers"]),
            )
        config_parser.set(
            "bank_info", "currency_primary", bank_info["currency_primary"]
        )
        config_parser.set("bank_info", "cashew_account", bank_info["cashew_account"])

    def _add_csv_config_section(
        self, config_parser: configparser.ConfigParser, csv_config: Dict[str, Any]
    ):
        """Add csv_config section to config."""
        config_parser.add_section("csv_config")
        config_parser.set("csv_config", "encoding", csv_config.get("encoding", "utf-8"))
        config_parser.set("csv_config", "delimiter", csv_config.get("delimiter", ","))

        # Add header_row field (critical for proper parsing)
        if "header_row" in csv_config:
            config_parser.set("csv_config", "header_row", str(csv_config["header_row"]))
        else:
            config_parser.set("csv_config", "header_row", "0")  # Default to first row

        # Handle both new and old field formats
        if "has_header" in csv_config:
            config_parser.set(
                "csv_config", "has_header", str(csv_config["has_header"]).lower()
            )
        else:
            config_parser.set("csv_config", "has_header", "true")

        if "skip_rows" in csv_config:
            config_parser.set("csv_config", "skip_rows", str(csv_config["skip_rows"]))
        else:
            config_parser.set("csv_config", "skip_rows", "0")

        # Add detected date format if available
        if "date_format" in csv_config and csv_config["date_format"]:
            # Escape percentage signs for configparser
            escaped_format = csv_config["date_format"].replace("%", "%%")
            config_parser.set("csv_config", "date_format", escaped_format)

    def _add_column_mapping_section(
        self, config_parser: configparser.ConfigParser, column_mapping: Dict[str, str]
    ):
        """Add column_mapping section to config."""
        config_parser.add_section("column_mapping")
        for standard_field, csv_column in column_mapping.items():
            if csv_column:  # Only add non-empty mappings
                config_parser.set("column_mapping", standard_field, csv_column)

    def _add_data_cleaning_section(
        self, config_parser: configparser.ConfigParser, data_cleaning: Dict[str, Any]
    ):
        """Add data_cleaning section to config."""
        config_parser.add_section("data_cleaning")

        amount_format = data_cleaning.get("amount_format", {})
        if amount_format:
            # Use the new field names that UnifiedConfigService expects
            config_parser.set(
                "data_cleaning",
                "amount_format_decimal_separator",
                amount_format.get("decimal_separator", "."),
            )
            config_parser.set(
                "data_cleaning",
                "amount_format_thousand_separator",
                amount_format.get("thousand_separator", ","),
            )
            config_parser.set(
                "data_cleaning",
                "amount_format_negative_style",
                amount_format.get("negative_style", "minus"),
            )
            config_parser.set(
                "data_cleaning",
                "amount_format_currency_position",
                amount_format.get("currency_position", "prefix"),
            )

            # Also save the format name if it's a standard format
            format_name = amount_format.get("name", "")
            if format_name:
                config_parser.set(
                    "data_cleaning", "amount_format_name", format_name.lower()
                )

        config_parser.set(
            "data_cleaning",
            "auto_detect_format",
            str(data_cleaning.get("auto_detect_format", False)),
        )
        config_parser.set(
            "data_cleaning",
            "currency_handling",
            data_cleaning.get("currency_handling", "standard"),
        )

    def _add_categorization_section(
        self, config_parser: configparser.ConfigParser, categorization: Dict[str, str]
    ):
        """Add categorization section to config."""
        if categorization:
            config_parser.add_section("categorization")
            for pattern, category in categorization.items():
                config_parser.set("categorization", pattern, category)

    def _add_description_cleaning_section(
        self,
        config_parser: configparser.ConfigParser,
        description_cleaning: Dict[str, str],
    ):
        """Add description_cleaning section to config."""
        if description_cleaning:
            config_parser.add_section("description_cleaning")
            for pattern, replacement in description_cleaning.items():
                config_parser.set("description_cleaning", pattern, replacement)

    def _add_default_category_rules_section(
        self, config_parser: configparser.ConfigParser, rules: Dict[str, str]
    ):
        """Add default_category_rules section to config."""
        config_parser.add_section("default_category_rules")
        for rule_type, category in rules.items():
            config_parser.set("default_category_rules", rule_type, category)

    def _add_outgoing_patterns_section(
        self, config_parser: configparser.ConfigParser, patterns: Dict[str, str]
    ):
        """Add outgoing_patterns section to config."""
        config_parser.add_section("outgoing_patterns")
        # Empty for now - can be enhanced later

    def _add_incoming_patterns_section(
        self, config_parser: configparser.ConfigParser, patterns: Dict[str, str]
    ):
        """Add incoming_patterns section to config."""
        config_parser.add_section("incoming_patterns")
        # Empty for now - can be enhanced later

    def _detect_date_format(self, analysis: UnknownBankAnalysis) -> Optional[Dict[str, Any]]:
        """
        Detect date format from sample data using pandas with majority vote.

        Args:
            analysis: UnknownBankAnalysis containing sample data and field mappings

        Returns:
            Dictionary with detailed date format detection results or None if detection fails
        """
        try:
            # Find the date column from field mapping suggestions
            date_column_name = None
            for field, suggestion in analysis.field_mapping_suggestions.items():
                if field == "date" and suggestion.best_match:
                    date_column_name = suggestion.best_match
                    break

            # If no date field mapping found, try to find common date column names
            if not date_column_name and analysis.sample_data and analysis.headers:
                common_date_names = [
                    "date",
                    "timestamp",
                    "created_at",
                    "processed_at",
                    "transaction_date",
                    "booking_date",
                    "value_date",
                    "datum",
                    "fecha",
                    "data",
                ]

                for header in analysis.headers:
                    header_lower = header.lower()
                    if any(
                        date_name in header_lower for date_name in common_date_names
                    ):
                        date_column_name = header
                        print(
                            f"  [DEBUG] Found potential date column by name matching: '{date_column_name}'"
                        )
                        break

            if not date_column_name or not analysis.sample_data:
                print(
                    f"  [WARNING] Date format detection skipped: date_column='{date_column_name}', sample_data_available={bool(analysis.sample_data)}"
                )
                return None

            # Extract up to 5 non-null date samples for robust detection
            date_samples = []
            for row in analysis.sample_data[
                :10
            ]:  # Check first 10 rows to get 5 samples
                if date_column_name in row and row[date_column_name]:
                    date_value = str(row[date_column_name]).strip()
                    if date_value and date_value.lower() != "nan":
                        date_samples.append(date_value)
                        if len(date_samples) >= 5:
                            break

            if not date_samples:
                print(
                    f"  [WARNING] No valid date samples found in column '{date_column_name}'"
                )
                return None

            print(
                f"  [DEBUG] Date format detection using {len(date_samples)} samples from column '{date_column_name}': {date_samples}"
            )

            # Infer format for each sample
            inferred_formats = []
            for sample in date_samples:
                try:
                    format_guess = guess_datetime_format(sample)
                    if format_guess:
                        inferred_formats.append(format_guess)
                        print(f"    Sample '{sample}' → format '{format_guess}'")
                    else:
                        # Fallback: try common date patterns when pandas fails
                        fallback_format = self._try_common_date_patterns(sample)
                        if fallback_format:
                            inferred_formats.append(fallback_format)
                            print(
                                f"    Sample '{sample}' → format '{fallback_format}' (fallback)"
                            )
                        else:
                            print(f"    Sample '{sample}' → no format detected")
                except Exception as e:
                    print(f"    Sample '{sample}' → failed: {e}")
                    continue

            if not inferred_formats:
                print(f"  [WARNING] No date formats could be inferred from samples")
                return None

            # Find the most common format using majority vote
            format_counter = Counter(inferred_formats)
            most_common_format, count = format_counter.most_common(1)[0]
            confidence = count / len(inferred_formats) if inferred_formats else 0.0

            print(
                f"  [SUCCESS] Date format detection: '{most_common_format}' (appeared {count}/{len(inferred_formats)} times, {confidence:.1%} confidence)"
            )
            
            # Return detailed information
            return {
                'detected_format': most_common_format,
                'confidence': confidence,
                'samples_analyzed': len(date_samples),
                'format_distribution': [{'format': fmt, 'count': cnt} for fmt, cnt in format_counter.most_common()],
                'date_column_name': date_column_name,
                'sample_dates': date_samples
            }

        except Exception as e:
            print(f"  [ERROR] Date format detection failed: {e}")
            return None

    def _try_common_date_patterns(self, date_sample: str) -> Optional[str]:
        """
        Try common date patterns when pandas guess_datetime_format fails.
        Particularly useful for 2-digit years and other edge cases.

        Args:
            date_sample: Date string to analyze

        Returns:
            Detected format string or None if no pattern matches
        """
        from datetime import datetime

        # Common date patterns to try, especially for 2-digit years
        common_patterns = [
            "%d.%m.%y",  # 20.02.18 (German format with 2-digit year)
            "%d/%m/%y",  # 20/02/18 (European format with 2-digit year)
            "%m/%d/%y",  # 02/20/18 (American format with 2-digit year)
            "%y-%m-%d",  # 18-02-20 (ISO-like with 2-digit year)
            "%d-%m-%y",  # 20-02-18 (European format with 2-digit year)
            "%d.%m.%Y",  # 20.02.2018 (German format with 4-digit year)
            "%d/%m/%Y",  # 20/02/2018 (European format with 4-digit year)
            "%m/%d/%Y",  # 02/20/2018 (American format with 4-digit year)
            "%Y-%m-%d",  # 2018-02-20 (ISO format)
            "%d-%m-%Y",  # 20-02-2018 (European format with 4-digit year)
            "%Y.%m.%d",  # 2018.02.20 (Alternative ISO format)
            "%d %b %Y",  # 20 Feb 2018 (Month name format)
            "%b %d, %Y",  # Feb 20, 2018 (American month name format)
        ]

        for pattern in common_patterns:
            try:
                datetime.strptime(date_sample, pattern)
                return pattern
            except ValueError:
                continue

        return None
