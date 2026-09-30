"""
Work out which bank a transformed transaction row came from.
"""
from typing import Any, Dict, List, Optional


def bank_for_row(row: Dict[str, Any], csv_data_list: Optional[List[Dict[str, Any]]],
                 config_service) -> Optional[str]:
    """
    Return the bank name for a row, or None if it can't be determined.

    Rows from /multi-csv/transform carry _source_bank, set from the file's
    bank detection. Rows without it (older callers, tests) fall back to
    matching the Account against each detected bank's cashew_account or
    account_mapping values.
    """
    source_bank = row.get('_source_bank')
    if source_bank and source_bank != 'unknown':
        return source_bank

    account = row.get('Account', '')
    for csv_data in csv_data_list or []:
        bank_info = csv_data.get('bank_info') or {}
        bank_name = bank_info.get('bank_name', bank_info.get('detected_bank'))
        if not bank_name or bank_name == 'unknown':
            continue
        bank_config = config_service.get_bank_config(bank_name)
        if not bank_config:
            continue
        if bank_config.cashew_account and bank_config.cashew_account == account:
            return bank_name
        if account in (bank_config.account_mapping or {}).values():
            return bank_name
    return None
