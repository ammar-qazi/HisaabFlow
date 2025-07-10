"""
Validates that a given row in a CSV file matches the expected header structure.
"""
import csv
from typing import List

class HeaderValidationError(ValueError):
    """Custom exception for header validation errors."""
    pass

def find_and_validate_header(
    file_path: str,
    encoding: str,
    configured_header_row: int, # Expects 0-indexed row number
    expected_headers: List[str]
) -> List[str]:
    """
    Finds a header at a specific row and validates it against expected columns.

    Args:
        file_path: The absolute path to the CSV file.
        encoding: The file encoding to use.
        configured_header_row: The 0-indexed row where the header is expected.
        expected_headers: A list of expected header column names.

    Returns:
        The list of actual headers found in the file if validation passes.

    Raises:
        HeaderValidationError: If the file can't be read, the header row is not found,
                               or the header fails to match at least 80% of expected columns.
    """
    if not expected_headers:
        raise HeaderValidationError("Configuration error: No expected_headers defined for this bank.")

    actual_header = []
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            reader = csv.reader(f)
            for i, row in enumerate(reader):
                if i == configured_header_row:
                    actual_header = [str(h).strip() for h in row]
                    break
            else:
                raise HeaderValidationError(
                    f"Header row not found. Configured row ({configured_header_row}) "
                    f"is beyond the file's total row count."
                )
    except FileNotFoundError:
        raise HeaderValidationError(f"File not found at path: {file_path}")
    except Exception as e:
        raise HeaderValidationError(f"Failed to read or parse CSV file: {e}")

    # Validation Logic
    expected_lower = {h.lower().strip() for h in expected_headers}
    actual_lower = {h.lower() for h in actual_header}

    matches = len(expected_lower.intersection(actual_lower))
    match_ratio = matches / len(expected_lower)

    if match_ratio < 0.8:
        raise HeaderValidationError(
            f"Header mismatch at row {configured_header_row + 1}. "
            f"Match ratio is {match_ratio:.2f}, but a minimum of 0.80 is required. "
            f"Found: {actual_header}, Expected: {expected_headers}"
        )

    print(f"Header validation passed for row {configured_header_row + 1} with ratio {match_ratio:.2f}")
    return actual_header