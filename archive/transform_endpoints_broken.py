"""
Data transformation endpoints
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import json
import os
import sys
import csv
import io
from fastapi.responses import StreamingResponse

# Add paths for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from enhanced_csv_parser import EnhancedCSVParser
    from bank_detection import BankDetector, BankConfigManager
except ImportError:
    # Fallback path for import issues
    backend_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, backend_path)
    from enhanced_csv_parser import EnhancedCSVParser
    from bank_detection import BankDetector, BankConfigManager

transform_router = APIRouter()

# Initialize parser and bank detection
enhanced_parser = EnhancedCSVParser()
bank_config_manager = BankConfigManager()
bank_detector = BankDetector(bank_config_manager)

class TransformRequest(BaseModel):
    data: List[Dict[str, Any]]
    column_mapping: Dict[str, str]
    bank_name: str = ""
    categorization_rules: Optional[List[Dict[str, Any]]] = None
    default_category_rules: Optional[Dict[str, str]] = None
    account_mapping: Optional[Dict[str, str]] = None

@transform_router.post("/transform")
async def transform_data(request: TransformRequest):
    """Transform data to Cashew format"""
    try:
        if request.categorization_rules or request.default_category_rules:
            result = enhanced_parser.transform_to_cashew(
                request.data, 
                request.column_mapping, 
                request.bank_name,
                request.categorization_rules,
                request.default_category_rules,
                getattr(request, 'account_mapping', None)
            )
        else:
            result = enhanced_parser.transform_to_cashew(
                request.data, 
                request.column_mapping, 
                request.bank_name
            )
        return {
            "success": True,
            "data": result,
            "row_count": len(result)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@transform_router.post("/multi-csv/transform")
async def transform_multi_csv_data(request: Request):
    """Transform multi-CSV data to Cashew format"""
    print(f"🔄 Multi-CSV transform request received")
    
    try:
        # Get raw request body for debugging
        body = await request.body()
        print(f"📖 Raw request body size: {len(body)} bytes")
        
        # Parse JSON manually for debugging
        raw_data = json.loads(body)
        print(f"🗂️ Request keys: {list(raw_data.keys())}")
        
        # Extract data from frontend format using bank-agnostic detection
        data, column_mapping, bank_name = _extract_transform_data_per_bank(raw_data)
        
        print(f"📈 Final data length: {len(data)}")
        print(f"🏦 Final bank name: {bank_name}")
        print(f"🗂️ Final column mapping: {column_mapping}")
        
        # Get categorization rules
        categorization_rules = raw_data.get('categorization_rules')
        default_category_rules = raw_data.get('default_category_rules')
        account_mapping = raw_data.get('account_mapping')
        
        # Show sample data for debugging
        if data:
            print(f"📄 Sample data (first row): {data[0] if data else 'none'}")
        
        # Transform data
        if categorization_rules or default_category_rules:
            print(f"📋 Using enhanced transformation with categorization rules")
            result = enhanced_parser.transform_to_cashew(
                data, 
                column_mapping, 
                bank_name,
                categorization_rules,
                default_category_rules,
                account_mapping
            )
        else:
            print(f"📋 Using basic transformation")
            result = enhanced_parser.transform_to_cashew(
                data, 
                column_mapping, 
                bank_name
            )
        
        print(f"✅ Transformation successful: {len(result)} rows transformed")
        if result:
            print(f"📄 Sample result (first row): {result[0] if result else 'none'}")
        
        # Frontend expects 'transformed_data' and 'transfer_analysis' format
        response_data = {
            "success": True,
            "transformed_data": result,  # ← Frontend expects this key
            "transformation_summary": {
                "total_transactions": len(result),
                "bank_name": bank_name,
                "data_source": "multi-csv"
            },
            "transfer_analysis": {  # ← Frontend expects this key
                "summary": {
                    "transfer_pairs_found": 0,
                    "potential_transfers": 0,
                    "conflicts": 0,
                    "flagged_for_review": 0
                },
                "transfers": [],
                "conflicts": []
            },
            # Legacy fields for compatibility
            "data": result,
            "row_count": len(result),
            "bank_name": bank_name
        }
        
        print(f"📦 Sending response with {len(result)} transformed_data rows")
        return response_data
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {str(e)}")
        raise HTTPException(status_code=422, detail=f"Invalid JSON: {str(e)}")
    except Exception as e:
        print(f"❌ Multi-CSV transform exception: {str(e)}")
        import traceback
        print(f"📖 Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

def _extract_transform_data_per_bank(raw_data: dict):
    """Extract transformation data using PRE-DETECTED bank info from parse endpoints"""
    
    # Handle different frontend data formats
    if 'csv_data_list' in raw_data:
        print(f"📋 Frontend format detected: csv_data_list")
        csv_data_list = raw_data.get('csv_data_list', [])
        print(f"📈 CSV data list length: {len(csv_data_list)}")
        
        # 🔍 DEBUG: Show raw_data structure for debugging
        print(f"🔍 Raw data top-level keys: {list(raw_data.keys())}")
        if csv_data_list and len(csv_data_list) > 0:
            print(f"🔍 First CSV item keys: {list(csv_data_list[0].keys())}")
            if 'bank_info' in csv_data_list[0]:
                print(f"🔍 First CSV bank_info: {csv_data_list[0]['bank_info']}")
            else:
                print(f"🔍 No bank_info found in first CSV item")
        
        if not csv_data_list:
            print(f"⚠️ No CSV data found in csv_data_list")
            return [], {}, ''
        
        # Process each CSV file using PRE-CLEANED data (no more mapping needed)
        all_transformed_data = []
        
        for csv_index, csv_data in enumerate(csv_data_list):
            print(f"\n🗂️ Processing CSV {csv_index + 1}/{len(csv_data_list)}")
            
            # 🔍 DEBUG: Show complete csv_data structure
            print(f"   🔍 CSV data keys: {list(csv_data.keys())}")
            
            # Get data from this CSV
            csv_file_data = csv_data.get('data', [])
            filename = csv_data.get('filename', f'file_{csv_index + 1}.csv')
            bank_info = csv_data.get('bank_info', {})  # 🏦 GET PRE-DETECTED BANK INFO
            
            # 🔍 DEBUG: Show bank_info in detail
            print(f"   🔍 Raw bank_info: {bank_info}")
            print(f"   🔍 Bank_info type: {type(bank_info)}")
            if bank_info:
                print(f"   🔍 Bank_info keys: {list(bank_info.keys())}")
                print(f"   🔍 Detected bank: {bank_info.get('detected_bank', 'none')}")
                print(f"   🔍 Confidence: {bank_info.get('confidence', 0.0)}")
            else:
                print(f"   ⚠️  Bank_info is empty or None!")
            
            if not csv_file_data:
                print(f"   ⚠️ No data in CSV {csv_index + 1}")
                continue
                
            print(f"   📊 CSV has {len(csv_file_data)} rows")
            print(f"   📁 Filename: {filename}")
            
            # 🎯 LOG PRE-DETECTED BANK INFO (for debugging)
            detected_bank = 'unknown'
            if bank_info:
                detected_bank = bank_info.get('detected_bank', 'unknown')
                confidence = bank_info.get('confidence', 0.0)
                original_headers = bank_info.get('original_headers', [])
                print(f"   🏦 PRE-DETECTED bank: {detected_bank} (confidence={confidence:.2f})")
                print(f"   📋 Original headers were: {original_headers}")
            else:
                print(f"   ⚠️ No bank_info found in data")
            
            # ✅ DATA IS ALREADY CLEANED AND STANDARDIZED - NO MORE MAPPING NEEDED!
            print(f"   ✅ Using pre-cleaned data as-is (already bank-specific cleaned)")
            if csv_file_data:
                cleaned_headers = list(csv_file_data[0].keys())
                print(f"   🧹 Cleaned headers: {cleaned_headers}")
                print(f"   📄 Sample cleaned row: {csv_file_data[0]}")
            
            # 🏦 Set the correct Account field based on detected bank
            bank_display_names = {
                'nayapay': 'NayaPay',
                'wise_usd': 'Wise USD', 
                'wise_eur': 'Wise EUR',
                'wise_huf': 'Wise HUF',
                'unknown': filename.replace('.csv', '').replace('_', ' ').title()
            }
            
            # 🔍 ENHANCED DEBUGGING FOR ACCOUNT FIELD LOGIC
            print(f"   🔍 Account field logic:")
            print(f"       - Detected bank: '{detected_bank}'")
            print(f"       - Filename: '{filename}'")
            print(f"       - Bank display names available: {list(bank_display_names.keys())}")
            
            if detected_bank and detected_bank != 'unknown':
                account_name = bank_display_names.get(detected_bank, detected_bank.title())
                print(f"       - Using detected bank mapping: '{detected_bank}' -> '{account_name}'")
            else:
                account_name = filename.replace('.csv', '').replace('_', ' ').replace('-', ' ').title()
                print(f"       - Using filename fallback: '{filename}' -> '{account_name}'")
                
            print(f"   🏦 Final Account field will be set to: '{account_name}'")
            
            # 🔍 Count how many rows will be updated
            if csv_file_data:
                print(f"   🔍 Will update Account field for {len(csv_file_data)} rows")
            
            # Update Account field for each row with correct bank name
            for row_index, row in enumerate(csv_file_data):
                row['Account'] = account_name
                # 🔍 DEBUG: Show first few Account field assignments
                if row_index < 3:
                    print(f"       - Row {row_index + 1}: Account = '{row.get('Account', 'NOT_SET')}'")
            
            print(f"   ✅ Account field updated for all {len(csv_file_data)} rows")
            
            # Add cleaned data to combined results
            all_transformed_data.extend(csv_file_data)
            print(f"   ✅ Added {len(csv_file_data)} rows to combined data (total now: {len(all_transformed_data)})"))"
                
        print(f"\n📈 Combined data from all CSVs: {len(all_transformed_data)} total rows")
        
        # 🔍 DEBUG: Verify Account fields in final combined data
        if all_transformed_data:
            account_values = set()
            for row in all_transformed_data[:10]:  # Check first 10 rows
                account_values.add(row.get('Account', 'MISSING'))
            print(f"🔍 Final combined data Account field values: {list(account_values)}")
            print(f"🔍 Final combined data sample row: {all_transformed_data[0]}")
        
        # Use standard mapping since all data is already standardized
        combined_column_mapping = {
            'Date': 'Date',
            'Amount': 'Amount',
            'Title': 'Title', 
            'Note': 'Note',
            'Balance': 'Balance'
        }
        
        # Use first detected bank name or default
        combined_bank_name = 'multi_bank_combined'
        
        return all_transformed_data, combined_column_mapping, combined_bank_name
        
    else:
        # Standard single-file format
        print(f"📋 Standard format detected")
        data = raw_data.get('data', [])
        column_mapping = raw_data.get('column_mapping', {})
        bank_name = raw_data.get('bank_name', '')
        
        return data, column_mapping, bank_name

def _create_fallback_mapping(sample_row: dict) -> dict:
    """Create a fallback column mapping when bank detection fails"""
    mapping = {}
    
    # Standard mappings based on common column names
    for key in sample_row.keys():
        key_lower = key.lower()
        
        if 'date' in key_lower or 'timestamp' in key_lower:
            mapping['Date'] = key
        elif 'amount' in key_lower:
            mapping['Amount'] = key
        elif 'description' in key_lower or 'title' in key_lower:
            mapping['Title'] = key
        elif 'note' in key_lower or 'type' in key_lower or 'reference' in key_lower:
            mapping['Note'] = key
        elif 'balance' in key_lower:
            mapping['Balance'] = key
        elif 'currency' in key_lower:
            mapping['Currency'] = key
    
    print(f"🔧 Created fallback mapping: {mapping}")
    return mapping

@transform_router.post("/export")
async def export_csv_data(request: Request):
    """Export transformed data as CSV file"""
    print(f"📥 Export request received")
    
    try:
        # Parse the request body
        body = await request.body()
        data = json.loads(body)
        
        # Handle different data formats
        if isinstance(data, list):
            # Direct array format
            csv_data = data
            print(f"🔍 Export data: direct array with {len(data)} items")
        elif isinstance(data, dict):
            print(f"🔍 Export data keys: {list(data.keys())}")
            # Extract the actual data - handle different possible formats
            if 'transformed_data' in data:
                csv_data = data['transformed_data']
            elif 'data' in data:
                csv_data = data['data']
            else:
                # If data is the direct format from frontend
                csv_data = data
        else:
            csv_data = None
            
        if not csv_data or not isinstance(csv_data, list) or len(csv_data) == 0:
            raise HTTPException(status_code=400, detail="No valid data provided for export")
            
        print(f"📊 Exporting {len(csv_data)} rows")
        
        # Debug: Show sample data structure
        if csv_data:
            print(f"🔍 Sample data row keys: {list(csv_data[0].keys()) if csv_data else 'none'}")
            if len(csv_data) > 1:
                print(f"🔍 Second row keys: {list(csv_data[1].keys())}")
        
        # Create CSV content
        output = io.StringIO()
        if csv_data:
            # Define standard Cashew fields (no Balance column)
            cashew_fields = ['Date', 'Amount', 'Category', 'Title', 'Note', 'Account']
            
            # Filter data to only include Cashew-compatible fields
            filtered_data = []
            for row in csv_data:
                filtered_row = {field: row.get(field, '') for field in cashew_fields if field in row}
                filtered_data.append(filtered_row)
            
            # Create writer with standard Cashew headers
            writer = csv.DictWriter(output, fieldnames=cashew_fields)
            writer.writeheader()
            
            # Write filtered rows
            for row in filtered_data:
                # Ensure all Cashew fields are present
                complete_row = {field: row.get(field, '') for field in cashew_fields}
                writer.writerow(complete_row)
            
        csv_content = output.getvalue()
        output.close()
        
        print(f"✅ CSV export successful: {len(csv_content)} characters")
        
        # Return as streaming response (blob)
        return StreamingResponse(
            io.BytesIO(csv_content.encode('utf-8')),
            media_type='text/csv',
            headers={
                'Content-Disposition': f'attachment; filename=exported_data_{len(csv_data)}_rows.csv'
            }
        )
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {str(e)}")
    except Exception as e:
        print(f"❌ Export error: {str(e)}")
        import traceback
        print(f"📖 Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))
