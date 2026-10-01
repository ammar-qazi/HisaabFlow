# HisaabFlow

A powerful, configuration-driven bank statement parser that transforms messy CSV exports into clean, categorized financial data. Automatically detects transfers between accounts and exports structured data perfect for budgeting apps.

![Demo](docs/_media/demo.gif)

## Features

- 🏛️ **Multi-Bank Support**: Wise (multi-currency), NayaPay, Erste Bank, Revolut
- 📊 **Smart Processing**: Parsing, standardization, categorization, description cleaning
- 🔄 **Transfer Detection**: Automatically identifies and matches transfers between accounts
- 🔧 **Configuration-Driven**: Customizable rules via simple `.conf` files
- 📈 **Clean Export**: Structured CSV output optimized for Cashew and other budgeting tools
- 🐳 **Runs in Docker**: One container serves the web UI and API on your machine
- 🛡️ **Privacy First**: All processing happens locally on your machine

## Quick Start

You need [Docker](https://docs.docker.com/get-docker/) with Docker Compose.

```bash
git clone https://github.com/ammar-qazi/HisaabFlow.git
cd HisaabFlow
docker compose up -d --build     # or: make up
```

Open http://127.0.0.1:8000. The app only listens on your own machine.

- Your configuration lives in `./data/configs` on your computer. Edit the `.conf` files there; they are kept across restarts and upgrades. On first start the shipped configs are copied in, and any shipped config you don't have yet is added later. Your own edits are never overwritten.
- Files in `./data` are owned by uid/gid 1000. If your user has a different id, start with `HISAABFLOW_UID=$(id -u) HISAABFLOW_GID=$(id -g) docker compose up -d`.
- Stop with `docker compose down` (or `make down`). Upgrade with `git pull` and `docker compose up -d --build`.

## Supported Banks

| Bank | Currency | Status |
|------|----------|--------|
| **Wise** | Multiple | ✅ Full Support |
| **NayaPay** | PKR | ✅ Full Support |
| **Erste Bank** | HUF | ✅ Full Support |
| **Revolut** | Multiple | ✅ Full Support |
| **Meezan** | PKR | ✅ Full Support |
| **Other Banks** | Single/Multiple | ✅ Full Support Via Unknown Bank Panel |

**Can't parse your bank?** Open a ticket and I'll add support for it.

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

**App-wide settings** (`data/configs/app.conf`):

```conf
[general]
date_tolerance_hours = 72
user_name = Your Name Here

[transfer_detection]
confidence_threshold = 0.7

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

**Bank-specific overrides** (e.g., `data/configs/nayapay.conf`):

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

## Development

Without Docker, with Python 3.11 and Node 22:

```bash
pip install -r backend/requirements-dev.txt
(cd frontend && npm ci)
make dev
```

Open http://127.0.0.1:3000. The React dev server reloads on changes and forwards `/api` to the backend on port 8000, which reloads too. Ctrl+C stops both. Without `HISAABFLOW_CONFIG_DIR` set, the backend reads the repository's `configs/` directly.

## Running Tests

```bash
pip install -r backend/requirements-dev.txt
pytest
```

Tests run against a temporary copy of `configs/`, and the run fails if any test changes the real files.

`backend/tests/golden/` runs every file in `sample_data/` through upload, preview, parse, transform and export, and compares the result with the snapshots in `backend/tests/golden/snapshots/`. If you change the output on purpose, regenerate the snapshots and review the diff before committing:

```bash
UPDATE_GOLDEN=1 pytest backend/tests/golden
git diff backend/tests/golden/snapshots
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

*HisaabFlow - Because your financial data deserves better than manual categorization*
