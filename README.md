# HisaabFlow

Many of us want to track our expenses, but life gets in the way. A day passes, then a week, then a month, and suddenly you're staring at a pile of bank statements from different accounts, currencies, and formats that would take hours to organize manually.

I built HisaabFlow because I got tired of spending more time wrestling with CSV files than I did traveling. Now I just upload, click, and get back to the important stuff.

## What It Does

HisaabFlow takes whatever messy CSV your bank gives you and converts it into clean, organized data. No more copying and pasting between spreadsheets or trying to remember if that $50 charge was groceries or dining.

Right now it converts everything to work with Cashew (the expense tracker I use), but the whole system is built around simple configuration files.

## Features

- **🎯 Smart Bank Detection**: Recognizes your bank from the CSV filename
- **⚙️ Configuration-Based**: No hardcoded bank rules, everything's customizable through simple .conf files
- **🔄 Transfer Detection**: Finds matching transfers between different accounts (like Wise to NayaPay)
- **🏷️ Auto-Categorization**: Your groceries stay groceries, your rent stays rent
- **💱 Multi-Currency Support**: Handles different Wise currency pockets separately
- **📋 Reusable Configs**: Set up once per bank, use forever
- **🖥️ Desktop App**: Runs locally; your financial data never leaves your computer

## Target Format (Cashew)

HisaabFlow converts everything to this clean, standardized format:

```csv
Date,Amount,Category,Title,Note,Account
2025-06-01 08:08:35,-50,Groceries,Fruits and Vegetables,Paid with cash,NayaPay
2025-06-01 12:30:00,2500,Income,Salary Transfer,Monthly salary,Wise USD
```

Six simple columns that work with most personal finance tools, spreadsheets, or whatever system you prefer.

## Quick Start

### What You Need

- Python 3.8+ (for the backend)
- Node.js 14+ (for the desktop app)
- A few minutes to set up your bank configurations

### Start the App

```bash
./start_app.sh
```

That's it. The script handles installing dependencies and starting both the backend and desktop app. The first time takes a minute while everything installs and loads.

## How to Use It

### First Time: Set Up Your Banks

1. **Copy the configuration templates:**
   ```bash
   cp configs/app.conf.template configs/app.conf
   cp configs/wise_usd.conf.template configs/wise_usd.conf
   # Copy templates for any banks you use
   ```

2. **Edit your personal info in `configs/app.conf`:**
   ```ini
   [general]
   user_name = Your Name  # Used for transfer detection
   ```

3. **Update bank configs with your real merchants:**
   ```ini
   [categorization]
   # Replace template examples with YOUR merchants
   Amazon.com = Shopping
   Your Local Grocery = Groceries
   Your Workplace = Income
   ```

### Daily Use: Convert Your Statements

1. **Upload your CSV**: Drag and drop or click to upload
2. **Preview and confirm**: The app shows what it detected
3. **Export**: Download your clean, categorized data

That's it. The configuration you set up once handles everything on its own.

### Example: Setting Up NayaPay

If you use NayaPay, copy the template and customize it:

```bash
cp configs/nayapay.conf.template configs/nayapay.conf
```

Then edit the categorization section with your actual merchants:

```ini
[categorization]
# Your real merchants, not the template examples
Careem = Transportation
Al-Fatah = Groceries
Dominos = Dining
```

Now every NayaPay CSV you upload will categorize these merchants correctly.

## How to Add Your Own .conf File

Got a bank that's not supported yet? Here's how to add it:

### 1. Create the Configuration File

Start with a basic template:

```ini
[bank_info]
name = your_bank_name
file_patterns = yourbank,your_bank  # Keywords that appear in CSV filenames
currency_primary = USD
cashew_account = Your Bank Name # Account name in Cashew

[csv_config]
delimiter = ,
has_header = true
date_format = %Y-%m-%d

[column_mapping]
Date = Date
Amount = Amount  
Title = Description
Note = Payment Reference # Or Note
```

### 2. Map Your CSV Columns

Look at your bank's CSV file and map the columns:

- **Date**: Whatever column has the transaction date
- **Amount**: The money column (positive/negative values)
- **Title**: Transaction description 
- **Note**: Payment reference or similar
- **Account**: (Optional to use for currency comparions)

### 3. Add Your Merchants

```ini
[categorization]
Your Grocery Store = Groceries
Your Favorite Restaurant = Dining
Your Workplace = Income
Your Landlord = Rent
```

### 4. Test It

Upload a CSV file and see if the detection and categorization work. Tweak the patterns as needed.

The configuration system is forgiving. You can adjust things as you learn how your bank formats their data. You can also ask any of the LLMs to help with it since they can understand .conf files. 

## Project Structure

```
HisaabFlow/
├── backend/                 # Python FastAPI backend
│   ├── main.py             # Main server
│   ├── api/                # Modular API endpoints
│   └── requirements.txt    # Python dependencies
├── frontend/               # Electron + React desktop app
│   ├── src/App.js          # Main interface
│   ├── public/electron.js  # Desktop app wrapper
│   └── package.json        # Node dependencies
├── configs/                # Bank configurations
│   ├── *.conf.template     # Public templates
│   └── *.conf              # Your personal configs (git-ignored)
└── sample_data/            # Example CSV files for testing
```

The configuration files live in `configs/` and contain all the bank-specific rules. Your personal `.conf` files are ignored by git, so your real merchant data stays private.

## Supported Banks

HisaabFlow includes templates for:

- **Wise** (USD, EUR, HUF, PKR currency pockets)
- **NayaPay** (Pakistani digital wallet)
- **Erste Bank** (Hungarian bank)

But the power is in the configuration system. You can add any bank by creating a simple `.conf` file.

## Future Plans

Here's what's coming next:

### Near Term
- **Revolut support**
- **PDF parsing** for banks that don't provide CSV exports
- **More output formats** beyond Cashew
- **Date range filtering** for partial exports

### Longer Term  
- **Improved frontend** with better UX
- **More modular codebase** for easier contributions
- **Bank detection** from CSV content
- **Rule suggestions** based on transaction patterns

## Contributing

Want to help make HisaabFlow better? Here are the best ways:

### 🐛 Bug Reports
Found something broken? Open an issue with:
- What you were trying to do
- What happened instead
- Your bank/CSV format if relevant

### 🏦 Bank Statement Contributions

This is the most valuable contribution. If you want HisaabFlow to support your bank:

1. **Download a CSV statement** from your bank
2. **Anonymize it** by replacing:
   - Your real name with "John Smith"
   - Real merchant names with generic ones ("Local Grocery", "Coffee Shop", etc.)
   - Account numbers with fake ones
   - Keep the structure and formatting identical
3. **Share it** via GitHub issue or email

I'll create the `.conf` file and template so other users with your bank can benefit right away.

### 💻 Code Contributions

The codebase is modular and well-documented. Feel free to:
- Add new features to the configuration system
- Improve the desktop app interface  
- Optimize parsing performance
- Add new export formats

## Privacy & Security

Your financial data never leaves your computer. HisaabFlow runs entirely locally:

- **No cloud processing**: Everything happens on your machine
- **No data transmission**: CSV files stay in your local folders
- **Private configurations**: Your `.conf` files with real merchant names are git-ignored
- **Open source**: You can audit exactly what the code does

The only thing that gets shared publicly are the anonymized `.conf.template` files that help other users set up their banks.

## Need Help?

### Common Issues

**"Unknown bank type" error**: Create a `.conf` file for your bank or check that the `file_patterns` match your CSV filename.

**Transfers not detected**: Make sure your `user_name` in `app.conf` matches exactly how it appears in your bank statements.

**Wrong categorization**: Add or update the merchant names in your bank's `.conf` file.

### Getting Support

- Check the sample configurations in `configs/` for examples
- Test with the included sample data first
- Open a GitHub issue for bugs or feature requests

The configuration system is flexible. Most issues can be solved by tweaking a `.conf` file rather than changing code.

---

HisaabFlow turns the tedious job of organizing bank statements into a one-click process. Set it up once, use it forever, and never categorize transactions by hand again.
