import React, { useState } from 'react';
import { useTheme } from '../../../theme/ThemeProvider';
import { Card, Button, Badge } from '../../ui';
import { ChevronDown, ChevronUp, AlertCircle, TrendingUp } from '../../ui/Icons'; // Assuming icons exist
import { TransformationService } from '../../../services/transformationService';
import toast from 'react-hot-toast';

function TransferAnalysisPanel({ 
  transferAnalysis, 
  manuallyConfirmedTransfers, 
  setManuallyConfirmedTransfers,
  transformedData,
  setTransformedData
}) {
  const theme = useTheme();
  const [expandedTransfers, setExpandedTransfers] = useState({});
  const [expandedPotentialTransfers, setExpandedPotentialTransfers] = useState(false);
  const [selectedPotentialTransfers, setSelectedPotentialTransfers] = useState(new Set());
  const [isApplyingCategorization, setIsApplyingCategorization] = useState(false);
  
  // Use passed manuallyConfirmedTransfers and setManuallyConfirmedTransfers instead of local state
  const localManuallyConfirmedTransfers = manuallyConfirmedTransfers || [];
  const updateManuallyConfirmedTransfers = setManuallyConfirmedTransfers || (() => {});

  // Add debugging
  console.log(' TransferAnalysisPanel Debug:', {
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

  const togglePotentialTransfersExpand = () => {
    setExpandedPotentialTransfers(prev => !prev);
  };

  const togglePotentialTransferSelection = (transactionIndex) => {
    setSelectedPotentialTransfers(prev => {
      const newSet = new Set(prev);
      if (newSet.has(transactionIndex)) {
        newSet.delete(transactionIndex);
      } else {
        newSet.add(transactionIndex);
      }
      return newSet;
    });
  };

  const confirmSelectedPairs = async () => {
    if (selectedPotentialTransfers.size === 0 || isApplyingCategorization) return;

    // Get selected pairs
    const selectedPairs = availablePotentialPairs.filter(pair => 
      selectedPotentialTransfers.has(pair.outgoing?._transaction_index)
    );

    // Convert selected pairs to confirmed transfer format
    const newPairs = selectedPairs.map(pair => ({
      outgoing: pair.outgoing,
      incoming: pair.incoming,
      confidence: 0.8, // Manual confirmation gets high confidence
      type: 'manual',
      manual: true,
      reason: pair.reason || 'manual_confirmation'
    }));

    setIsApplyingCategorization(true);

    try {
      // 1. Optimistically update local state
      const updatedManuallyConfirmed = [...(localManuallyConfirmedTransfers || []), ...newPairs];
      updateManuallyConfirmedTransfers(updatedManuallyConfirmed);
      
      // 2. Apply categorization via API
      const result = await TransformationService.applyTransferCategorization({
        transformedData: transformedData,
        manuallyConfirmedPairs: updatedManuallyConfirmed,
        transferAnalysis: transferAnalysis
      });
      
      // 3. Update transformed data with new categories
      if (setTransformedData && result.transformedData) {
        setTransformedData(result.transformedData);
      }
      
      // 4. Clear selection and show success
      setSelectedPotentialTransfers(new Set());
      toast.success(`Processed ${newPairs.length} transfer pair${newPairs.length !== 1 ? 's' : ''}`);
      
      console.log('Successfully applied categorization to transfer pairs:', newPairs);
      
    } catch (error) {
      // Revert optimistic update on error
      updateManuallyConfirmedTransfers(localManuallyConfirmedTransfers);
      toast.error(`Failed to process transfer pairs: ${error.message}`);
      console.error('Transfer categorization error:', error);
    } finally {
      setIsApplyingCategorization(false);
    }
  };

  // Handle multiple possible data structures
  let transferPairs = [];
  let currencyConversions = 0;
  let hasTransfers = false;
  let potentialPairs = [];
  let hasPotentialPairs = false;

  if (transferAnalysis) {
    // Case 1: transferAnalysis.transfers exists (current backend format)
    if (transferAnalysis.transfers && Array.isArray(transferAnalysis.transfers)) {
      transferPairs = transferAnalysis.transfers;
      currencyConversions = transferAnalysis.summary?.currency_conversions || 0;
      hasTransfers = transferPairs.length > 0;
      
      // Extract potential pairs
      if (transferAnalysis.potential_pairs && Array.isArray(transferAnalysis.potential_pairs)) {
        potentialPairs = transferAnalysis.potential_pairs;
        hasPotentialPairs = potentialPairs.length > 0;
      }
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

  // Filter out transactions that are already in confirmed pairs (both auto-detected and manual)
  const confirmedTransactionIds = new Set();
  transferPairs.forEach(pair => {
    confirmedTransactionIds.add(pair.outgoing?._transaction_index);
    confirmedTransactionIds.add(pair.incoming?._transaction_index);
  });
  localManuallyConfirmedTransfers.forEach(pair => {
    confirmedTransactionIds.add(pair.outgoing?._transaction_index);
    confirmedTransactionIds.add(pair.incoming?._transaction_index);
  });

  // Filter potential pairs to exclude already confirmed ones
  const availablePotentialPairs = potentialPairs.filter(pair => 
    !confirmedTransactionIds.has(pair.outgoing?._transaction_index) &&
    !confirmedTransactionIds.has(pair.incoming?._transaction_index)
  );

  // Combine auto-detected and manually confirmed transfers for display
  const allTransferPairs = [...transferPairs, ...localManuallyConfirmedTransfers];
  const allHasTransfers = allTransferPairs.length > 0;

  console.log('[DATA] TransferAnalysisPanel Computed:', { 
    transferPairs, 
    localManuallyConfirmedTransfers,
    allTransferPairs,
    hasTransfers, 
    allHasTransfers,
    transferPairsLength: transferPairs.length,
    availablePotentialPairs: availablePotentialPairs.length
  });

  return (
    <Card style={{ padding: theme.spacing.lg }}>
      <h3 style={{ ...theme.typography.h5, color: theme.colors.text.primary, marginBottom: theme.spacing.md }}>
        Transfer Detection Insights
      </h3>
      {!allHasTransfers && (
        <p style={{ ...theme.typography.body1, color: theme.colors.text.secondary }}>
          No transfer pairs detected or analysis not yet available.
        </p>
      )}
      {allHasTransfers && (
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
              Detected {allTransferPairs.length} transfer pair(s) ({transferPairs.length} auto-detected, {localManuallyConfirmedTransfers.length} manually confirmed){currencyConversions > 0 ? ` and ${currencyConversions} currency conversion(s)` : ''}.
            </p>
          </div>
          {allTransferPairs.map((pair, index) => {
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
                    {pair.manual && (
                      <Badge variant='secondary'>
                        Manual
                      </Badge>
                    )}
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
      
      {availablePotentialPairs.length > 0 && (
        <div style={{ marginTop: theme.spacing.lg }}>
          {/* Potential Transfers Header */}
          <Button
            variant="secondary"
            onClick={togglePotentialTransfersExpand}
            style={{
              width: '100%',
              textAlign: 'left',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              padding: theme.spacing.md,
              border: `1px solid ${theme.colors.border}`,
              borderRadius: theme.borderRadius.lg,
              backgroundColor: theme.colors.background.paper,
              marginBottom: expandedPotentialTransfers ? theme.spacing.sm : 0,
            }}
          >
            <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
              <span style={{ ...theme.typography.body1, color: theme.colors.text.primary, fontWeight: '500' }}>
                Potential Transfer Pairs ({availablePotentialPairs.length})
              </span>
              <span style={{ ...theme.typography.caption, color: theme.colors.text.secondary }}>
                Amount & date match, but name mismatch - review and confirm
              </span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: theme.spacing.sm }}>
              <Badge variant="info">
                {selectedPotentialTransfers.size} selected
              </Badge>
              {expandedPotentialTransfers ? 
                <ChevronUp size={18} color={theme.colors.text.primary} /> : 
                <ChevronDown size={18} color={theme.colors.text.primary} />
              }
            </div>
          </Button>

          {/* Potential Transfers List */}
          {expandedPotentialTransfers && (
            <div style={{ 
              border: `1px solid ${theme.colors.border}`, 
              borderRadius: theme.borderRadius.lg, 
              backgroundColor: theme.colors.background.paper,
              padding: theme.spacing.md
            }}>
              {availablePotentialPairs.map((pair, index) => {
                const isSelected = selectedPotentialTransfers.has(pair.outgoing?._transaction_index);
                const outgoingDate = new Date(pair.outgoing?.Date);
                const incomingDate = new Date(pair.incoming?.Date);
                const formattedDate = outgoingDate.toLocaleDateString(undefined, {
                  year: 'numeric', month: 'short', day: 'numeric' 
                });
                const daysDiff = Math.abs((outgoingDate - incomingDate) / (1000 * 60 * 60 * 24));

                return (
                  <div 
                    key={index} 
                    style={{ 
                      padding: theme.spacing.md,
                      borderBottom: index < availablePotentialPairs.length - 1 ? `1px solid ${theme.colors.border}` : 'none',
                      backgroundColor: isSelected ? theme.colors.background.selected || theme.colors.background.default : 'transparent',
                      borderRadius: theme.borderRadius.sm,
                      cursor: 'pointer',
                    }}
                    onClick={() => togglePotentialTransferSelection(pair.outgoing?._transaction_index)}
                  >
                    {/* Header with checkbox and summary */}
                    <div style={{ display: 'flex', alignItems: 'center', marginBottom: theme.spacing.sm }}>
                      <input
                        type="checkbox"
                        checked={isSelected}
                        onChange={(e) => {
                          e.stopPropagation(); // Prevent event bubbling to row click
                          togglePotentialTransferSelection(pair.outgoing?._transaction_index);
                        }}
                        onClick={(e) => e.stopPropagation()} // Also prevent click bubbling
                        style={{ marginRight: theme.spacing.sm }}
                      />
                      
                      <div style={{ flex: 1 }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: theme.spacing.sm, marginBottom: '4px' }}>
                          <span style={{ ...theme.typography.body1, color: theme.colors.text.primary, fontWeight: '500' }}>
                            {pair.outgoing?.Account || pair.outgoing?._csv_name} → {pair.incoming?.Account || pair.incoming?._csv_name}
                          </span>
                          <Badge variant="warning" style={{ fontSize: '0.75rem' }}>
                            Name Mismatch
                          </Badge>
                        </div>
                        <div style={{ ...theme.typography.caption, color: theme.colors.text.secondary }}>
                          {formattedDate} • {daysDiff < 1 ? 'Same day' : `${Math.round(daysDiff)} day${daysDiff !== 1 ? 's' : ''} apart`}
                        </div>
                      </div>
                      
                      <div style={{ textAlign: 'right' }}>
                        <span style={{ ...theme.typography.body1, fontWeight: '500', color: theme.colors.text.primary }}>
                          {pair.outgoing?.Amount} → {pair.incoming?.Amount}
                        </span>
                      </div>
                    </div>

                    {/* Details */}
                    <div style={{ 
                      display: 'flex', 
                      justifyContent: 'space-between', 
                      marginLeft: theme.spacing.lg,
                      opacity: 0.8 
                    }}>
                      <div style={{ flex: 1, marginRight: theme.spacing.md }}>
                        <div style={{ ...theme.typography.caption, color: theme.colors.text.secondary, marginBottom: '2px' }}>
                          Outgoing:
                        </div>
                        <div style={{ ...theme.typography.body2, color: theme.colors.text.primary }}>
                          {pair.outgoing?.Description || pair.outgoing?.Title || 'N/A'}
                        </div>
                        {pair.outgoing_name && (
                          <div style={{ ...theme.typography.caption, color: theme.colors.text.secondary }}>
                            Name: "{pair.outgoing_name}"
                          </div>
                        )}
                      </div>
                      
                      <div style={{ flex: 1 }}>
                        <div style={{ ...theme.typography.caption, color: theme.colors.text.secondary, marginBottom: '2px' }}>
                          Incoming:
                        </div>
                        <div style={{ ...theme.typography.body2, color: theme.colors.text.primary }}>
                          {pair.incoming?.Description || pair.incoming?.Title || 'N/A'}
                        </div>
                        {pair.incoming_name && (
                          <div style={{ ...theme.typography.caption, color: theme.colors.text.secondary }}>
                            Name: "{pair.incoming_name}"
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}

              {/* Action Buttons */}
              {selectedPotentialTransfers.size > 0 && (
                <div style={{ 
                  marginTop: theme.spacing.md, 
                  paddingTop: theme.spacing.md,
                  borderTop: `1px solid ${theme.colors.border}`,
                  display: 'flex',
                  gap: theme.spacing.sm,
                  justifyContent: 'flex-end'
                }}>
                  <Button
                    variant="secondary"
                    onClick={() => setSelectedPotentialTransfers(new Set())}
                  >
                    Clear Selection
                  </Button>
                  <Button
                    variant="primary"
                    onClick={confirmSelectedPairs}
                    disabled={isApplyingCategorization}
                  >
                    {isApplyingCategorization 
                      ? `Processing ${selectedPotentialTransfers.size} pair${selectedPotentialTransfers.size !== 1 ? 's' : ''}...`
                      : `Confirm Selected (${selectedPotentialTransfers.size})`
                    }
                  </Button>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </Card>
  );
}

export default TransferAnalysisPanel;