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
except ImportError:
    # Fallback path for import issues
    backend_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, backend_path)
    from enhanced_csv_parser import EnhancedCSVParser

transform_router = APIRouter()

# Initialize parser
enhanced_parser = EnhancedCSVParser()

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
        
        # Extract data from frontend format
        data, column_mapping, bank_name = _extract_transform_data(raw_data)
        
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

def _extract_transform_data(raw_data: dict):
    """Extract transformation data from frontend request format"""
    
    # Handle different frontend data formats
    if 'csv_data_list' in raw_data:
        # Frontend sends data in csv_data_list format
        print(f"📋 Frontend format detected: csv_data_list")
        csv_data_list = raw_data.get('csv_data_list', [])
        print(f"📈 CSV data list length: {len(csv_data_list)}")
        
        # Process all CSV files, not just the first one
        if csv_data_list:
            # Combine data from all CSV files
            all_data = []
            combined_column_mapping = {}
            combined_bank_name = ''
            
            for csv_index, csv_data in enumerate(csv_data_list):
                print(f"🗂️ Processing CSV {csv_index + 1}/{len(csv_data_list)}")
                csv_file_data = csv_data.get('data', [])
                if csv_file_data:
                    all_data.extend(csv_file_data)
                    print(f"   📊 Added {len(csv_file_data)} rows from CSV {csv_index + 1}")
                
                # Use configuration from first file for consistency
                if csv_index == 0:
                    first_csv = csv_data
            print(f"🗂️ First CSV keys: {list(first_csv.keys()) if first_csv else 'empty'}")
            
            data = all_data  # Use combined data from all files
            
            # **DEBUG: Check all possible configuration sources**
            print(f"🔍 CONFIGURATION DEBUG:")
            if 'config' in first_csv:
                print(f"   ✅ 'config' found: {first_csv['config']}")
            if 'template_config' in first_csv:
                print(f"   ⚠️  'template_config' found: {first_csv['template_config']}")
            if 'configuration' in first_csv:
                print(f"   ✅ 'configuration' found: {first_csv['configuration']}")
            if 'bank_config' in first_csv:
                print(f"   ✅ 'bank_config' found: {first_csv['bank_config']}")
                
            # Try to find column mapping in different places
            column_mapping = first_csv.get('column_mapping', {})
            
            # NEW: Check for configuration-based mapping first
            if not column_mapping and 'config' in first_csv:
                config = first_csv.get('config', {})
                column_mapping = config.get('column_mapping', {})
                print(f"🗂️ Found column mapping in config: {column_mapping}")
            elif not column_mapping and 'template_config' in first_csv:
                template_config = first_csv.get('template_config', {})
                column_mapping = template_config.get('column_mapping', {})
                print(f"🗂️ Found column mapping in template_config: {column_mapping}")
            
            # Try to find bank name
            bank_name = first_csv.get('bank_name', '')
            
            # NEW: Check for configuration-based bank name first
            if not bank_name and 'config' in first_csv:
                config = first_csv.get('config', {})
                bank_name = config.get('bank_name', '')
                print(f"🏦 Found bank name in config: {bank_name}")
            elif not bank_name and 'template_config' in first_csv:
                template_config = first_csv.get('template_config', {})
                bank_name = template_config.get('bank_name', '')
                print(f"🏦 Found bank name in template_config: {bank_name}")
            
            # If still empty, create a basic mapping from the data structure
            if not column_mapping and data:
                sample_row = data[0]
                print(f"📄 Sample row keys: {list(sample_row.keys())}")
                
                # **SMART MAPPING**: Try to detect Wise vs other banks
                if 'Description' in sample_row and 'TransferwiseId' in sample_row:
                    print(f"🔍 WISE BANK DETECTED - creating Wise-specific mapping")
                    
                    # Find the correct payment reference column name
                    payment_ref_col = None
                    for col_key in sample_row.keys():
                        if 'payment' in col_key.lower() and 'reference' in col_key.lower():
                            payment_ref_col = col_key
                            break
                    
                    # If no payment reference found, use any likely candidates
                    if not payment_ref_col:
                        for col_key in sample_row.keys():
                            if col_key.lower() in ['paymentreference', 'payment_reference', 'reference', 'note']:
                                payment_ref_col = col_key
                                break
                    
                    print(f"🔍 Payment reference column found: '{payment_ref_col}'")
                    
                    column_mapping = {
                        'Date': 'Date',
                        'Amount': 'Amount', 
                        'Title': 'Description',  # Map to Description for Wise
                        'Note': payment_ref_col or 'Note',  # Use detected column or fallback
                        'Currency': 'Currency'
                    }
                    bank_name = bank_name or 'wise_eur'  # Default to wise_eur
                    print(f"🔧 Created WISE column mapping: {column_mapping}")
                else:
                    # Default mapping for other banks
                    print(f"🔍 NON-WISE BANK DETECTED - creating standard mapping")
                    column_mapping = {
                        'Date': 'Date',
                        'Amount': 'Amount', 
                        'Title': 'Title',
                        'Note': 'Note',
                        'Currency': 'Currency'
                    }
                    print(f"🔧 Created basic column mapping: {column_mapping}")
            
            # Default bank name if still empty
            if not bank_name:
                # Try to detect bank from data
                if data and 'TransferwiseId' in data[0]:
                    bank_name = 'wise_eur'
                    print(f"🏦 Auto-detected bank name: {bank_name}")
                else:
                    bank_name = 'nayapay'  # Default based on the data we see
                    print(f"🏦 Using default bank name: {bank_name}")
        else:
            print(f"⚠️ No CSV data found in csv_data_list")
            data = []
            column_mapping = {}
            bank_name = ''
    else:
        # Standard format
        print(f"📋 Standard format detected")
        data = raw_data.get('data', [])
        column_mapping = raw_data.get('column_mapping', {})
        bank_name = raw_data.get('bank_name', '')
    
    # **FINAL DEBUG OUTPUT**
    print(f"🔍 FINAL EXTRACTION RESULTS:")
    print(f"   📊 Data rows: {len(data)}")
    print(f"   🗺️  Column mapping: {column_mapping}")
    print(f"   🏦 Bank name: {bank_name}")
    if data:
        print(f"   📄 Sample data keys: {list(data[0].keys())}")
    
    return data, column_mapping, bank_name

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
