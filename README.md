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
1. ✅ Check system requirements
2. 🔧 Set up Python virtual environment
3. 📦 Install all dependencies automatically
4. 🚀 Launch both backend and frontend
5. 🖥️ Open the desktop application

### Manual Setup (Alternative)

<details>
<summary>Click to expand manual setup instructions</summary>

**⚠️ Note for Windows users:** This project uses pandas which requires cmake on Windows. There are currently some setup issues on Windows that haven't been fully resolved yet. So, it's a work in progress.

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

HisaabFlow uses a modern, modular architecture:

```
HisaabFlow/
├── backend/                 # FastAPI backend
│   ├── api/                # API endpoints (modular)
│   ├── services/           # Business logic
│   ├── csv_parser/         # Bank statement parsing
│   ├── transfer_detection/ # Transfer matching algorithms
│   └── models/             # Data models (Pydantic)
├── frontend/               # React + Electron frontend
│   ├── src/components/     # React components
│   ├── src/services/       # API communication
│   └── public/             # Electron main process
├── configs/                # Bank configuration files
├── sample_data/            # Example bank statements
└── start_app.sh           # One-command launcher
```

## Configuration

### Bank Configuration
HisaabFlow uses .conf files to support different bank formats. Here's the structure based on the actual NayaPay configuration:

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
| **Wise (TransferWise)** | USD | ✅ Full Support | `statement_20141677_USD_2025-01-04_2025-06-02.csv` |
| **Wise (TransferWise)** | EUR | ✅ Full Support | `statement_23243482_EUR_2025-01-04_2025-06-02.csv` |
| **Wise (TransferWise)** | PKR | ✅ Full Support | N/A |
| **Wise (TransferWise)** | HUF | ✅ Full Support | N/A |
| **NayaPay** | PKR | ✅ Full Support | `m-02-2025.csv` |
| **Erste Bank** | HUF | ✅ Full Support | `12345678-00000000-87654321_2025-06-01_2025-06-30.csv` |
| **Revolut** | Multiple | 🚧 Coming Next | In development |

**Planning to add your bank?** HisaabFlow's flexible .conf system is designed to support new banks, though it's currently experimental as each bank format has required adjustments to the universal parsing system so far.

## Workflow

### 1. File Upload
- Drag & drop CSV files or click to browse
- Automatic bank detection from file format and content
- Support for multiple files simultaneously

### 2. Configuration & Review
- Review detected bank configuration
- Preview parsed results in interactive table
- Change configs if needed

### 3. Review & Export
- View categorized transactions in interactive table
- Analyze transfer detection insights
- Export structured data in CSV format for budgeting apps

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

### Adding New Banks (Experimental)

**Note**: Adding new banks via .conf files is currently experimental. The three supported banks (Wise, NayaPay, Erste) required significant adjustments to make the parsing system more universal.

1. **Create Configuration File**
```bash
cp configs/nayapay.conf.template configs/yourbank.conf
```

2. **Configure Bank Detection**
```conf
[bank_info]
name = yourbank
file_patterns = yourbank,your_bank
filename_regex_patterns = ^yourbank.*\.csv$
detection_content_signatures = Unique Header,Bank Identifier
currency_primary = USD
```

3. **Set Column Mapping**
```conf
[column_mapping]
Date = Transaction Date
Amount = Amount
Title = Description
Note = Reference
Balance = Running Balance
```

4. **Add Description Cleaning Rules**
```conf
[description_cleaning]
# Transform merchant names and clean descriptions
merchant_pattern = Original Pattern.*|Clean Name
card_transaction = Card transaction at (.*?)\|.*|Card purchase at \1
```

5. **Configure Categorization**
```conf
[categorization]
grocery_store = Grocery
gas_station = Transportation
restaurant = Food
amazon = Shopping
```

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