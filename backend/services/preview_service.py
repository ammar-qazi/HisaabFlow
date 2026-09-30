"""
Preview service for CSV files with bank-aware header detection
"""

from typing import Optional
from backend.infrastructure.csv_parsing import UnifiedCSVParser
from backend.core.bank_detection import BankDetector
from backend.services.bank_detection_cache import get_bank_detection_cache


class PreviewService:
    """Service for handling CSV file previews with bank detection"""

    def __init__(self, config_service):
        self.unified_parser = UnifiedCSVParser()
        self.config_service = config_service
        # Use global cache for bank detection results
        self.cache = get_bank_detection_cache()

    def preview_csv_file(
        self,
        file_path: str,
        filename: str,
        encoding: Optional[str] = None,
        header_row: Optional[int] = None,
    ):
        """
        Preview CSV file with global structure analysis and single-pass bank detection

        Args:
            file_path: Path to the CSV file
            filename: Original filename for bank detection
            encoding: File encoding override
            header_row: Manual header row override (0-based)

        Returns:
            dict: Preview result with bank detection info and global support
        """
        print(f"ℹ [REFACTORED] Preview request for file: {filename}")

        try:
            # Step 1: Single comprehensive structure analysis
            print("ℹ [REFACTORED] Performing global structure analysis...")
            structure_result = self.unified_parser.analyze_structure(
                file_path, encoding
            )

            if not structure_result["success"]:
                return structure_result

            # Step 2: Handle headerless files
            if not structure_result.get("has_headers", True):
                print(
                    f"ℹ [REFACTORED] Headerless CSV detected: {structure_result['total_columns']} columns"
                )

                # Parse some sample data for preview
                sample_parse = self.unified_parser.preview_csv(
                    file_path,
                    encoding=structure_result["encoding"],
                    header_row=None,  # No headers
                    max_rows=20,
                )

                return {
                    "success": True,
                    "headerless_file": True,
                    "preview_data": sample_parse.get("preview_data", []),
                    "column_names": structure_result["suggested_columns"],
                    "total_rows": sample_parse.get("total_rows", 0),
                    "encoding_used": structure_result["encoding"],
                    "dialect_detected": structure_result["dialect"],
                    "language_hints": structure_result.get("language_hints", []),
                    "structure_confidence": structure_result["confidence"],
                    "bank_detection": {
                        "detected_bank": "unknown",
                        "confidence": 0.0,
                        "reasons": ["Headerless file - bank detection not applicable"],
                    },
                    "message": "CSV file has no headers. Generated column names provided.",
                }

            # Step 3: Override header row if manually specified
            effective_header_row = (
                header_row
                if header_row is not None
                else structure_result["suggested_header_row"]
            )

            print(f"ℹ [REFACTORED] Using header row: {effective_header_row}")

            # Step 4: Single bank detection with complete structure info
            print("ℹ [REFACTORED] Performing bank detection with complete structure...")
            bank_detector = BankDetector(self.config_service)
            bank_detection = bank_detector.detect_bank(
                filename=filename,
                csv_content=structure_result["content_sample"],
                headers=structure_result["raw_headers"],
                min_confidence=BankDetector.MIN_CONFIDENCE,
            )

            # Cache the bank detection result for later use
            self.cache.set(
                filename,
                file_path,
                {
                    "bank_name": bank_detection.bank_name,
                    "confidence": bank_detection.confidence,
                    "reasons": bank_detection.reasons,
                    "headers": structure_result["raw_headers"],
                    "encoding": structure_result["encoding"],
                    "content_sample": structure_result[
                        "content_sample"
                    ],  # Store content for signature matching
                },
            )

            print(
                f"ℹ [REFACTORED] Detected bank: {bank_detection.bank_name} (confidence: {bank_detection.confidence:.2f})"
            )

            # Step 5: Parse with known structure (no more guessing!)
            print("ℹ [REFACTORED] Parsing with definitive structure...")
            parse_result = self.unified_parser.preview_csv(
                file_path,
                encoding=structure_result["encoding"],
                header_row=effective_header_row,
                max_rows=20,
            )

            if not parse_result.get("success"):
                return parse_result

            # Step 6: Combine results
            final_result = {
                **parse_result,
                "bank_detection": {
                    "detected_bank": bank_detection.bank_name,
                    "confidence": bank_detection.confidence,
                    "reasons": bank_detection.reasons,
                },
                "structure_analysis": {
                    "method": structure_result.get("method", "multilingual_analysis"),
                    "confidence": structure_result["confidence"],
                    "language_hints": structure_result.get("language_hints", []),
                    "has_headers": structure_result["has_headers"],
                },
                "encoding_used": structure_result["encoding"],
                "dialect_detected": structure_result["dialect"],
                "detected_header_row": structure_result["suggested_header_row"] + 1
                if header_row is None
                else None,  # Convert to 1-based, only if auto-detected
            }

            print(
                f"ℹ [SUCCESS] Single-pass preview completed: {len(parse_result.get('column_names', []))} columns"
            )
            return final_result

        except Exception as e:
            print(f"[ERROR] Preview exception: {str(e)}")
            import traceback

            print(f"Traceback: {traceback.format_exc()}")
            return {"success": False, "error": str(e)}

    def get_cached_bank_detection(
        self, filename: str, file_path: str
    ) -> Optional[dict]:
        """Get cached bank detection result if available"""
        return self.cache.get(filename, file_path)

    def clear_cache(self):
        """Clear the bank detection cache"""
        self.cache.clear()
