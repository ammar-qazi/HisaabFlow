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
