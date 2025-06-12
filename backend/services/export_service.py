"""
Export service for generating CSV files from transformed data
"""
import csv
import io
import json
from fastapi.responses import StreamingResponse


class ExportService:
    """Service for handling data export operations"""
    
    def export_to_csv(self, request_data):
        """
        Export transformed data as CSV file
        
        Args:
            request_data: Request data containing the data to export
            
        Returns:
            StreamingResponse: CSV file as streaming response
        """
        print(f"📥 Export request received")
        
        try:
            # Handle different data formats
            csv_data = self._extract_export_data(request_data)
            
            if not csv_data or not isinstance(csv_data, list) or len(csv_data) == 0:
                raise ValueError("No valid data provided for export")
                
            print(f"📊 Exporting {len(csv_data)} rows")
            
            # Debug: Show sample data structure
            if csv_data:
                print(f"🔍 Sample data row keys: {list(csv_data[0].keys()) if csv_data else 'none'}")
                if len(csv_data) > 1:
                    print(f"🔍 Second row keys: {list(csv_data[1].keys())}")
            
            # Create CSV content
            csv_content = self._create_csv_content(csv_data)
            
            print(f"✅ CSV export successful: {len(csv_content)} characters")
            
            # Return as streaming response (blob)
            return StreamingResponse(
                io.BytesIO(csv_content.encode('utf-8')),
                media_type='text/csv',
                headers={
                    'Content-Disposition': f'attachment; filename=exported_data_{len(csv_data)}_rows.csv'
                }
            )
            
        except Exception as e:
            print(f"❌ Export error: {str(e)}")
            import traceback
            print(f"📖 Full traceback: {traceback.format_exc()}")
            raise e
    
    def _extract_export_data(self, request_data):
        """Extract data for export from different request formats"""
        if isinstance(request_data, list):
            # Direct array format
            csv_data = request_data
            print(f"🔍 Export data: direct array with {len(request_data)} items")
        elif isinstance(request_data, dict):
            print(f"🔍 Export data keys: {list(request_data.keys())}")
            # Extract the actual data - handle different possible formats
            if 'transformed_data' in request_data:
                csv_data = request_data['transformed_data']
            elif 'data' in request_data:
                csv_data = request_data['data']
            else:
                # If data is the direct format from frontend
                csv_data = request_data
        else:
            csv_data = None
        
        return csv_data
    
    def _create_csv_content(self, csv_data: list):
        """Create CSV content from data"""
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
        
        return csv_content
