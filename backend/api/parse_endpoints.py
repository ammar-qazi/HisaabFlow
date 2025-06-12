"""
CSV parsing endpoints with preprocessing layer
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import sys

# Add paths for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from enhanced_csv_parser import EnhancedCSVParser
    from robust_csv_parser import RobustCSVParser
    from data_cleaner import DataCleaner
    from bank_detection import BankDetector, BankConfigManager
    from csv_preprocessing.csv_preprocessor import CSVPreprocessor  # 🔧 NEW: Import preprocessor
except ImportError:
    # Fallback path for import issues
    backend_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, backend_path)
    from enhanced_csv_parser import EnhancedCSVParser
    from robust_csv_parser import RobustCSVParser
    from data_cleaner import DataCleaner
    from bank_detection import BankDetector, BankConfigManager
    from csv_preprocessing.csv_preprocessor import CSVPreprocessor  # 🔧 NEW: Import preprocessor

# Import file helper function
try:
    from api.file_endpoints import get_uploaded_file
except ImportError:
    # Fallback implementation
    def get_uploaded_file(file_id):
        # This will be populated by file_endpoints when it loads
        return None

parse_router = APIRouter()

# Initialize parsers, bank detection, and preprocessor
enhanced_parser = EnhancedCSVParser()
robust_parser = RobustCSVParser()
data_cleaner = DataCleaner()
bank_config_manager = BankConfigManager()
bank_detector = BankDetector(bank_config_manager)
csv_preprocessor = CSVPreprocessor()  # 🔧 NEW: Initialize preprocessor

class ParseRangeRequest(BaseModel):
    start_row: int
    end_row: Optional[int] = None
    start_col: int = 0
    end_col: Optional[int] = None
    encoding: str = "utf-8"
    enable_cleaning: bool = True

class MultiCSVParseRequest(BaseModel):
    file_ids: List[str]
    parse_configs: List[Dict[str, Any]]
    user_name: str = "Ammar Qazi"
    date_tolerance_hours: int = 24
    enable_cleaning: bool = True

@parse_router.get("/preview/{file_id}")
async def preview_csv(file_id: str, encoding: str = "utf-8", header_row: int = None):
    """Preview uploaded CSV file with bank-aware header detection"""
    print(f"🕵️‍♂️ Preview request for file_id: {file_id}, header_row: {header_row}")
    
    file_info = get_uploaded_file(file_id)
    if not file_info:
        print(f"❌ File {file_id} not found")
        raise HTTPException(status_code=404, detail="File not found")
    
    file_path = file_info["temp_path"]
    filename = file_info["original_name"]
    
    try:
        # 🔍 STEP 1: Detect bank first for header detection
        print(f"🔍 Step 1: Detecting bank for header detection...")
        
        # Read first few lines for bank detection
        preview_result = robust_parser.preview_csv(file_path, encoding, header_row=0)
        if not preview_result['success']:
            raise HTTPException(status_code=400, detail=preview_result['error'])
        
        # Extract content for bank detection
        preview_data = preview_result['preview_data']
        content_lines = []
        headers_detected = []
        
        for row in preview_data[:10]:  # Use first 10 rows for detection
            row_text = ' '.join([str(cell) for cell in row.values() if cell])
            content_lines.append(row_text)
            
            # Also collect potential headers
            row_values = list(row.values())
            if row_values and any(cell for cell in row_values):
                headers_detected = row_values
        
        content_for_detection = '\n'.join(content_lines)
        
        # Detect bank using filename and content
        bank_detection = bank_detector.detect_bank(filename, content_for_detection, headers_detected)
        print(f"🏦 Detected bank: {bank_detection.bank_name} (confidence: {bank_detection.confidence:.2f})")
        
        # 🔍 STEP 2: Use bank-specific header detection if available
        detected_header_row = header_row
        header_detection_info = None
        
        if bank_detection.bank_name != 'unknown' and bank_detection.confidence > 0.5:
            print(f"🔍 Step 2: Using bank-specific header detection for {bank_detection.bank_name}")
            header_detection_result = bank_config_manager.detect_header_row(
                file_path, bank_detection.bank_name, encoding
            )
            
            if header_detection_result['success']:
                detected_header_row = header_detection_result['header_row']
                header_detection_info = header_detection_result
                print(f"📋 Bank-specific header detection: row {detected_header_row}")
            else:
                print(f"⚠️ Bank-specific header detection failed: {header_detection_result.get('error', 'Unknown error')}")
        
        # 🔍 STEP 3: Generate enhanced preview with proper headers
        print(f"🔍 Step 3: Generating enhanced preview with header_row={detected_header_row}")
        
        # Use the detected header row for the final preview
        result = robust_parser.preview_csv(file_path, encoding, detected_header_row)
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        
        # 🆕 Add bank detection and header detection info to response
        result['bank_detection'] = {
            'detected_bank': bank_detection.bank_name,
            'confidence': bank_detection.confidence,
            'reasons': bank_detection.reasons
        }
        
        if header_detection_info:
            result['header_detection'] = header_detection_info
            result['suggested_header_row'] = header_detection_info['header_row']
            result['suggested_data_start_row'] = header_detection_info['data_start_row']
        
        print(f"✅ Enhanced preview completed with {len(result['column_names'])} columns")
        return result
        
    except Exception as e:
        print(f"❌ Preview exception: {str(e)}")
        import traceback
        print(f"📚 Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@parse_router.get("/detect-range/{file_id}")
async def detect_data_range(file_id: str, encoding: str = "utf-8"):
    """Auto-detect data range in CSV"""
    print(f"🔍 Detect range request for file_id: {file_id}")
    
    file_info = get_uploaded_file(file_id)
    if not file_info:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_path = file_info["temp_path"]
    
    try:
        result = robust_parser.detect_data_range(file_path, encoding)
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
        return result
    except Exception as e:
        print(f"❌ Detect range exception: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@parse_router.post("/parse-range/{file_id}")
async def parse_range(file_id: str, request: ParseRangeRequest):
    """Parse CSV with specified range and data cleaning"""
    print(f"🕵️‍♂️ Parse range request for file_id: {file_id}")
    print(f"🧹 Data cleaning enabled: {request.enable_cleaning}")
    
    file_info = get_uploaded_file(file_id)
    if not file_info:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_path = file_info["temp_path"]
    
    try:
        # Parse with enhanced parser
        parse_result = enhanced_parser.parse_with_range(
            file_path, 
            request.start_row, 
            request.end_row, 
            request.start_col, 
            request.end_col, 
            request.encoding
        )
        
        if not parse_result['success']:
            raise HTTPException(status_code=400, detail=parse_result['error'])
        
        # 🔍 BANK DETECTION ON RAW DATA (BEFORE CLEANING) - Single File
        print(f"🔍 Detecting bank for single file using RAW CSV data...")
        detection_result = bank_detector.detect_bank_from_data(
            file_info['original_name'], 
            parse_result['data']
        )
        print(f"🎯 Single file bank detected: {detection_result.bank_name} (confidence={detection_result.confidence:.2f})")
        
        # Store bank detection info
        bank_info = {
            'detected_bank': detection_result.bank_name,
            'confidence': detection_result.confidence,
            'reasons': detection_result.reasons,
            'original_headers': parse_result.get('headers', [])
        }
        
        # Apply data cleaning if enabled
        final_result = parse_result
        if request.enable_cleaning:
            print(f"🧹 Applying data cleaning...")
            
            # 🏦 CREATE BANK-SPECIFIC CLEANING CONFIG
            bank_cleaning_config = None
            if bank_info['detected_bank'] != 'unknown':
                bank_column_mapping = bank_config_manager.get_column_mapping(bank_info['detected_bank'])
                bank_cleaning_config = {
                    'column_mapping': bank_column_mapping,
                    'bank_name': bank_info['detected_bank']
                }
                print(f"🗺️ Using bank-specific cleaning config: {bank_cleaning_config}")
            
            cleaning_result = data_cleaner.clean_parsed_data(parse_result, bank_cleaning_config)
            
            if cleaning_result['success']:
                final_result = {
                    'success': True,
                    'headers': [col for col in cleaning_result['data'][0].keys()] if cleaning_result['data'] else [],
                    'data': cleaning_result['data'],
                    'row_count': cleaning_result['row_count'],
                    'cleaning_applied': True,
                    'cleaning_summary': cleaning_result['cleaning_summary'],
                    'updated_column_mapping': cleaning_result.get('updated_column_mapping', {}),
                    'original_headers': parse_result.get('headers', []),
                    'bank_info': bank_info  # 🏦 ADD BANK INFO TO SINGLE FILE TOO
                }
                print(f"✅ Data cleaning successful")
            else:
                print(f"⚠️  Data cleaning failed, using uncleaned data")
                final_result['cleaning_applied'] = False
                final_result['bank_info'] = bank_info  # 🏦 ADD BANK INFO EVEN IF CLEANING FAILS
        else:
            final_result['cleaning_applied'] = False
            final_result['bank_info'] = bank_info  # 🏦 ADD BANK INFO TO UNCLEANED DATA
        
        return final_result
        
    except Exception as e:
        print(f"❌ Parse exception: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@parse_router.post("/multi-csv/parse")
async def parse_multiple_csvs(request: MultiCSVParseRequest):
    """Parse multiple CSV files"""
    print(f"🚀 Multi-CSV parse request for {len(request.file_ids)} files")
    print(f"🧹 Data cleaning enabled: {request.enable_cleaning}")
    
    try:
        # Validate all file IDs exist
        for file_id in request.file_ids:
            if not get_uploaded_file(file_id):
                raise HTTPException(status_code=404, detail=f"File {file_id} not found")
        
        if len(request.file_ids) != len(request.parse_configs):
            raise HTTPException(status_code=400, detail="Number of file IDs must match number of parse configs")
        
        results = []
        
        # Process each file
        for i, file_id in enumerate(request.file_ids):
            print(f"📁 Processing file {i+1}/{len(request.file_ids)}: {file_id}")
            
            file_info = get_uploaded_file(file_id)
            file_path = file_info["temp_path"]
            config = request.parse_configs[i]
            
            # 🔧 NEW: STEP 1 - GENERIC CSV PREPROCESSING
            print(f"🔧 Step 1: Generic CSV preprocessing (bank-agnostic)")
            
            # Apply generic CSV preprocessing (fixes multiline fields, encoding, etc.)
            preprocessing_result = csv_preprocessor.preprocess_csv(
                file_path, 
                'generic',  # Bank-agnostic preprocessing
                config.get('encoding', 'utf-8')
            )
            
            # Use preprocessed file if successful, otherwise use original
            actual_file_path = file_path
            preprocessing_info = {'applied': False}
            
            if preprocessing_result['success'] and preprocessing_result['issues_fixed']:
                actual_file_path = preprocessing_result['processed_file_path']
                preprocessing_info = {
                    'applied': True,
                    'issues_fixed': preprocessing_result['issues_fixed'],
                    'original_rows': preprocessing_result['original_rows'],
                    'processed_rows': preprocessing_result['processed_rows']
                }
                print(f"✅ Generic preprocessing applied: {len(preprocessing_result['issues_fixed'])} issues fixed")
                print(f"   📊 Rows: {preprocessing_result['original_rows']} → {preprocessing_result['processed_rows']}")
            else:
                print(f"📝 Generic preprocessing skipped (no issues found)")
            
            # 🔧 STEP 2: BANK DETECTION FOR PROPER PARSING
            print(f"🔧 Step 2: Detecting bank for proper parsing of {file_info['original_name']}")
            
            # Detect bank on cleaned file (should be more accurate now)
            bank_detection = bank_detector.detect_bank(file_info['original_name'], "", [])
            header_row = None
            data_start_row = config.get('start_row', 0)
            
            
            if bank_detection.bank_name != 'unknown' and bank_detection.confidence > 0.1:
                print(f"🏦 Bank detected: {bank_detection.bank_name} (confidence: {bank_detection.confidence:.2f})")
                
                # 🔧 DYNAMIC HEADER DETECTION: Find headers in preprocessed file
                print(f"🔧 Finding headers dynamically in preprocessed file")
                header_row = None
                data_start_row = config.get('start_row', 0)
                
                try:
                    with open(actual_file_path, 'r', encoding='utf-8-sig') as f:
                        lines = f.readlines()
                    
                    # Look for the characteristic headers based on bank type
                    header_patterns = {
                        'nayapay': ['TIMESTAMP', 'TYPE', 'DESCRIPTION'],
                        'wise_usd': ['Date', 'Amount', 'Description'],
                        'wise_eur': ['Date', 'Amount', 'Description'],
                        'wise_huf': ['Date', 'Amount', 'Description']
                    }
                    
                    patterns = header_patterns.get(bank_detection.bank_name, ['Date', 'Amount'])
                    
                    for i, line in enumerate(lines):
                        line_upper = line.upper()
                        if all(pattern.upper() in line_upper for pattern in patterns):
                            header_row = i
                            data_start_row = i + 1
                            print(f"🔧 Found headers at row {header_row} in preprocessed file")
                            print(f"🔧 Headers: {line.strip()}")
                            break
                    
                    if header_row is None:
                        print(f"⚠️ Could not find headers in preprocessed file, using manual config")
                        
                except Exception as e:
                    print(f"⚠️ Header detection failed: {e}")
            else:
                print(f"📝 Using manual config for unknown bank")
            
            # 🔧 STEP 3: PARSE WITH ENHANCED PARSER
            print(f"🔧 Step 3: Parsing with enhanced parser")
            
            # Parse with enhanced parser using proper header/data separation
            parse_result = enhanced_parser.parse_with_range(
                actual_file_path,  # Use preprocessed file
                data_start_row,  # Use bank-detected data start row
                config.get('end_row'),
                config.get('start_col', 0),
                config.get('end_col'),
                config.get('encoding', 'utf-8'),
                header_row  # Pass separate header row
            )
            
            if not parse_result['success']:
                raise HTTPException(status_code=400, detail=f"Failed to parse {file_info['original_name']}: {parse_result.get('error', 'Unknown error')}")
            
            # 🔍 STEP 4: FINAL BANK DETECTION ON PARSED DATA
            print(f"🔍 Step 4: Final bank detection on parsed data for {file_info['original_name']}")
            detection_result = bank_detector.detect_bank_from_data(
                file_info['original_name'], 
                parse_result['data']
            )
            print(f"🎯 Final bank detected: {detection_result.bank_name} (confidence={detection_result.confidence:.2f})")
            print(f"📋 Detection reasons: {detection_result.reasons}")
            
            # Store comprehensive bank detection info
            bank_info = {
                'detected_bank': detection_result.bank_name,
                'confidence': detection_result.confidence,
                'reasons': detection_result.reasons,
                'original_headers': parse_result.get('headers', []),
                'preprocessing_applied': preprocessing_info['applied'],
                'preprocessing_info': preprocessing_info
            }
            
            # Apply data cleaning if enabled
            final_result = parse_result
            if request.enable_cleaning:
                print(f"🧹 Applying data cleaning to {file_info['original_name']}...")
                
                # 🏦 CREATE BANK-SPECIFIC CLEANING CONFIG
                bank_cleaning_config = None
                if bank_info['detected_bank'] != 'unknown':
                    bank_column_mapping = bank_config_manager.get_column_mapping(bank_info['detected_bank'])
                    bank_cleaning_config = {
                        'column_mapping': bank_column_mapping,
                        'bank_name': bank_info['detected_bank']
                    }
                    print(f"🗺️ Using bank-specific cleaning config for {bank_info['detected_bank']}: {bank_cleaning_config}")
                
                cleaning_result = data_cleaner.clean_parsed_data(parse_result, bank_cleaning_config)
                
                if cleaning_result['success']:
                    final_result = {
                        'success': True,
                        'headers': [col for col in cleaning_result['data'][0].keys()] if cleaning_result['data'] else [],
                        'data': cleaning_result['data'],
                        'row_count': cleaning_result['row_count'],
                        'cleaning_applied': True,
                        'cleaning_summary': cleaning_result['cleaning_summary'],
                        'updated_column_mapping': cleaning_result.get('updated_column_mapping', {}),
                        'original_headers': parse_result.get('headers', []),
                        'bank_info': bank_info  # 🏦 ADD BANK DETECTION INFO
                    }
                    print(f"✅ Data cleaning successful: {cleaning_result['row_count']} clean rows")
                else:
                    print(f"⚠️  Data cleaning failed, using uncleaned data")
                    final_result['cleaning_applied'] = False
                    final_result['bank_info'] = bank_info  # 🏦 ADD BANK INFO EVEN IF CLEANING FAILS
            else:
                final_result['cleaning_applied'] = False
                final_result['bank_info'] = bank_info  # 🏦 ADD BANK INFO TO UNCLEANED DATA
            
            results.append({
                "file_id": file_id,
                "file_name": file_info["original_name"],
                "parse_result": final_result,
                "config": config,
                "data": final_result['data'],
                "bank_info": bank_info  # 🏦 ADD BANK DETECTION INFO
            })
        
        print(f"🎉 Successfully parsed all {len(results)} files")
        return {
            "success": True,
            "parsed_csvs": results,
            "total_files": len(results)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Multi-CSV parse exception: {str(e)}")
        import traceback
        print(f"📖 Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))
