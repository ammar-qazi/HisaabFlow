"""
Data transformation service for converting parsed data to Cashew format
"""
import os
import sys
import json

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


class TransformationService:
    """Service for transforming data to Cashew format"""
    
    def __init__(self):
        self.enhanced_parser = EnhancedCSVParser()
        self.bank_config_manager = BankConfigManager()
        self.bank_detector = BankDetector(self.bank_config_manager)
    
    def transform_single_data(self, data: list, column_mapping: dict, bank_name: str = "", 
                            categorization_rules: list = None, default_category_rules: dict = None,
                            account_mapping: dict = None):
        """
        Transform single dataset to Cashew format
        
        Args:
            data: List of data rows
            column_mapping: Column mapping dictionary
            bank_name: Bank name for transformation
            categorization_rules: Optional categorization rules
            default_category_rules: Optional default category rules
            account_mapping: Optional account mapping
            
        Returns:
            dict: Transformation result
        """
        try:
            if categorization_rules or default_category_rules:
                result = self.enhanced_parser.transform_to_cashew(
                    data, 
                    column_mapping, 
                    bank_name,
                    categorization_rules,
                    default_category_rules,
                    account_mapping
                )
            else:
                result = self.enhanced_parser.transform_to_cashew(
                    data, 
                    column_mapping, 
                    bank_name
                )
            
            return {
                "success": True,
                "data": result,
                "row_count": len(result)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def transform_multi_csv_data(self, raw_data: dict):
        """
        Transform multi-CSV data to Cashew format
        
        Args:
            raw_data: Raw request data from frontend
            
        Returns:
            dict: Multi-CSV transformation result
        """
        print(f"🔄 Multi-CSV transform request received")
        
        try:
            print(f"🗂️ Request keys: {list(raw_data.keys())}")
            
            # Extract data from frontend format using bank-agnostic detection
            data, column_mapping, bank_name = self._extract_transform_data_per_bank(raw_data)
            
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
                result = self.enhanced_parser.transform_to_cashew(
                    data, 
                    column_mapping, 
                    bank_name,
                    categorization_rules,
                    default_category_rules,
                    account_mapping
                )
            else:
                print(f"📋 Using basic transformation")
                result = self.enhanced_parser.transform_to_cashew(
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
                "transformed_data": result,
                "transformation_summary": {
                    "total_transactions": len(result),
                    "bank_name": bank_name,
                    "data_source": "multi-csv"
                },
                "transfer_analysis": {
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
            
        except Exception as e:
            print(f"❌ Multi-CSV transform exception: {str(e)}")
            import traceback
            print(f"📖 Full traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _extract_transform_data_per_bank(self, raw_data: dict):
        """Extract transformation data using PRE-DETECTED bank info from parse endpoints"""
        
        # Handle different frontend data formats
        if 'csv_data_list' in raw_data:
            return self._process_multi_csv_format(raw_data)
        else:
            # Standard single-file format
            print(f"📋 Standard format detected")
            data = raw_data.get('data', [])
            column_mapping = raw_data.get('column_mapping', {})
            bank_name = raw_data.get('bank_name', '')
            
            return data, column_mapping, bank_name
    
    def _process_multi_csv_format(self, raw_data: dict):
        """Process multi-CSV format data"""
        print(f"📋 Frontend format detected: csv_data_list")
        csv_data_list = raw_data.get('csv_data_list', [])
        print(f"📈 CSV data list length: {len(csv_data_list)}")
        
        if not csv_data_list:
            print(f"⚠️ No CSV data found in csv_data_list")
            return [], {}, ''
        
        return self._process_csv_data_list(csv_data_list)
    
    def _process_csv_data_list(self, csv_data_list: list):
        """Process each CSV file using PRE-CLEANED data"""
        all_transformed_data = []
        
        for csv_index, csv_data in enumerate(csv_data_list):
            print(f"\n🗂️ Processing CSV {csv_index + 1}/{len(csv_data_list)}")
            
            # Get data from this CSV
            csv_file_data = csv_data.get('data', [])
            filename = csv_data.get('filename', f'file_{csv_index + 1}.csv')
            bank_info = csv_data.get('bank_info', {})
            
            if not csv_file_data:
                print(f"   ⚠️ No data in CSV {csv_index + 1}")
                continue
            
            print(f"   📊 CSV has {len(csv_file_data)} rows")
            print(f"   📁 Filename: {filename}")
            
            # Log pre-detected bank info
            detected_bank = self._get_detected_bank(bank_info)
            print(f"   🏦 PRE-DETECTED bank: {detected_bank}")
            
            # Data is already cleaned and standardized
            print(f"   ✅ Using pre-cleaned data as-is")
            
            # Get Account name from bank configuration
            account_name = self._get_account_name(bank_info, filename)
            
            # Update Account field for each row
            for row in csv_file_data:
                row['Account'] = account_name
            
            print(f"   ✅ Account field '{account_name}' set for all {len(csv_file_data)} rows")
            
            # Add cleaned data to combined results
            all_transformed_data.extend(csv_file_data)
        
        print(f"\n📈 Combined data from all CSVs: {len(all_transformed_data)} total rows")
        
        # Use standard mapping since all data is already standardized
        combined_column_mapping = {
            'Date': 'Date',
            'Amount': 'Amount',
            'Title': 'Title', 
            'Note': 'Note',
            'Balance': 'Balance'
        }
        
        combined_bank_name = 'multi_bank_combined'
        
        return all_transformed_data, combined_column_mapping, combined_bank_name
    
    def _get_detected_bank(self, bank_info: dict):
        """Extract detected bank from bank info"""
        if bank_info:
            detected_bank = bank_info.get('detected_bank', 'unknown')
            confidence = bank_info.get('confidence', 0.0)
            return f"{detected_bank} (confidence={confidence:.2f})"
        return 'unknown'
    
    def _get_account_name(self, bank_info: dict, filename: str):
        """Get account name from bank configuration or filename"""
        account_name = 'Unknown'
        
        if bank_info and 'detected_bank' in bank_info:
            detected_bank = bank_info['detected_bank']
            if detected_bank != 'unknown':
                try:
                    bank_config = self.bank_config_manager.get_bank_config(detected_bank)
                    if bank_config and bank_config.has_section('bank_info'):
                        cashew_account = bank_config.get('bank_info', 'cashew_account', fallback=None)
                        if cashew_account:
                            account_name = cashew_account
                            print(f"   🏦 Using cashew_account from {detected_bank} config: '{account_name}'")
                        else:
                            print(f"   ⚠️  No cashew_account in {detected_bank} config")
                    else:
                        print(f"   ⚠️  Could not load config for {detected_bank}")
                except Exception as e:
                    print(f"   ⚠️  Error loading config for {detected_bank}: {e}")
        
        # Fallback to filename if config loading failed
        if account_name == 'Unknown':
            account_name = filename.replace('.csv', '').replace('_', ' ').replace('-', ' ').title()
            print(f"   🏦 Using filename fallback: '{account_name}'")
        
        return account_name
