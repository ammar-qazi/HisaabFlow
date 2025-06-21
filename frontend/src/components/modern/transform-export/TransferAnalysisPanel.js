import React, { useState } from 'react';
import { useTheme } from '../../../theme/ThemeProvider';
import { Card, Button, Badge } from '../../ui';
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
          <div style={{ 
            display: 'flex', 
            alignItems: 'center', 
            gap: theme.spacing.sm, 
            backgroundColor: theme.colors.background.default, 
            padding: theme.spacing.lg, 
            borderRadius: theme.borderRadius.lg, 
            border: `1px solid ${theme.colors.border}` 
          }}>
            <TrendingUp size={20} color={theme.colors.info} />
            <p style={{ ...theme.typography.body2, color: theme.colors.text.primary }}>
              Detected {transferPairs.length} potential transfer pair(s){currencyConversions > 0 ? ` and ${currencyConversions} currency conversion(s)` : ''}.
            </p>
          </div>
          {transferPairs.map((pair, index) => {
            const formattedDate = new Date(pair.outgoing?.Date).toLocaleDateString(undefined, {
              year: 'numeric', month: 'long', day: 'numeric' 
            });

            return (
              <div key={index} style={{ 
                border: `1px solid ${theme.colors.border}`, 
                borderRadius: theme.borderRadius.lg, 
                overflow: 'hidden',
                backgroundColor: theme.colors.background.paper
              }}>
                {/* ===== Redesigned Accordion Header ===== */}
                <Button
                  variant="secondary"
                  onClick={() => toggleExpand(index)}
                  style={{
                    width: '100%',
                    textAlign: 'left',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    padding: theme.spacing.md,
                    border: 'none', // Remove the border for a cleaner look
                    backgroundColor: 'transparent', // Ensure transparent background
                  }}
                >
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                    <span style={{ ...theme.typography.body1, color: theme.colors.text.primary, fontWeight: '500' }}>
                      {pair.outgoing?.Account || 'Unknown'} → {pair.incoming?.Account || 'Unknown'}
                    </span>
                    <span style={{ ...theme.typography.caption, color: theme.colors.text.secondary }}>
                      {formattedDate}
                    </span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: theme.spacing.sm }}>
                    <Badge variant={pair.confidence >= 0.9 ? 'success' : 'warning'}>
                      {((pair.confidence || 0) * 100).toFixed(0)}% Confidence
                    </Badge>
                    {expandedTransfers[index] ? 
                      <ChevronUp size={18} color={theme.colors.text.primary} /> : 
                      <ChevronDown size={18} color={theme.colors.text.primary} />
                    }
                  </div>
                </Button>

                {/* ===== Redesigned Accordion Body ===== */}
                {expandedTransfers[index] && (
                  <div style={{ 
                    padding: `${theme.spacing.sm} ${theme.spacing.md} ${theme.spacing.md}`, // Less padding on top
                    borderTop: `1px solid ${theme.colors.border}`,
                    display: 'flex',
                    justifyContent: 'space-between',
                    gap: theme.spacing.lg
                  }}>
                    {/* Left side: Amounts */}
                    <div style={{ display: 'flex', alignItems: 'center', gap: theme.spacing.md }}>
                      <span style={{ ...theme.typography.h6, color: theme.colors.error }}>{pair.outgoing?.Amount}</span>
                      <span style={{ ...theme.typography.body1, color: theme.colors.text.secondary }}>→</span>
                      <span style={{ ...theme.typography.h6, color: theme.colors.success }}>{pair.incoming?.Amount}</span>
                    </div>
                    {/* Right side: Description */}
                    <div style={{ ...theme.typography.body2, color: theme.colors.text.secondary, textAlign: 'right' }}>
                      {pair.outgoing?.Title || pair.outgoing?.Description || 'N/A'}
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </Card>
  );
}

export default TransferAnalysisPanel;