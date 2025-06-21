import React, { useState } from 'react';
import { useTheme } from '../../../theme/ThemeProvider';
import { Card, Button } from '../../ui';
import { Download, CheckCircle, FileText } from '../../ui/Icons'; // Assuming icons exist

function ExportOptions({ transformedData, exportData }) {
  const theme = useTheme();
  const [exporting, setExporting] = useState(false);
  const [exportSuccess, setExportSuccess] = useState(false);
  const [selectedFormat, setSelectedFormat] = useState('csv'); // Default to CSV

  // Add debugging and handle multiple data structures
  console.log('🔍 ExportOptions Debug:', {
    transformedData,
    transformedDataType: Array.isArray(transformedData) ? 'array' : typeof transformedData,
    transformedDataLength: Array.isArray(transformedData) ? transformedData.length : 'not array'
  });

  const handleExportClick = async () => {
    setExporting(true);
    setExportSuccess(false);
    
    try {
      // Call the actual export function
      await exportData();
      setExportSuccess(true);
    } catch (error) {
      console.error('Export failed:', error);
      // Handle error (could add error state here)
    } finally {
      setExporting(false);
    }
  };

  // Handle multiple possible data structures for checking if data is available
  let isDataAvailable = false;
  
  if (transformedData) {
    if (Array.isArray(transformedData)) {
      isDataAvailable = transformedData.length > 0;
    } else if (transformedData.processed_transactions) {
      isDataAvailable = transformedData.processed_transactions.length > 0;
    } else if (typeof transformedData === 'object') {
      // If it's an object, assume it has data
      isDataAvailable = true;
    }
  }

  console.log('📊 ExportOptions Computed:', { isDataAvailable });

  return (
    <Card style={{ padding: theme.spacing.xl }}>
      <div style={{ 
        display: 'flex', 
        alignItems: 'center', 
        gap: theme.spacing.md, 
        marginBottom: theme.spacing.lg 
      }}>
        <Download size={24} color={theme.colors.primary} />
        <h3 style={{ 
          ...theme.typography.h4, 
          color: theme.colors.text.primary, 
          margin: 0 
        }}>
          Export Your Data
        </h3>
      </div>
      
      <div style={{ display: 'flex', flexDirection: 'column', gap: theme.spacing.lg }}>
        <div style={{ 
          display: 'flex', 
          alignItems: 'center', 
          gap: theme.spacing.md,
          padding: theme.spacing.lg,
          backgroundColor: theme.colors.background.default,
          borderRadius: theme.borderRadius.lg,
          border: `1px solid ${theme.colors.border}`
        }}>
          <FileText size={24} color={theme.colors.text.secondary} />
          <div style={{ flex: 1 }}>
            <h4 style={{ ...theme.typography.h6, color: theme.colors.text.primary, marginBottom: theme.spacing.xs }}>
              Export Format
            </h4>
            <select
              value={selectedFormat}
              onChange={(e) => setSelectedFormat(e.target.value)}
              style={{
                width: '100%',
                padding: theme.spacing.md,
                borderRadius: theme.borderRadius.md,
                border: `1px solid ${theme.colors.border}`,
                backgroundColor: theme.colors.background.paper,
                color: theme.colors.text.primary,
                fontSize: theme.typography.body1.fontSize
              }}
            >
              <option value="csv">CSV (Comma Separated Values)</option>
              {/* Add other format options if needed in the future */}
            </select>
          </div>
        </div>

        <Button
          variant="primary"
          size="large"
          onClick={handleExportClick}
          disabled={!isDataAvailable || exporting}
          loading={exporting}
          leftIcon={exporting ? null : <Download size={18} />}
        >
          {exporting ? 'Preparing Download...' : 'Download Processed Data'}
        </Button>

        {exportSuccess && (
          <div style={{ 
            display: 'flex', 
            alignItems: 'center', 
            gap: theme.spacing.md, 
            padding: theme.spacing.lg,
            backgroundColor: theme.colors.success + '10',
            borderRadius: theme.borderRadius.lg,
            border: `1px solid ${theme.colors.success}30`
          }}>
            <CheckCircle size={24} color={theme.colors.success} />
            <div>
              <h4 style={{ ...theme.typography.h6, color: theme.colors.success, marginBottom: theme.spacing.xs }}>
                Download Complete!
              </h4>
              <p style={{ ...theme.typography.body2, color: theme.colors.success, margin: 0 }}>
                Your processed data has been downloaded successfully.
              </p>
            </div>
          </div>
        )}
      </div>
    </Card>
  );
}

export default ExportOptions;