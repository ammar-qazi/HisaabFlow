import React from 'react';
import { useTheme } from '../../../theme/ThemeProvider';
import { Card } from '../../ui'; // Assuming Card is available from '../ui'
import { CheckCircle, BarChart, TrendingUp, Tag } from '../../ui/Icons';

function TransformationResults({ transformedData, transferAnalysis }) {
  const theme = useTheme();

  // Add comprehensive debugging
  console.log('🔍 TransformationResults Debug:', {
    transformedData,
    transformedDataType: Array.isArray(transformedData) ? 'array' : typeof transformedData,
    transformedDataLength: Array.isArray(transformedData) ? transformedData.length : 'not array',
    transferAnalysis,
    transferAnalysisType: typeof transferAnalysis
  });

  // Handle multiple possible data structures from backend
  let summary = {
    total_transactions: 0,
    categorized_transactions: 0,
    transfer_pairs_found: 0,
  };

  let hasData = false;

  if (transformedData) {
    // Case 1: transformedData is an array of transactions (most likely based on logs)
    if (Array.isArray(transformedData)) {
      summary.total_transactions = transformedData.length;
      summary.categorized_transactions = transformedData.filter(t => 
        t.Category && t.Category !== 'Uncategorized' && t.Category !== '' && t.Category !== 'Other'
      ).length;
      hasData = transformedData.length > 0;
    }
    // Case 2: transformedData has a processed_transactions property
    else if (transformedData.processed_transactions) {
      summary.total_transactions = transformedData.processed_transactions.length;
      summary.categorized_transactions = transformedData.processed_transactions.filter(t => 
        t.Category && t.Category !== 'Uncategorized' && t.Category !== '' && t.Category !== 'Other'
      ).length;
      hasData = transformedData.processed_transactions.length > 0;
    }
    // Case 3: transformedData has a transformation_summary property
    else if (transformedData.transformation_summary) {
      summary = { ...transformedData.transformation_summary };
      hasData = summary.total_transactions > 0;
    }
  }

  // Handle transfer analysis data from backend
  if (transferAnalysis) {
    // Check for transfers array (current backend format)
    if (transferAnalysis.transfers && Array.isArray(transferAnalysis.transfers)) {
      summary.transfer_pairs_found = transferAnalysis.transfers.length;
    }
    // Check for summary data (preferred backend format)
    else if (transferAnalysis.summary && transferAnalysis.summary.transfer_pairs_found !== undefined) {
      summary.transfer_pairs_found = transferAnalysis.summary.transfer_pairs_found;
    }
    // Legacy format: transfer_pairs
    else if (transferAnalysis.transfer_pairs && Array.isArray(transferAnalysis.transfer_pairs)) {
      summary.transfer_pairs_found = transferAnalysis.transfer_pairs.length;
    }
    // Legacy format: transfer_pairs_found
    else if (transferAnalysis.transfer_pairs_found !== undefined) {
      summary.transfer_pairs_found = transferAnalysis.transfer_pairs_found;
    }
  }

  console.log('📊 TransformationResults Computed Summary:', { summary, hasData });

  return (
    <Card style={{ padding: theme.spacing.xl, marginBottom: theme.spacing.lg }}>
      <div style={{ 
        display: 'flex', 
        alignItems: 'center', 
        gap: theme.spacing.md, 
        marginBottom: theme.spacing.lg 
      }}>
        <CheckCircle size={24} color={theme.colors.success} />
        <h3 style={{ 
          ...theme.typography.h4, 
          color: theme.colors.text.primary, 
          margin: 0 
        }}>
          Processing Complete!
        </h3>
      </div>
      
      {hasData ? (
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
          gap: theme.spacing.lg 
        }}>
          <div style={{ 
            padding: theme.spacing.lg, 
            backgroundColor: theme.colors.background.default, 
            borderRadius: theme.borderRadius.lg, 
            border: `1px solid ${theme.colors.border}`,
            textAlign: 'center'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: theme.spacing.sm, marginBottom: theme.spacing.sm }}>
              <BarChart size={20} color={theme.colors.primary} />
              <h4 style={{ ...theme.typography.h6, color: theme.colors.text.secondary, margin: 0 }}>
                Total Transactions
              </h4>
            </div>
            <p style={{ ...theme.typography.h3, color: theme.colors.text.primary, margin: 0 }}>
              {summary.total_transactions}
            </p>
          </div>

          <div style={{ 
            padding: theme.spacing.lg, 
            backgroundColor: theme.colors.background.default, 
            borderRadius: theme.borderRadius.lg, 
            border: `1px solid ${theme.colors.border}`,
            textAlign: 'center'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: theme.spacing.sm, marginBottom: theme.spacing.sm }}>
              <Tag size={20} color={theme.colors.success} />
              <h4 style={{ ...theme.typography.h6, color: theme.colors.text.secondary, margin: 0 }}>
                Categorized
              </h4>
            </div>
            <p style={{ ...theme.typography.h3, color: theme.colors.text.primary, margin: 0 }}>
              {summary.categorized_transactions}
            </p>
          </div>

          <div style={{ 
            padding: theme.spacing.lg, 
            backgroundColor: theme.colors.background.default, 
            borderRadius: theme.borderRadius.lg, 
            border: `1px solid ${theme.colors.border}`,
            textAlign: 'center'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: theme.spacing.sm, marginBottom: theme.spacing.sm }}>
              <TrendingUp size={20} color={theme.colors.info} />
              <h4 style={{ ...theme.typography.h6, color: theme.colors.text.secondary, margin: 0 }}>
                Transfers Detected
              </h4>
            </div>
            <p style={{ ...theme.typography.h3, color: theme.colors.text.primary, margin: 0 }}>
              {summary.transfer_pairs_found}
            </p>
          </div>

        </div>
      ) : (
        <p style={{ ...theme.typography.body1, color: theme.colors.text.secondary, textAlign: 'center' }}>
          No transformation results available yet.
        </p>
      )}
    </Card>
  );
}

export default TransformationResults;