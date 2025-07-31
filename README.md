# HisaabFlow

A powerful, configuration-driven bank statement parser that transforms messy CSV exports into clean, categorized financial data. Automatically detects transfers between accounts and exports structured data perfect for budgeting apps.

![Demo](docs/_media/demo.gif)

## Features

- 🏛️ **Multi-Bank Support**: Wise (multi-currency), NayaPay, Erste Bank, Revolut
- 📊 **Smart Processing**: Parsing, standardization, categorization, description cleaning
- 🔄 **Transfer Detection**: Automatically identifies and matches transfers between accounts
- 🔧 **Configuration-Driven**: Customizable rules via simple `.conf` files
- 📈 **Clean Export**: Structured CSV output optimized for Cashew and other budgeting tools
- 🖥️ **Desktop App**: Native Electron application with modern React UI
- 🛡️ **Privacy First**: All processing happens locally on your machine

## Quick Start

**Download the latest release from [GitHub Releases](https://github.com/ammar-qazi/HisaabFlow/releases)**

**Linux (AppImage):**

```bash
chmod +x HisaabFlow.AppImage
./HisaabFlow.AppImage
```

**macOS:**

```bash
# Download HisaabFlow.dmg and drag to Applications
```

**Windows:**

```bash
# Download HisaabFlow.exe
# Note: You may see a security warning since the app is unsigned
# Click "More info" → "Run anyway" to proceed
```

**Build from Source:**

```bash
git clone https://github.com/ammar-qazi/HisaabFlow.git
cd HisaabFlow
chmod +x start_app.sh
./start_app.sh
```

## Supported Banks

| Bank | Currency | Status |
|------|----------|--------|
| **Wise** | Multiple | ✅ Full Support |
| **NayaPay** | PKR | ✅ Full Support |
| **Erste Bank** | HUF | ✅ Full Support |
| **Revolut** | Multiple | ✅ Full Support |
| **Meezan** | PKR | ✅ Full Support |
| **Other Banks** | Multiple | ✅ Full Support Via Unknown Bank Panel* |

**Can't parse your bank** Open a ticket and I'll add support for it.

## How It Works

1. **Upload CSV Files**: Drag and drop your bank statement CSVs
2. **Automatic Detection**: HisaabFlow identifies the bank and applies the right configuration
3. **Smart Processing**:
   - Parses and standardizes transaction data
   - Cleans up messy descriptions
   - Categorizes transactions using customizable rules
   - Detects transfers between your accounts
4. **Review & Export**: Export clean, unified CSV data ready for budgeting apps

## Configuration

HisaabFlow uses `.conf` files for flexible, bank-specific processing rules:

**App-wide settings** (`configs/app.conf`):

```conf
[transfer_detection]
confidence_threshold = 0.7
date_tolerance_hours = 72
user_name = Your Name Here

# Category-based patterns applied to all banks
[Shopping]
Amazon.*
Walmart.*
Target.*

[Transport]
Uber.*
Lyft.*
Shell.*

[Food & Dining]
McDonald's.*
KFC.*
Starbucks.*
```

**Bank-specific overrides** (e.g., `configs/nayapay.conf`):

```conf
[bank_info]
name = nayapay
currency_primary = PKR

[column_mapping]
date = TIMESTAMP
amount = AMOUNT
title = DESCRIPTION

# Bank-specific patterns override global ones
[Groceries]
SaveMart
D. Watson
Grocery

[Bills & Fees]
Mobile top-up.*
Cloud Storage

[description_cleaning]
# Clean up messy transaction descriptions
mobile_topup = Mobile top-up purchased\|.*Nickname: (.*?)(?:\|.*)?$|Mobile topup for \1
```

## Key Capabilities

### Transfer Detection

Automatically identifies transfers between your accounts using:

- Amount matching with configurable tolerance
- Date proximity analysis
- Description pattern recognition
- User name detection in transaction details

### Smart Categorization

- **Global Rules**: Define patterns in `app.conf` that apply to all banks
- **Bank-Specific Rules**: Override global patterns for specific banks
- **Regex Support**: Use powerful pattern matching for complex categorization
- **Description Cleaning**: Transform messy bank descriptions into clean, readable text

### Multi-Currency Support

- Handles multiple currencies within the same processing session
- Preserves original currency information
- Supports currency-specific formatting rules

## Export Formats

Currently optimized for **Cashew** expense tracker with planned support for:

- Money Lover
- YNAB (You Need A Budget)
- Generic CSV formats

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

*HisaabFlow - Because your financial data deserves better than manual categorization*
