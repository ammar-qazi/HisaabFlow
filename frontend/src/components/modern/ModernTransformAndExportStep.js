import React from 'react';
import { useTheme } from '../../theme/ThemeProvider';
import { Button } from '../ui';
import { ChevronLeft, RefreshCw } from '../ui/Icons'; // Assuming icons exist

// Import modular sub-components
import TransformationProgress from './transform-export/TransformationProgress';
import TransformationResults from './transform-export/TransformationResults';
import TransferAnalysisPanel from './transform-export/TransferAnalysisPanel';
import InteractiveDataTable from './transform-export/InteractiveDataTable';
import ExportOptions from './transform-export/ExportOptions';

function ModernTransformAndExportStep({
  currentStep,
  transformedData,
  transferAnalysis,
  parsedResults,
  loading,
  transformAllFiles,
  exportData,
  onStartOver,
  setCurrentStep
}) {
  const theme = useTheme();
  
  // Calculate total transactions from parsed results
  const totalParsedTransactions = parsedResults?.reduce((total, result) => 
    total + (result.parsed_data?.length || 0), 0) || 0;

  // Determine if we have transformed data with defensive handling
  const hasTransformedData = transformedData && (
    (Array.isArray(transformedData) && transformedData.length > 0) ||
    (transformedData.processed_transactions && transformedData.processed_transactions.length > 0) ||
    (typeof transformedData === 'object' && !Array.isArray(transformedData))
  );

  // Debug logging
  console.log('🔍 ModernTransformAndExportStep Debug:', {
    currentStep,
    hasTransformedData: !!transformedData,
    transformedDataType: Array.isArray(transformedData) ? 'array' : typeof transformedData,
    transformedDataLength: Array.isArray(transformedData) ? transformedData.length : 'not array',
    hasTransferAnalysis: !!transferAnalysis,
    transferAnalysisType: typeof transferAnalysis,
    loading,
    totalParsedTransactions,
    parsedResultsLength: parsedResults?.length || 0
  });

  // This component should only render if currentStep is 3
  if (currentStep !== 3) return null;

  const handleBackToReview = () => {
    setCurrentStep(2); // Go back to the Configure & Review step
  };

  const handleTransformClick = async () => {
    await transformAllFiles();
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: theme.spacing.lg }}>
      {/* Step Header implicitly handled by ContentArea in ModernAppLogic */}

      {loading ? (
        // Show progress while transforming
        <TransformationProgress loading={loading} />
      ) : !hasTransformedData ? (
        // Show pre-transformation state with parsed data summary
        <div style={{ display: 'flex', flexDirection: 'column', gap: theme.spacing.lg }}>
          <div style={{
            backgroundColor: theme.colors.background.paper,
            border: `1px solid ${theme.colors.border}`,
            borderRadius: theme.borderRadius.lg,
            padding: theme.spacing.xl,
            textAlign: 'center'
          }}>
            <h3 style={{ 
              ...theme.typography.h4, 
              color: theme.colors.text.primary, 
              marginBottom: theme.spacing.md 
            }}>
              Ready for Processing
            </h3>
            <p style={{ 
              ...theme.typography.body1, 
              color: theme.colors.text.secondary,
              marginBottom: theme.spacing.lg
            }}>
              {totalParsedTransactions > 0 
                ? `${totalParsedTransactions} transactions from ${parsedResults?.length || 0} files are ready for processing`
                : 'No transactions found. Please go back and check your file configuration.'
              }
            </p>
            {totalParsedTransactions > 0 && (
              <Button
                variant="primary"
                size="large"
                onClick={handleTransformClick}
                disabled={loading}
              >
                Generate Financial Report
              </Button>
            )}
          </div>
        </div>
      ) : (
        // Show results and export options after transformation
        <>
          <TransformationResults
            transformedData={transformedData}
            transferAnalysis={transferAnalysis}
          />
          <TransferAnalysisPanel
            transferAnalysis={transferAnalysis}
          />
          <InteractiveDataTable
            transformedData={transformedData}
          />
          <ExportOptions
            transformedData={transformedData}
            exportData={exportData}
          />
        </>
      )}

      {/* Navigation */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginTop: theme.spacing.xl,
        paddingTop: theme.spacing.lg,
        borderTop: `1px solid ${theme.colors.border}`,
      }}>
        {!loading && (
          <Button
            variant="secondary"
            size="large"
            onClick={handleBackToReview}
            leftIcon={<ChevronLeft size={18} />}
            disabled={loading}
          >
            Back to Review
          </Button>
        )}
        
        {/* Only show 'Generate Report' if not already processed and not loading */}
        {!loading && !hasTransformedData && totalParsedTransactions === 0 && (
          <Button
            variant="secondary"
            size="large"
            onClick={handleBackToReview}
            leftIcon={<ChevronLeft size={18} />}
          >
            Back to Review
          </Button>
        )}

        {!loading && hasTransformedData && ( // Show Start Over button after processing
          <Button
            variant="secondary"
            size="large"
            onClick={onStartOver}
            leftIcon={<RefreshCw size={18} />}
          >
            Start Over
          </Button>
        )}
      </div>
    </div>
  );
}

export default ModernTransformAndExportStep;