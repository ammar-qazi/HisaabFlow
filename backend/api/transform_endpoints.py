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
    """Extract transformation data using bank-agnostic detection for each CSV file"""
    
    # Handle different frontend data formats
    if 'csv_data_list' in raw_data:
        print(f"📋 Frontend format detected: csv_data_list")
        csv_data_list = raw_data.get('csv_data_list', [])
        print(f"📈 CSV data list length: {len(csv_data_list)}")
        
        if not csv_data_list:
            print(f"⚠️ No CSV data found in csv_data_list")
            return [], {}, ''
        
        # Process each CSV file with its own bank detection
        all_transformed_data = []
        
        for csv_index, csv_data in enumerate(csv_data_list):
            print(f"\n🗂️ Processing CSV {csv_index + 1}/{len(csv_data_list)}")
            
            # Get data from this CSV
            csv_file_data = csv_data.get('data', [])
            filename = csv_data.get('filename', f'file_{csv_index + 1}.csv')
            
            if not csv_file_data:
                print(f"   ⚠️ No data in CSV {csv_index + 1}")
                continue
                
            print(f"   📊 CSV has {len(csv_file_data)} rows")
            print(f"   📁 Filename: {filename}")
            
            # Detect bank type for this specific CSV
            detection_result = bank_detector.detect_bank_from_data(filename, csv_file_data)
            print(f"   🎯 Bank detected: {detection_result}")
            
            if not detection_result.is_confident:
                print(f"   ⚠️ Low confidence detection for {filename}")
                # TODO: In future, ask user to manually select bank
                
            detected_bank = detection_result.bank_name
            
            # Get bank-specific column mapping
            if detected_bank != 'unknown':
                bank_column_mapping = bank_config_manager.get_column_mapping(detected_bank)
                print(f"   🗺️ Using bank-specific mapping: {bank_column_mapping}")
            else:
                # Fallback to generic mapping
                print(f"   🔧 Using fallback mapping for unknown bank")
                sample_row = csv_file_data[0] if csv_file_data else {}
                bank_column_mapping = _create_fallback_mapping(sample_row)
            
            # Transform this CSV's data using its specific bank mapping
            try:
                print(f"   🔄 Transforming CSV {csv_index + 1} with {detected_bank} mapping")
                
                # Apply bank-specific mapping to standardize column names
                standardized_data = []
                for row in csv_file_data:
                    standardized_row = {}
                    for target_col, source_col in bank_column_mapping.items():
                        if source_col in row:
                            standardized_row[target_col] = row[source_col]
                        else:
                            standardized_row[target_col] = ''  # Empty if column not found
                    standardized_data.append(standardized_row)
                
                print(f"   ✅ Standardized {len(standardized_data)} rows for CSV {csv_index + 1}")
                if standardized_data:
                    print(f"   📄 Sample standardized row: {standardized_data[0]}")
                
                # Add standardized data to combined results
                all_transformed_data.extend(standardized_data)
                
            except Exception as e:
                print(f"   ❌ Error processing CSV {csv_index + 1}: {str(e)}")
                continue
        
        print(f"\n📈 Combined data from all CSVs: {len(all_transformed_data)} total rows")
        
        # Use the most common bank or first detected bank for overall processing
        # For now, we'll use a standard mapping since all data is now standardized
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
        
        # Create CSV content
        output = io.StringIO()
        if csv_data:
            # Get headers from first row
            headers = list(csv_data[0].keys())
            writer = csv.DictWriter(output, fieldnames=headers)
            writer.writeheader()
            writer.writerows(csv_data)
            
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
