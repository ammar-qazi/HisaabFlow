import React, { useState } from 'react';
import { useTheme } from '../../../theme/ThemeProvider';
import { Card, Button } from '../../ui';
import { ChevronDown, ChevronUp, AlertCircle, TrendingUp } from '../../ui/Icons'; // Assuming icons exist

function TransferAnalysisPanel({ transferAnalysis }) {
  const theme = useTheme();
  const [expandedTransfers, setExpandedTransfers] = useState({});

  // Add debugging
  console.log('🔍 TransferAnalysisPanel Debug:', {
    transferAnalysis,
    transferAnalysisType: typeof transferAnalysis,
    transferAnalysisKeys: transferAnalysis ? Object.keys(transferAnalysis) : null
  });

  const toggleExpand = (id) => {
    setExpandedTransfers(prev => ({
      ...prev,
      [id]: !prev[id]
    }));
  };

  // Handle multiple possible data structures
  let transferPairs = [];
  let currencyConversions = 0;
  let hasTransfers = false;

  if (transferAnalysis) {
    // Case 1: transferAnalysis.transfers exists (current backend format)
    if (transferAnalysis.transfers && Array.isArray(transferAnalysis.transfers)) {
      transferPairs = transferAnalysis.transfers;
      currencyConversions = transferAnalysis.summary?.currency_conversions || 0;
      hasTransfers = transferPairs.length > 0;
    }
    // Case 2: transferAnalysis.transfer_pairs exists (legacy format)
    else if (transferAnalysis.transfer_pairs && Array.isArray(transferAnalysis.transfer_pairs)) {
      transferPairs = transferAnalysis.transfer_pairs;
      currencyConversions = transferAnalysis.currency_conversions_found || 0;
      hasTransfers = transferPairs.length > 0;
    }
    // Case 3: transferAnalysis is an array directly
    else if (Array.isArray(transferAnalysis)) {
      transferPairs = transferAnalysis;
      hasTransfers = transferPairs.length > 0;
    }
    // Case 4: Check for alternative property names
    else if (transferAnalysis.pairs) {
      transferPairs = transferAnalysis.pairs;
      hasTransfers = transferPairs.length > 0;
    }
  }

  console.log('📊 TransferAnalysisPanel Computed:', { 
    transferPairs, 
    hasTransfers, 
    transferPairsLength: transferPairs.length 
  });

  return (
    <Card style={{ padding: theme.spacing.lg }}>
      <h3 style={{ ...theme.typography.h5, color: theme.colors.text.primary, marginBottom: theme.spacing.md }}>
        Transfer Detection Insights
      </h3>
      {!hasTransfers && (
        <p style={{ ...theme.typography.body1, color: theme.colors.text.secondary }}>
          No transfer pairs detected or analysis not yet available.
        </p>
      )}
      {hasTransfers && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: theme.spacing.md }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: theme.spacing.sm, backgroundColor: theme.colors.background.default, padding: theme.spacing.sm, borderRadius: theme.borderRadius.md, border: `1px solid ${theme.colors.divider}` }}>
            <TrendingUp size={20} color={theme.colors.info} />
            <p style={{ ...theme.typography.body2, color: theme.colors.text.primary }}>
              Detected {transferPairs.length} potential transfer pair(s){currencyConversions > 0 ? ` and ${currencyConversions} currency conversion(s)` : ''}.
            </p>
          </div>
          {transferPairs.map((pair, index) => (
            <div key={index} style={{ border: `1px solid ${theme.colors.divider}`, borderRadius: theme.borderRadius.md, overflow: 'hidden' }}>
              <Button
                variant="text"
                onClick={() => toggleExpand(index)}
                style={{
                  width: '100%',
                  textAlign: 'left',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: theme.spacing.md,
                  backgroundColor: theme.colors.background.paper,
                  borderBottom: expandedTransfers[index] ? `1px solid ${theme.colors.divider}` : 'none'
                }}
              >
                <span style={{ ...theme.typography.body1, color: theme.colors.text.primary }}>
                  Transfer: {pair.outgoing?._csv_name || 'Unknown'} → {pair.incoming?._csv_name || 'Unknown'}
                </span>
                {expandedTransfers[index] ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
              </Button>
              {expandedTransfers[index] && (
                <div style={{ padding: theme.spacing.md, backgroundColor: theme.colors.background.default }}>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: theme.spacing.md }}>
                    <div>
                      <h4 style={{ ...theme.typography.h6, color: theme.colors.text.primary, marginBottom: theme.spacing.sm }}>Outgoing</h4>
                      <p style={{ ...theme.typography.body2, color: theme.colors.text.secondary, marginBottom: theme.spacing.xs }}>
                        Account: {pair.outgoing?.Account || 'Unknown'}
                      </p>
                      <p style={{ ...theme.typography.body2, color: theme.colors.text.secondary, marginBottom: theme.spacing.xs }}>
                        Amount: {pair.outgoing?.Amount || 'Unknown'}
                      </p>
                      <p style={{ ...theme.typography.body2, color: theme.colors.text.secondary, marginBottom: theme.spacing.xs }}>
                        Date: {pair.outgoing?.Date || 'Unknown'}
                      </p>
                      <p style={{ ...theme.typography.body2, color: theme.colors.text.secondary, marginBottom: theme.spacing.xs }}>
                        Description: {pair.outgoing?.Title || pair.outgoing?.Description || 'Unknown'}
                      </p>
                    </div>
                    <div>
                      <h4 style={{ ...theme.typography.h6, color: theme.colors.text.primary, marginBottom: theme.spacing.sm }}>Incoming</h4>
                      <p style={{ ...theme.typography.body2, color: theme.colors.text.secondary, marginBottom: theme.spacing.xs }}>
                        Account: {pair.incoming?.Account || 'Unknown'}
                      </p>
                      <p style={{ ...theme.typography.body2, color: theme.colors.text.secondary, marginBottom: theme.spacing.xs }}>
                        Amount: {pair.incoming?.Amount || 'Unknown'}
                      </p>
                      <p style={{ ...theme.typography.body2, color: theme.colors.text.secondary, marginBottom: theme.spacing.xs }}>
                        Date: {pair.incoming?.Date || 'Unknown'}
                      </p>
                      <p style={{ ...theme.typography.body2, color: theme.colors.text.secondary, marginBottom: theme.spacing.xs }}>
                        Description: {pair.incoming?.Title || pair.incoming?.Description || 'Unknown'}
                      </p>
                    </div>
                  </div>
                  <div style={{ marginTop: theme.spacing.md, padding: theme.spacing.sm, backgroundColor: theme.colors.background.paper, borderRadius: theme.borderRadius.sm }}>
                    <p style={{ ...theme.typography.body2, color: theme.colors.text.secondary, marginBottom: theme.spacing.xs }}>
                      Match Strategy: {pair.match_strategy || 'Unknown'}
                    </p>
                    <p style={{ ...theme.typography.body2, color: theme.colors.text.secondary, marginBottom: theme.spacing.xs }}>
                      Confidence: {((pair.confidence || 0) * 100).toFixed(1)}%
                    </p>
                    <p style={{ ...theme.typography.body2, color: theme.colors.text.secondary, marginBottom: theme.spacing.xs }}>
                      Pair ID: {pair.pair_id || 'Unknown'}
                    </p>
                    {pair.match_details && (
                      <p style={{ ...theme.typography.body2, color: theme.colors.text.secondary }}>
                        Details: {pair.match_details}
                      </p>
                    )}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </Card>
  );
}

export default TransferAnalysisPanel;