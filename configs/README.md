# Configuration System for Bank Statement Parser

## Overview
The bank statement parser now uses a flexible configuration system that eliminates hardcoded bank rules from the code. This makes it easy to add new banks and customize transaction patterns without modifying the source code.

## Configuration Structure

```
configs/
├── app.conf          # Global application settings
├── wise_usd.conf     # Wise USD account configuration  
├── wise_eur.conf     # Wise EUR account configuration
├── wise_huf.conf     # Wise HUF account configuration
└── nayapay.conf      # Nayapay account configuration
```

## Configuration Files

### Global Configuration (`app.conf`)
```ini
[general]
user_name = Ammar Qazi
date_tolerance_hours = 72

[transfer_detection]
confidence_threshold = 0.7
```

### Bank Configuration Format
Each bank has its own `.conf` file with these sections:

#### Bank Information
```ini
[bank_info]
name = wise_usd
file_patterns = wise,transferwise,wise_usd
currency_primary = USD
cashew_account = TransferWise
```

#### Transfer Patterns
```ini
[outgoing_patterns]
send_money = Send money to {user_name}
transfer_to = Transfer to {user_name}

[incoming_patterns]
received_money = Received money from {user_name}
```

#### Categorization Rules
```ini
[categorization]
Lidl = Grocery
Aldi = Grocery
Amazon = Shopping
PayPal = Online Payment
```

## Adding New Banks

1. Create a new `.conf` file in the `configs/` directory
2. Follow the format above
3. Add file patterns to detect the bank from CSV filenames
4. Define transfer patterns that match the bank's transaction descriptions
5. Optionally add categorization rules for merchants

Example for a new bank (`bankxyz.conf`):
```ini
[bank_info]
name = bankxyz
file_patterns = xyz,bank_xyz
currency_primary = USD
cashew_account = BankXYZ Account

[outgoing_patterns]
sent_to = Sent to {user_name}

[incoming_patterns]
received_from = Received from {user_name}

[categorization]
Walmart = Grocery
Target = Shopping
```

## Features

### Multi-Currency Support
- Each Wise currency pocket has its own configuration
- Maps to specific Cashew accounts
- Separate categorization rules per currency

### Flexible Pattern Matching
- Uses simple string matching (no regex required)
- Supports `{user_name}` variable substitution
- Easy to copy-paste patterns from actual transaction descriptions

### Bank Detection
- Automatically detects bank type from CSV filename
- Uses configured file patterns for matching
- Falls back to 'unknown' if no match found

### Categorization
- Bank-specific merchant categorization
- Simple substring matching
- Easily extensible for new merchants

## Configuration Variables

Currently supported variables in patterns:
- `{user_name}` - Replaced with the configured user name

## Testing Configuration

Run the configuration test to verify your setup:
```bash
python3 test_config_system.py
```

This will test:
- Configuration loading
- Bank detection
- Pattern generation
- Categorization rules
- CrossBankMatcher initialization

## Benefits

1. **No Code Changes**: Add new banks without touching source code
2. **Easy Maintenance**: All bank rules in readable configuration files
3. **User Customizable**: Users can modify patterns for their specific needs
4. **Multi-Currency**: Built-in support for multiple currency accounts
5. **Simple Syntax**: No regex knowledge required, just copy-paste transaction text

## Troubleshooting

### Unknown Bank Type
If you see "Unknown bank type for file: filename.csv":
1. Check if a configuration file exists for this bank
2. Verify the `file_patterns` in the bank configuration include keywords from the filename
3. Add the missing configuration file

### Pattern Not Matching
If transfers aren't being detected:
1. Check the actual transaction descriptions in your CSV files
2. Copy the exact text and add it to the appropriate pattern section
3. Ensure `{user_name}` variable is used correctly
4. Test with the configuration test script

### Missing Configuration
If you get "Please create configs/app.conf":
1. Copy the example `app.conf` from above
2. Adjust the `user_name` to match your needs
3. Restart the application

## Example: Adding Chase Bank

1. Create `configs/chase.conf`:
```ini
[bank_info]
name = chase
file_patterns = chase,chase_bank
currency_primary = USD
cashew_account = Chase Checking

[outgoing_patterns]
zelle_sent = Zelle payment to {user_name}
wire_transfer = Wire transfer to {user_name}

[incoming_patterns]
zelle_received = Zelle from {user_name}
wire_received = Wire from {user_name}

[categorization]
Starbucks = Food
Shell = Gas
Target = Shopping
```

2. The system will automatically detect Chase CSV files and apply these rules

## Advanced Configuration

### Multiple File Patterns
Use comma-separated patterns for banks with varying filename formats:
```ini
file_patterns = wise,transferwise,wise_account,tw_export
```

### Case Sensitivity
- All pattern matching is case-insensitive
- File pattern matching is case-insensitive
- Categorization matching is case-insensitive

### Pattern Precedence
- First matching pattern wins
- Outgoing patterns are checked before incoming patterns
- Exact substring matches are used (no regex)

## Migration from Hardcoded Rules

The old hardcoded patterns in `cross_bank_matcher.py` have been replaced with:
- Configuration-driven pattern matching
- Flexible bank detection
- User-customizable rules
- Multi-currency support

No existing functionality has been lost, but everything is now configurable.
