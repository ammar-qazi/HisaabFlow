# HisaabFlow

**HisaabFlow** (*"Hisaab" = Account/Calculation in Urdu/Hindi*) is a powerful, configuration-driven bank statement parser that automatically categorizes transactions, detects transfers between accounts, and exports clean, structured financial data.

## Key Features

- 🏛️ **Multi-Bank Support**: Currently supports Wise (multi-currency), NayaPay, and Erste Bank
- 🔧 **Configuration-Based Categorization**: Rule-based transaction categorization with customizable keywords
- 🔄 **Transfer Detection**: Automatically identifies and matches transfers between your accounts
- 📊 **Structured Data Export**: Clean, organized transaction data perfect for budgeting apps
- 🖥️ **Desktop App**: Native Electron application with modern React UI
- 📈 **CSV Export**: Export processed data in structured CSV format for Cashew and other budgeting tools
- 🛡️ **Privacy First**: All processing happens locally on your machine

## Screenshots

### Upload Files
![Drag-and-drop file upload interface with bank auto-detection](/docs/_media/upload_statements.png)

### Configure
![Set configs and review transaction tables](/docs/_media/Configure.png)

### Review & Export
![Screenshot placeholder - Transfer detection insights and CSV export options](/docs/_media/Review_Export.png)

## Quick Start

### Download & Run (Recommended)

**Get the latest release from [GitHub Releases](https://github.com/ammar-qazi/HisaabFlow/releases)**

**Linux (AppImage):**
```bash
# Download HisaabFlow.AppImage
chmod +x HisaabFlow.AppImage
./HisaabFlow.AppImage
```

**📁 First Run Setup**: On first launch, HisaabFlow automatically creates a `~/HisaabFlow/` directory in your home folder containing:
- `sample_data/` - Example CSV files for testing
- `configs/` - Configuration files copied from the app

**All users work from `~/HisaabFlow/` regardless of installation method.** Use sample data from `~/HisaabFlow/sample_data/` and edit configs in `~/HisaabFlow/configs/` for your personal setup.

**macOS:**
```bash
# Download HisaabFlow.dmg
# Open and drag to Applications folder
```

**Windows:**
```
🚧 Coming Soon. Work in progress
```

### Build from Source (Alternative)

If you prefer to build from source or want to contribute:

### Prerequisites

- **Python 3.9+** with pip
- **Node.js 16+** with npm/yarn

### One-Command Installation & Launch

```bash
# Clone the repository
git clone https://github.com/ammar-qazi/HisaabFlow.git
cd HisaabFlow

# Make start script executable and run
chmod +x start_app.sh
./start_app.sh
```

The start script will:
1. [SUCCESS] Check system requirements
2. 🔧 Set up Python virtual environment
3. 📦 Install all dependencies automatically
4. 🚀 Launch both backend and frontend
5. 🖥️ Open the desktop application

### Manual Setup (Alternative)

<details>
<summary>Click to expand manual setup instructions</summary>

**⚠️ Note for Windows users:** This project uses pandas which requires cmake on Windows. There are currently some setup issues on Windows that haven't been fully resolved yet. So, it's a work in progress.

**📁 One-Time Setup for Source Builds:** GitHub releases come with ready-to-use .conf files, but source builds start with only templates. Before first run, create working configs:

```bash
# Copy essential configuration templates to create working configs
cp configs/app.conf.template configs/app.conf
cp configs/wise_usd.conf.template configs/wise_usd.conf
cp configs/wise_eur.conf.template configs/wise_eur.conf
cp configs/wise_huf.conf.template configs/wise_huf.conf
cp configs/wise_family.conf.template configs/wise_family.conf
cp configs/nayapay.conf.template configs/nayapay.conf
cp configs/Erste.conf.template configs/Erste.conf

# Edit configs/app.conf with your personal information
```

**After this one-time setup, the desktop app will copy these configs to `~/HisaabFlow/configs/` and use them from there.**

#### Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

#### Frontend Setup
```bash
cd frontend
npm install
npm run electron-dev
```

</details>

## Architecture

HisaabFlow is built with a modern, decoupled architecture that separates the user interface from the core data processing logic. This ensures that the application is both robust and easy to maintain.

```
                               +--------------------+
                               |   Frontend (UI)    |
                               | (React + Electron) |
                               +--------------------+
                                        |
                                        | (API Calls)
                                        v
+--------------------------------------------------------------------------+
|                               Backend (API)                              |
|                                 (FastAPI)                                |
+--------------------------------------------------------------------------+
|        |                |                  |                 |           |
|        v                v                  v                 v           v
|  +-----------+    +-----------+    +---------------+    +-----------+    +---------+
|  | File Mgmt |    | Parsing   |    | Transformation|    | Transfer  |    | Config  |
|  | Service   |    | Service   |    | Service       |    | Detection |    | Service |
|  +-----------+    +-----------+    +---------------+    +-----------+    +---------+
|        |                |                  |                 |           |
|        |                |                  |                 |           |
|        v                v                  v                 v           v
|  +--------------------------------------------------------------------------+
|  |                              Core Logic                                |
|  +--------------------------------------------------------------------------+
|  | Bank Detection | CSV Processing | Data Cleaning | Transfer Matching | ... |
|  +--------------------------------------------------------------------------+

```

### Key Components:

*   **Frontend**: A desktop application built with **React** and **Electron**. It provides the user interface for file uploads, configuration, and data review.

*   **Backend**: A powerful API server built with **FastAPI**. It handles all the heavy lifting, including file parsing, data cleaning, and transfer detection.

*   **Services Layer**: The backend is organized into a set of focused services, each responsible for a specific part of the workflow (e.g., `ParsingService`, `TransformationService`).

*   **Core Logic**: This is the heart of the application, containing the sophisticated algorithms for bank detection, CSV processing, and transfer matching.

*   **Configuration Files**: The entire process is driven by simple `.conf` files, which define the rules for each bank. This makes the application incredibly flexible and easy to extend.

## Configuration

### Bank Configuration
HisaabFlow uses .conf files to support different bank formats. Here's the structure based on the actual NayaPay configuration:

**📁 Configuration File Locations:**
All desktop app users work with configs in `~/HisaabFlow/configs/` (automatically created and managed by the app).

```conf
# configs/nayapay.conf
[bank_info]
name = nayapay
file_patterns = nayapay,naya_pay
filename_regex_patterns = ^m-\d{2}-\d{4}\.csv$
detection_content_signatures = NayaPay ID,NayaPay Account Number
currency_primary = PKR
cashew_account = NayaPay

[csv_config]
has_header = true
date_format = %%Y-%%m-%%d
encoding = utf-8
start_row = 13
header_row = 13
data_start_row = 14
expected_headers = TIMESTAMP,TYPE,DESCRIPTION,AMOUNT,BALANCE

[column_mapping]
Date = TIMESTAMP
Amount = AMOUNT
Title = DESCRIPTION
Note = TYPE
Balance = BALANCE

[data_cleaning]
enable_currency_addition = true
numeric_amount_conversion = true
date_standardization = true
remove_invalid_rows = true
default_currency = PKR

[description_cleaning]
# Transform specific patterns in transaction descriptions
uber_pattern = Card transaction.*Uber.*|Uber Ride
savemart_pattern = Savemart.*|Savemart
mobile_topup = Mobile top-up purchased\|.*Nickname: (.*?)(?:\|.*)?$|Mobile topup for \1

[categorization]
Savemart = Grocery
KFC = Food
amazon = Shopping
salary = Income
Mobile topup.* = Bills & Fees
```

### Transfer Detection
Configure transfer detection in `configs/app.conf`:

```conf
[transfer_detection]
confidence_threshold = 0.7
date_tolerance_hours = 72
# Optional
user_name = Your Name Here

[transfer_categorization]
default_pair_category = Balance Correction
```

## Supported Banks

HisaabFlow currently includes configurations for:

| Bank | Currency | Status | Sample Format |
|------|----------|--------|---------------|
| **Wise (TransferWise)** | USD | [SUCCESS] Full Support | `statement_20141677_USD_2025-01-04_2025-06-02.csv` |
| **Wise (TransferWise)** | EUR | [SUCCESS] Full Support | `statement_23243482_EUR_2025-01-04_2025-06-02.csv` |
| **Wise (TransferWise)** | PKR | [SUCCESS] Full Support | N/A |
| **Wise (TransferWise)** | HUF | [SUCCESS] Full Support | N/A |
| **NayaPay** | PKR | [SUCCESS] Full Support | `m-02-2025.csv` |
| **Erste Bank** | HUF | [SUCCESS] Full Support | `12345678-00000000-87654321_2025-06-01_2025-06-30.csv` |
| **Revolut** | Multiple | [SUCCESS] Full Support | `account-statement_2024-04-01_2025-06-25_en-us_b9705c.csv` |

**Don't see your bank?** HisaabFlow's powerful configuration system allows you to easily add support for any bank that provides CSV exports. See the "Adding New Banks" section for more details.

## Workflow

HisaabFlow provides a simple, step-by-step workflow to transform your messy bank statements into a clean, unified dataset.

1.  **Upload Your CSVs**: Drag and drop one or more of your bank statement CSV files into the application. HisaabFlow will automatically analyze each file.

2.  **Automatic Bank Detection**: For each file, HisaabFlow's intelligent detection engine will identify the source bank using filename patterns and content analysis.
    *   **Known Banks**: If the bank is recognized, the corresponding configuration is automatically applied.
    *   **Unknown Banks**: If a bank isn't recognized, you'll be guided through a simple, one-time setup process to create a new configuration.

3.  **Configure and Review**: In this step, you can:
    *   Review the automatically parsed data in an interactive table.
    *   For unknown banks, visually map the columns from your CSV (e.g., "Transaction Date", "Details", "Amount In") to HisaabFlow's standard fields.
    *   Save the new configuration for future use.

4.  **Transform and Analyze**: With all your data parsed and standardized, HisaabFlow performs its most powerful operations:
    *   **Data Cleaning**: Standardizes dates, cleans up transaction descriptions, and ensures all data is in a consistent format.
    *   **Transfer Detection**: Intelligently identifies and flags transfer transactions between your different accounts, preventing them from being counted as income or expenses.

5.  **Review and Export**: In the final step, you can:
    *   Review the fully processed and unified transaction list.
    *   Manually confirm any potential transfer pairs that the system is not 100% confident about.
    *   Export the final, clean dataset as a single CSV file, ready for import into your favorite budgeting application.

## Use Cases

## Use Cases

### Personal Finance Management
- **CSV Consolidation**: Combine multiple bank statement CSVs into one structured format
- **Cashew Integration**: Export data perfectly formatted for Cashew expense tracker
- **Transfer Detection**: Automatically identify transfers between your accounts to avoid double-counting
- **Clean Categorization**: Rule-based transaction categorization for better organization

### Multi-Account Management
- **Multi-Bank Support**: Handle CSV exports from different banks (Wise, NayaPay, Erste)
- **Currency Handling**: Support for multiple currencies (USD, EUR, PKR, HUF)
- **Account Reconciliation**: Match transfers between different accounts and banks
- **Unified Export**: Single CSV export containing all accounts for budgeting apps

### Budgeting App Preparation
- **Cashew Ready**: Currently optimized for Cashew expense tracker format
- **Future Support**: Planned integration with Money Lover, YNAB, and other budgeting apps
- **Clean Data**: Processed, categorized, and transfer-aware transaction data

## Advanced Usage

### Adding New Banks

HisaabFlow is designed to be easily extended to support any bank that provides CSV exports. If you use a bank that isn't already supported, you can add it yourself in a few simple steps. The application will guide you through a one-time setup process where you can:

1.  **Visually Map Columns**: Match the columns from your bank's CSV file to HisaabFlow's standard fields (Date, Amount, Title, etc.).
2.  **Define Key Details**: Specify the date format, number format, and other CSV properties.
3.  **Save and Go**: Save your new configuration, and HisaabFlow will be ready to process your bank's statements automatically in the future.

This powerful feature ensures that you can adapt HisaabFlow to your specific needs and are not limited to the pre-configured banks.

### Custom Categorization

Customize transaction categorization by editing .conf files:

```conf
[categorization]
# Grocery stores
walmart = Grocery
target = Grocery
safeway = Grocery

# Restaurants
mcdonalds = Food
starbucks = Food
chipotle = Food

# Transportation
uber = Transportation
lyft = Transportation
shell = Transportation

# Bills & Utilities
verizon = Bills & Fees
pge = Bills & Fees
internet = Bills & Fees
```

### Description Cleaning

Clean and standardize transaction descriptions:

```conf
[description_cleaning]
# Clean up card transactions
card_pattern = Card transaction at (.*?)\s*\|.*|Purchase at \1

# Standardize merchant names
uber_pattern = .*Uber.*|Uber
amazon_pattern = Amazon.*|Amazon

# Extract useful info from complex descriptions
mobile_pattern = Mobile top-up.*Nickname: (.*?)(?:\|.*)?$|Mobile topup for \1
```

### Transfer Detection Tuning

Fine-tune transfer detection sensitivity:

```conf
[transfer_detection]
# Lower threshold = more sensitive (may catch false positives)
# Higher threshold = less sensitive (may miss actual transfers)
confidence_threshold = 0.7

# Time window for matching transfers (hours)
date_tolerance_hours = 72

# Your name variations for transfer detection
user_name = John Doe, J. Doe, John D
```

## Distribution

### Desktop Application (AppImage)

HisaabFlow can be packaged as a standalone desktop application:

```bash
# Build for all platforms
npm run dist:all

# Build for specific platform
npm run dist:linux    # Linux(AppImage)
npm run dist:mac    # macOS
```

**Download ready-to-run desktop apps from [GitHub Releases](https://github.com/ammar-qazi/HisaabFlow/releases)**

## Privacy & Security

- **Local Processing**: All data stays on your machine
- **No Cloud Storage**: No data sent to external servers
- **Open Source**: Full transparency in code and algorithms
- **Configurable**: Control exactly how your data is processed

## Contributing

We welcome contributions! Here's how to get started:

### Development Setup

1. **Fork and Clone**
```bash
git clone https://github.com/ammar-qazi/HisaabFlow.git
cd HisaabFlow
```

2. **Install Dependencies**
```bash
./start_app.sh  # Handles all setup automatically
```

3. **Development Mode**
```bash
# Backend (API server)
cd backend && python main.py

# Frontend (React dev server)
cd frontend && npm start

# Desktop app development
cd frontend && npm run electron-dev
```

### Code Style

- **Backend**: Python with FastAPI, Pydantic models
- **Frontend**: Modern React with hooks, Tailwind CSS
- **Configuration**: CONF files for bank configurations
- **Testing**: Inline debugging (console.log, print statements)

### Contribution Guidelines

- 📝 **Documentation**: Update README for new features
- 🧪 **Testing**: Test with real bank statements (anonymized)
- 🔧 **Configuration**: Add bank configs for new formats
- 🎨 **UI**: Keep interface clean and intuitive
- 🛡️ **Privacy**: Ensure no data leaves user's machine

## API Documentation

When running locally, visit:
- **API Documentation**: http://127.0.0.1:8000/docs
- **API Endpoints**: http://127.0.0.1:8000/redoc

### Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/banks` | GET | List available bank configurations |
| `/api/v1/parse/preview` | POST | Preview CSV parsing results |
| `/api/v1/parse/process` | POST | Process and categorize transactions |
| `/api/v1/transform/analyze-transfers` | POST | Detect transfers between accounts |
| `/api/v1/transform/export` | POST | Export processed data in CSV format |

## Troubleshooting

### Common Issues

**"Backend failed to start"**
```bash
# Check Python version
python3 --version

# Reinstall dependencies
cd backend && pip install -r requirements.txt

# Check if port 8000 is in use
lsof -i :8000
```

**"Frontend won't load"**
```bash
# Clear npm cache
npm cache clean --force

# Reinstall dependencies
cd frontend && rm -rf node_modules && npm install

# Check Node.js version
node --version  # Should be 16+
```

**"Bank not detected"**
```bash
# Check CSV format
head -5 your_bank_statement.csv

# Create custom configuration
cp configs/template.conf configs/yourbank.conf
# Edit the configuration file
```

### Getting Help

- 🐛 **Issues**: Report bugs on GitHub Issues
- 💬 **Discussions**: Ask questions in GitHub Discussions

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **FastAPI** - Modern Python web framework
- **React** - Frontend library
- **Electron** - Desktop app framework
- **Pydantic** - Data validation and parsing
- **Tailwind CSS** - Utility-first CSS framework
- **Pandas** - Data processing and analysis

---

*HisaabFlow - Because your financial data deserves better than manual categorization*