# Configuration System for Bank Statement Parser

## Overview
The bank statement parser uses a flexible configuration system that eliminates hardcoded bank rules from the code. This makes it easy to add new banks and customize transaction patterns without modifying the source code.

## 🔧 Setup Instructions

### First Time Setup
1. **Copy template configurations to create your personal configs:**
   ```bash
   cp configs/app.conf.template configs/app.conf
   cp configs/wise_usd.conf.template configs/wise_usd.conf
   cp configs/wise_eur.conf.template configs/wise_eur.conf
   cp configs/wise_huf.conf.template configs/wise_huf.conf
   cp configs/nayapay.conf.template configs/nayapay.conf
   cp configs/Erste.conf.template configs/Erste.conf
   ```

2. **Edit `configs/app.conf` with your personal information:**
   ```ini
   [general]
   user_name = Your Actual Name
   date_tolerance_hours = 72
   ```

3. **Customize bank configurations with your actual merchants and patterns**

## Configuration Structure

```
configs/
├── app.conf.template      # Template for global settings
├── wise_family.conf       # Shared Wise rules (included in repo)
├── *.conf.template        # Template configurations (included in repo)
└── *.conf                 # Your personal configurations (git-ignored)
```

## Template vs Personal Configurations

### 📋 Templates (Public Repository)
- `*.conf.template` files contain anonymized examples
- Match the anonymized sample data for demonstration
- Safe to include in public repositories
- Use generic names like "John Smith", "Sample Company"

### 🔒 Personal Configurations (Private)
- `*.conf` files contain your actual personal data
- Automatically excluded from git (see `.gitignore`)
- Contain your real merchant names, personal contacts, workplace

## Configuration Files

### Global Configuration (`app.conf`)
```ini
[general]
# Replace with your actual name for transfer detection
user_name = Your Actual Name
date_tolerance_hours = 72

[transfer_detection]
confidence_threshold = 0.7

[transfer_categorization]
default_pair_category = Balance Correction
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
[transfer_patterns]
outgoing_transfer = Sent money to {name}
incoming_transfer = Received money from {name}

[incoming_patterns]
received_money = Received money from {user_name}
```

#### Categorization Rules
```ini
[categorization]
# Replace template examples with your actual merchants
Your Local Grocery = Groceries
Your Workplace = Income
Your Favorite Restaurant = Dining
Your Bank Name = Bills & Fees
```

## 🏦 Supported Banks

The system includes template configurations for:
- **Wise (USD)** - US Dollar account
- **Wise (EUR)** - Euro account  
- **Wise (HUF)** - Hungarian Forint account
- **Wise (PKR)** - Pakistani Rupee account
- **NayaPay** - Pakistani digital bank
- **Erste/Forint Bank** - Hungarian bank

## Adding New Banks

1. Create a new `.conf` file in the `configs/` directory
2. Follow the format from existing templates
3. Add file patterns to detect the bank from CSV filenames
4. Define transfer patterns that match the bank's transaction descriptions
5. Add categorization rules for your specific merchants

Example for a new bank (`chase.conf`):
```ini
[bank_info]
name = chase
file_patterns = chase,chase_bank
currency_primary = USD
cashew_account = Chase Checking

[transfer_patterns]
outgoing_transfer = Zelle payment to {name}
incoming_transfer = Zelle from {name}

[categorization]
# Add your actual merchants here
Starbucks = Dining
Shell = Travel
Target = Shopping
```

## Features

### 🌍 Multi-Currency Support
- Each Wise currency pocket has its own configuration
- Maps to specific Cashew accounts
- Separate categorization rules per currency

### 🔍 Flexible Pattern Matching
- Uses pattern matching with name extraction
- Supports `{name}` and `{user_name}` variables
- Easy to copy-paste patterns from actual transaction descriptions

### 🏦 Automatic Bank Detection
- Detects bank type from CSV filename patterns
- Uses configured file patterns for matching
- Content-based detection for additional accuracy

### 🏷️ Smart Categorization
- Bank-specific merchant categorization
- Pattern-based matching with regex support
- Hierarchical rules (family configs + bank-specific overrides)

## 🔧 Configuration Variables

Supported variables in patterns:
- `{name}` - Extracts recipient/sender name from transaction
- `{user_name}` - Uses the configured user name from app.conf

## 🧪 Testing Your Configuration

Test your configuration by running the application with sample data:
```bash
./start_app.sh
```

Upload the included anonymized sample CSV files to verify:
- Bank detection works correctly
- Transfer detection finds matches between files
- Categorization rules apply to your merchants

## Benefits

1. **🚫 No Code Changes**: Add new banks without touching source code
2. **🔧 Easy Maintenance**: All bank rules in readable configuration files
3. **👤 User Customizable**: Modify patterns for your specific needs
4. **🌍 Multi-Currency**: Built-in support for multiple currency accounts
5. **📝 Simple Syntax**: Pattern-based matching, easy to understand and modify
6. **🔒 Privacy Safe**: Personal configurations stay local, templates are shareable

## 🚨 Privacy & Security

### What's Safe to Share
- `*.conf.template` files (anonymized examples)
- `wise_family.conf` (generic shared rules)
- `app.conf.template` (template with placeholders)

### What to Keep Private
- `*.conf` files (your personal configurations)
- Any files containing real merchant names, personal contacts, workplace info
- Your actual `app.conf` with real user name

### Git Safety
The `.gitignore` file automatically excludes:
```
configs/app.conf
configs/*.conf
!configs/*.conf.template
!configs/wise_family.conf
```

## 🛠️ Troubleshooting

### Unknown Bank Type
If you see "Unknown bank type for file: filename.csv":
1. Check if a configuration file exists for this bank
2. Verify the `file_patterns` in the bank configuration include keywords from the filename
3. Create a new configuration file based on the templates

### Transfer Detection Not Working
If transfers aren't being detected:
1. Check your `app.conf` has the correct `user_name`
2. Verify transfer patterns match your actual transaction descriptions
3. Ensure `{name}` and `{user_name}` variables are used correctly

### Categorization Issues
If merchants aren't being categorized correctly:
1. Check the exact merchant name in your CSV files
2. Add or update categorization rules in the appropriate bank config
3. Use pattern matching (e.g., `Your Store.*` to match "Your Store 123")

### Missing Configuration Error
If you get "Please create configs/app.conf":
1. Copy `app.conf.template` to `app.conf`
2. Edit with your actual information
3. Restart the application

## 📝 Example: Complete Bank Setup

### 1. Copy Template
```bash
cp configs/wise_usd.conf.template configs/wise_usd.conf
```

### 2. Customize with Your Data
```ini
[categorization]
# Replace template examples with YOUR actual merchants
Amazon.com = Shopping
Whole Foods = Groceries
Your Company Name = Income
Your Local Coffee Shop = Dining
Your Gym Name = Health
Your Landlord Name = Rent
```

### 3. Test with Real Data
Upload your actual CSV files and verify the categorization works correctly.

## 🔄 Updating Configurations

As you encounter new merchants:
1. Note the exact merchant name from failed categorizations
2. Add appropriate categorization rules to your bank config
3. Re-process the CSV files to apply new rules

## 🏗️ Advanced Features

### Conditional Description Overrides
```ini
[conditional_override_ride_hailing]
name = Detect Ride Hailing
if_amount_min = -2000
if_amount_max = -0.01
if_note_equals = Raast Out
if_description_contains = fund transfer
set_description = Ride Hailing Services
```

### Hierarchical Configuration
- **Family configs** (e.g., `wise_family.conf`) provide shared rules
- **Bank-specific configs** override and extend family rules
- **Automatic inheritance** reduces duplication

### Pattern-Based Matching
```ini
[categorization]
# Exact match
Starbucks = Dining

# Pattern match (regex)
Starbucks.* = Dining
.*Restaurant.* = Dining
```

## 📊 Sample Data Compatibility

The included anonymized sample data works with the template configurations:
- `m-02-2025.csv` → `nayapay.conf.template`
- `statement_*_USD_*.csv` → `wise_usd.conf.template`
- `statement_*_EUR_*.csv` → `wise_eur.conf.template`
- `11600006-*.csv` → `Erste.conf.template`

This allows immediate testing without personal data.

## 🤝 Contributing

When contributing configuration improvements:
1. Only modify `.template` files
2. Use generic, anonymized examples
3. Ensure templates work with sample data
4. Document new features in this README

## 📚 Configuration Reference

### Required Sections
- `[bank_info]` - Basic bank information
- `[csv_config]` - CSV parsing settings
- `[column_mapping]` - Map CSV columns to standard fields

### Optional Sections
- `[categorization]` - Merchant categorization rules
- `[transfer_patterns]` - Transfer detection patterns
- `[description_cleaning]` - Text cleaning rules
- `[conditional_override_*]` - Advanced conditional rules

### Standard Fields
- `Date` - Transaction date
- `Amount` - Transaction amount
- `Title` - Transaction description
- `Note` - Additional notes
- `Account` - Account/currency identifier
- `Category` - Expense category

This configuration system makes the bank statement parser highly flexible and user-customizable while maintaining privacy and security.
