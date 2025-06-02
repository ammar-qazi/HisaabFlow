# Bank Statement Parser

A desktop application for parsing and converting bank statement CSVs to a standardized format.

## Features

- 📁 **File Upload**: Drag & drop or click to upload CSV files
- 👀 **Preview**: View your CSV structure before processing
- 🎯 **Range Selection**: Define exactly where your data starts and ends
- 🔗 **Column Mapping**: Map your bank's columns to standard format
- 💾 **Templates**: Save configurations for reuse with same bank
- 📊 **Live Preview**: See transformations in real-time
- 📥 **Export**: Download converted data in Cashew format

## Target Format (Cashew)

The app converts bank statements to this standardized format:
```csv
Date,Amount,Category,Title,Note,Account
2025-06-01 08:08:35,-50,Groceries,Fruits and Vegetables,Paid with cash,NayaPay
```

## Quick Start

### Backend Setup (Python + FastAPI)

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the backend server**:
   ```bash
   python main.py
   ```
   
   The API will be available at: `http://127.0.0.1:8000`

### Frontend Setup (Electron + React)

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install Node.js dependencies**:
   ```bash
   npm install
   ```

3. **Start the development server**:
   ```bash
   npm run electron-dev
   ```

This will start both the React development server and the Electron app.

## How to Use

### Step 1: Upload CSV File
- Click or drag & drop your bank statement CSV file
- The app will automatically preview the file structure

### Step 2: Define Data Range
- **Start Row**: Row where your data headers begin (auto-detected)
- **End Row**: Last row with data (optional, defaults to end of file)
- **Start/End Column**: Define column range if needed

### Step 3: Map Columns
- Map your bank's column names to the standard format:
  - **Date**: Transaction date/timestamp
  - **Amount**: Transaction amount (positive or negative)
  - **Title**: Transaction description
  - **Note**: Transaction type or additional info
  - **Category**: Transaction category (optional)
  - **Account**: Bank/account name

### Step 4: Save Template (Optional)
- Save your configuration as a template
- Reuse for future files from the same bank

### Step 5: Export
- Review the converted data
- Download as CSV file

## Example: NayaPay Statement

For the included NayaPay sample:
1. **Data starts at row 13** (headers: TIMESTAMP, TYPE, DESCRIPTION, AMOUNT, BALANCE)
2. **Column mapping**:
   - Date ← TIMESTAMP
   - Amount ← AMOUNT
   - Title ← DESCRIPTION
   - Note ← TYPE
3. **Save as template**: "NayaPay_Format" for future use

## Project Structure

```
bank_statement_parser/
├── backend/                 # Python FastAPI backend
│   ├── main.py             # Main FastAPI application
│   ├── csv_parser.py       # Core parsing logic
│   ├── test_parser.py      # Test script
│   └── requirements.txt    # Python dependencies
├── frontend/               # Electron + React frontend
│   ├── src/
│   │   ├── App.js          # Main React component
│   │   ├── index.js        # React entry point
│   │   └── index.css       # Styles
│   ├── public/
│   │   ├── electron.js     # Electron main process
│   │   └── index.html      # HTML template
│   └── package.json        # Node.js dependencies
├── templates/              # Saved parsing templates
├── cashew_import.csv       # Target format example
└── nayapay_statement.csv   # Sample bank statement
```

## API Endpoints

The backend provides these REST API endpoints:

- `POST /upload` - Upload CSV file
- `GET /preview/{file_id}` - Preview file structure
- `GET /detect-range/{file_id}` - Auto-detect data range
- `POST /parse-range/{file_id}` - Parse specific range
- `POST /transform` - Transform to Cashew format
- `POST /export` - Export as CSV
- `POST /save-template` - Save parsing template
- `GET /templates` - List saved templates
- `GET /template/{name}` - Load specific template

## Building for Production

### Backend
```bash
cd backend
pip install -r requirements.txt
python main.py
```

### Frontend
```bash
cd frontend
npm run build
npm run electron-pack
```

This creates a distributable desktop app in the `dist/` folder.

## Adding New Bank Formats

1. **Upload a sample CSV** from the new bank
2. **Use the app** to define the data range and column mapping
3. **Save as a template** with a descriptive name (e.g., "Chase_Checking")
4. **Share the template** by copying the JSON file from `templates/` folder

## Troubleshooting

### Common Issues

**Backend won't start**:
- Check Python version (3.8+ required)
- Install dependencies: `pip install -r requirements.txt`
- Check port 8000 is available

**Frontend won't start**:
- Check Node.js version (14+ required)
- Install dependencies: `npm install`
- Check port 3000 is available

**File upload fails**:
- Ensure CSV file is properly formatted
- Check file size (large files may need chunking)
- Verify backend is running

**Date parsing issues**:
- Check date format in your CSV
- Modify date parsing logic in `csv_parser.py` if needed

### Need Help?

1. Check the console for error messages
2. Verify both backend and frontend are running
3. Test with the included NayaPay sample file first
4. Check the `templates/` folder for saved configurations

## Contributing

Feel free to:
- Add support for new bank formats
- Improve date/amount parsing
- Enhance the UI/UX
- Add new export formats
- Optimize performance

The codebase is modular and well-documented for easy extension.
