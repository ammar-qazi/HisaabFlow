import React, { useMemo } from 'react';
import { useTheme } from '../../../theme/ThemeProvider';
import { Card, Button, Badge } from '../../ui';
import { 
  CheckCircle, AlertCircle, BarChart, Building, Calendar // Removed Calendar from imports
} from '../../ui/Icons';

function ConfidenceDashboard({ 
  autoParseResults,
  uploadedFiles,
  showAdvancedConfig,
  setShowAdvancedConfig
}) {
  const theme = useTheme();

  // Calculate confidence metrics from parsed results
  const confidenceMetrics = useMemo(() => {
    if (!autoParseResults || autoParseResults.length === 0) {
      return {
        totalTransactions: 0,
        totalFiles: uploadedFiles.length,
        successfulFiles: 0,
        successRate: 0,
        bankDetectionConfidence: 0,
        cleaningApplied: 0,
        dateRange: null
      };
    }

    const totalTransactions = autoParseResults.reduce((sum, result) => 
      sum + (result.parse_result?.row_count || 0), 0);
    
    const successfulFiles = autoParseResults.filter(result => 
      result.parse_result?.success && result.parse_result?.row_count > 0).length;
    
    const bankDetectionConfidence = uploadedFiles.reduce((sum, file) => 
      sum + (file.confidence || 0), 0) / uploadedFiles.length;

    const cleaningApplied = autoParseResults.filter(result => 
      result.parse_result?.cleaning_applied).length;

    // Calculate date ranges
    const allDates = [];
    autoParseResults.forEach(result => {
      if (result.parse_result?.data) {
        result.parse_result.data.forEach(row => { // row here is a CSVRow object if use_pydantic=true
          const date = row.Date; // Access the 'date' field from the CSVRow Pydantic model
          if (date) allDates.push(new Date(date));
        });
      }
    });
    
    const dateRange = allDates.length > 0 ? {
      start: new Date(Math.min(...allDates)).toLocaleDateString(),
      end: new Date(Math.max(...allDates)).toLocaleDateString(),
      days: Math.ceil((Math.max(...allDates) - Math.min(...allDates)) / (1000 * 60 * 60 * 24))
    } : null;

    return {
      totalTransactions,
      totalFiles: autoParseResults.length,
      successfulFiles,
      successRate: (successfulFiles / autoParseResults.length) * 100,
      bankDetectionConfidence: bankDetectionConfidence * 100,
      cleaningApplied,
      dateRange
    };
  }, [autoParseResults, uploadedFiles.length]);

  return (
    <Card padding="lg" elevated>
      {/* Confidence Dashboard */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: theme.spacing.md,
        marginBottom: theme.spacing.lg,
      }}>
        <div style={{
          padding: theme.spacing.md,
          backgroundColor: theme.colors.background.elevated,
          borderRadius: theme.borderRadius.md,
          textAlign: 'center',
        }}>
          <BarChart size={24} color={theme.colors.primary} style={{ marginBottom: theme.spacing.xs }} /> 
          <div style={{ fontSize: '24px', fontWeight: '600', color: theme.colors.text.primary }}>
            {confidenceMetrics.totalTransactions.toLocaleString()}
          </div>
          <div style={{ fontSize: '12px', color: theme.colors.text.secondary }}>
            Total Transactions
          </div>
        </div>

        <div style={{
          padding: theme.spacing.md,
          backgroundColor: theme.colors.background.elevated,
          borderRadius: theme.borderRadius.md,
          textAlign: 'center',
        }}>
          <Building size={24} color={theme.colors.success} style={{ marginBottom: theme.spacing.xs }} />
          <div style={{ fontSize: '24px', fontWeight: '600', color: theme.colors.text.primary }}>
            {Math.round(confidenceMetrics.bankDetectionConfidence)}%
          </div>
          <div style={{ fontSize: '12px', color: theme.colors.text.secondary }}>
            Bank Detection Confidence
          </div>
        </div>

        <div style={{
          padding: theme.spacing.md,
          backgroundColor: theme.colors.background.elevated,
          borderRadius: theme.borderRadius.md,
          textAlign: 'center',
        }}>
          <Calendar size={24} color={theme.colors.success} style={{ marginBottom: theme.spacing.xs }} />
          <div style={{ fontSize: '24px', fontWeight: '600', color: theme.colors.text.primary }}>
            {confidenceMetrics.dateRange ? 
              confidenceMetrics.dateRange.days : 
              0
            }
          </div>
          <div style={{ fontSize: '12px', color: theme.colors.text.secondary }}>
            {confidenceMetrics.dateRange ? 
              'Days of Data' : 
              'No Date Range'
            }
          </div>
        </div>

        <div style={{
          padding: theme.spacing.md,
          backgroundColor: theme.colors.background.elevated,
          borderRadius: theme.borderRadius.md,
          textAlign: 'center',
        }}>
          <CheckCircle size={24} color={theme.colors.success} style={{ marginBottom: theme.spacing.xs }} />
          <div style={{ fontSize: '24px', fontWeight: '600', color: theme.colors.text.primary }}>
            {confidenceMetrics.successfulFiles}/{confidenceMetrics.totalFiles}
          </div>
          <div style={{ fontSize: '12px', color: theme.colors.text.secondary }}>
            Files Processed Successfully
          </div>
        </div>
      </div>

      {/* Data Health Indicator */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: theme.spacing.md,
        padding: theme.spacing.md,
        backgroundColor: confidenceMetrics.successRate > 80 ? 
          theme.colors.success + '20' : theme.colors.warning + '20',
        borderRadius: theme.borderRadius.md,
        border: `1px solid ${confidenceMetrics.successRate > 80 ? 
          theme.colors.success : theme.colors.warning}`,
      }}>
        {confidenceMetrics.successRate > 80 ? (
          <CheckCircle size={20} color={theme.colors.success} />
        ) : (
          <AlertCircle size={20} color={theme.colors.warning} />
        )}
        <div style={{ flex: 1 }}>
          <div style={{
            fontSize: '14px',
            fontWeight: '500',
            color: theme.colors.text.primary,
            marginBottom: '4px',
          }}>
            {confidenceMetrics.successRate > 80 ? 
              'Data looks great!' : 
              'Some files need attention'
            }
          </div>
          <div style={{
            fontSize: '12px',
            color: theme.colors.text.secondary,
          }}>
            {Math.round(confidenceMetrics.successRate)}% success rate, 
            {confidenceMetrics.cleaningApplied > 0 && 
              ` ${confidenceMetrics.cleaningApplied} files cleaned,`
            } ready for processing
          </div>
        </div>
        {confidenceMetrics.successRate < 80 && (
          <Button
            variant="outline"
            size="small"
            onClick={() => setShowAdvancedConfig(!showAdvancedConfig)}
          >
            {showAdvancedConfig ? 'Hide' : 'Show'} Config
          </Button>
        )}
      </div>
    </Card>
  );
}

export default ConfidenceDashboard;