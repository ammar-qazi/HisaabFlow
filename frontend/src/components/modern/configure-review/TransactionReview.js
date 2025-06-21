import React, { useState } from 'react';
import { useTheme } from '../../../theme/ThemeProvider';
import { Card, Badge, Button } from '../../ui'; // Added Button for consistency, though not strictly needed for the core structure
import { CheckCircle, ChevronDown, ChevronUp, FileText, AlertCircle } from '../../ui/Icons';
import InteractiveDataTable from '../transform-export/InteractiveDataTable';

function TransactionReview({ autoParseResults, uploadedFiles }) {
  const theme = useTheme();
  const [expandedFiles, setExpandedFiles] = useState(new Set());

  // State Management: Toggle file expansion
  const toggleFileExpansion = (fileIndex) => {
    const newExpanded = new Set(expandedFiles);
    if (newExpanded.has(fileIndex)) {
      newExpanded.delete(fileIndex);
    } else {
      newExpanded.add(fileIndex);
    }
    setExpandedFiles(newExpanded);
  };

  // Data Processing Functions:
  // Get bank name for a file
  const getBankName = (filename) => {
    const file = uploadedFiles.find(f => f.fileName === filename);
    // Prioritize detectedBank from uploadedFiles, then bank_detection from preview, then default
    return file?.detectedBank || file?.preview?.bank_detection?.detected_bank || 'Unknown Bank';
  };

  // Get transaction count
  const getTransactionCount = (result) => {
    return result.parse_result?.data?.length || result.parse_result?.row_count || 0;
  };

  // Check if file parsed successfully
  const isFileParsed = (result) => {
    return result.parse_result?.success && getTransactionCount(result) > 0;
  };

  // Calculate total transactions across all parsed files for the header summary
  const totalTransactions = autoParseResults.reduce((sum, result) => sum + getTransactionCount(result), 0);

  // Early exit if no parsed results
  if (!autoParseResults || autoParseResults.length === 0) {
    return (
      <Card padding="lg" elevated>
        <div style={{ textAlign: 'center', color: theme.colors.text.secondary }}>
          <CheckCircle size={48} color={theme.colors.success} style={{ marginBottom: theme.spacing.md }} />
          <p style={{ ...theme.typography.body1 }}>No parsed results to review yet.</p>
        </div>
      </Card>
    );
  }

  // Main Render Structure:
  return (
    <Card padding="lg" elevated>
      {/* Header Section */}
      <div style={{ display: 'flex', alignItems: 'center', gap: theme.spacing.md, marginBottom: theme.spacing.lg }}>
        <FileText size={20} color={theme.colors.primary} />
        <h3 style={{ margin: 0, ...theme.typography.h5, color: theme.colors.text.primary }}>
          Transaction Review
        </h3>
        <div style={{ marginLeft: 'auto', ...theme.typography.body2, color: theme.colors.text.secondary }}>
          {autoParseResults.length} file{autoParseResults.length !== 1 ? 's' : ''} • {totalTransactions} transactions
        </div>
      </div>

      {/* File List Section */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: theme.spacing.lg }}>
        {autoParseResults.map((result, index) => {
          const isExpanded = expandedFiles.has(index);
          const data = result.parse_result?.data || [];
          const parsedSuccessfully = isFileParsed(result);

          return (
            <div key={index} style={{ border: `1px solid ${isExpanded ? theme.colors.primary : theme.colors.border}`, borderRadius: theme.borderRadius.md, overflow: 'hidden', transition: 'border-color 0.2s ease' }}>
              {/* Collapsed File Item - Now a semantic button for accessibility */}
              <button
                aria-expanded={isExpanded}
                aria-controls={`transaction-details-${index}`}
                style={{
                  // Reset button styles
                  background: 'none',
                  border: 'none',
                  width: '100%',
                  textAlign: 'left',
                  font: 'inherit',
                  color: 'inherit',
                  // Original styles
                  padding: theme.spacing.md, 
                  backgroundColor: theme.colors.background.elevated, 
                  cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'space-between', transition: 'background-color 0.2s ease' }}
                onClick={() => toggleFileExpansion(index)}
              >
                {/* Left side: File info */}
                <div style={{ display: 'flex', alignItems: 'center', gap: theme.spacing.md, flex: 1, minWidth: 0 }}>
                  {parsedSuccessfully ? <CheckCircle size={20} color={theme.colors.success} /> : <AlertCircle size={20} color={theme.colors.error} />}
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ fontSize: '16px', fontWeight: '500', color: theme.colors.text.primary, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                      {result.filename}
                    </div>
                    <div style={{ fontSize: '12px', color: theme.colors.text.secondary }}>
                      {getBankName(result.filename)} | {getTransactionCount(result)} transactions
                    </div>
                  </div>
                </div>
                {/* Right side: Expand button */}
                <div style={{ display: 'flex', alignItems: 'center', gap: theme.spacing.sm }}>
                  <Badge variant={parsedSuccessfully ? 'success' : 'error'}>{parsedSuccessfully ? 'Parsed' : 'Failed'}</Badge>
                  {isExpanded ? <ChevronUp size={18} color={theme.colors.text.secondary} /> : <ChevronDown size={18} color={theme.colors.text.secondary} />}
                </div>
              </button>

              {/* Expanded Data Table */}
              {isExpanded && parsedSuccessfully && (
                <div 
                  id={`transaction-details-${index}`}
                  style={{ backgroundColor: theme.colors.background.paper, borderTop: `1px solid ${theme.colors.border}` }}>
                  <InteractiveDataTable data={data} isReviewMode={true} showToolbar={false} showPagination={false} />
                </div>
              )}
            </div>
          );
        })}
      </div>
    </Card>
  );
}

export default TransactionReview;