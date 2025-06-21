import React, { useState, useEffect } from 'react';
import { useTheme } from '../../../theme/ThemeProvider';
import { Card } from '../../ui';
import { RefreshCw, CheckCircle } from '../../ui/Icons'; // Assuming these icons exist

function TransformationProgress({ loading, currentStage = 'idle' }) {
  const theme = useTheme();
  const [stageIndex, setStageIndex] = useState(0);
  const stages = [
    "Analyzing transactions",
    "Detecting transfers",
    "Applying categorization",
    "Preparing export"
  ];

  useEffect(() => {
    if (loading) {
      // Simulate progress through stages if no real-time update from parent
      const interval = setInterval(() => {
        setStageIndex(prev => (prev < stages.length - 1 ? prev + 1 : prev));
      }, 1500); // Advance stage every 1.5 seconds
      return () => clearInterval(interval);
    } else {
      setStageIndex(0); // Reset or set to final success stage
    }
  }, [loading]); // Only re-run when loading state changes

  const displayStage = stages[stageIndex] || "Idle";

  return (
    <Card style={{ padding: theme.spacing.xl }}>
      <div style={{ 
        display: 'flex', 
        alignItems: 'center', 
        gap: theme.spacing.md, 
        marginBottom: theme.spacing.lg 
      }}>
        {loading ? (
          <RefreshCw 
            size={24} 
            color={theme.colors.primary} 
            className="spin"
          />
        ) : (
          <CheckCircle size={24} color={theme.colors.success} />
        )}
        <h3 style={{ 
          ...theme.typography.h4, 
          color: theme.colors.text.primary, 
          margin: 0 
        }}>
          {loading ? 'Processing in Progress' : 'Processing Complete!'}
        </h3>
      </div>
      
      <div style={{ 
        padding: theme.spacing.lg,
        backgroundColor: theme.colors.background.default,
        borderRadius: theme.borderRadius.lg,
        border: `1px solid ${theme.colors.border}`,
        textAlign: 'center'
      }}>
        {loading ? (
          <div>
            <p style={{ 
              ...theme.typography.h6, 
              color: theme.colors.primary,
              marginBottom: theme.spacing.md 
            }}>
              {displayStage}...
            </p>
            <p style={{ 
              ...theme.typography.body2, 
              color: theme.colors.text.secondary,
              margin: 0 
            }}>
              This may take a few moments while we analyze your transactions
            </p>
          </div>
        ) : (
          <div>
            <p style={{ 
              ...theme.typography.h6, 
              color: theme.colors.success,
              marginBottom: theme.spacing.sm 
            }}>
              All transactions have been processed successfully!
            </p>
            <p style={{ 
              ...theme.typography.body2, 
              color: theme.colors.text.secondary,
              margin: 0 
            }}>
              Review your results and download your data below
            </p>
          </div>
        )}
      </div>
    </Card>
  );
}

export default TransformationProgress;