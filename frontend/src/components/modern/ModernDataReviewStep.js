import React, { useState, useMemo } from 'react';
import { useTheme } from '../../theme/ThemeProvider';
import { Card, Button, Badge, Progress } from '../ui';
import { 
  ChevronLeft, ChevronRight, CheckCircle, AlertCircle,
  TrendingUp, DollarSign, Building,
  Eye, Filter, Search, BarChart, Minus
} from '../ui/Icons';

function ModernDataReviewStep({ 
  currentStep, 
  parsedResults, 
  loading, 
  transformAllFiles,
  setCurrentStep 
}) {
  const theme = useTheme();
  const [viewMode, setViewMode] = useState('summary'); // 'summary' | 'highlights' | 'full'
  const [expandedFiles, setExpandedFiles] = useState(new Set());
  const [validationChecklist, setValidationChecklist] = useState({
    largeTransactions: false,
    dateRange: false,
    categories: false,
    dataQuality: false
  });

  if (currentStep < 3 || parsedResults.length === 0) return null;

  // Calculate confidence metrics
  const confidenceMetrics = useMemo(() => {
    const totalTransactions = parsedResults.reduce((sum, result) => 
      sum + (result.parse_result?.row_count || 0), 0);
    
    const successfulFiles = parsedResults.filter(result => 
      result.parse_result?.success && result.parse_result?.row_count > 0).length;
    
    const bankDetectionConfidence = parsedResults.reduce((sum, result) => 
      sum + (result.bank_info?.confidence || 0), 0) / parsedResults.length;

    const cleaningApplied = parsedResults.filter(result => 
      result.parse_result?.cleaning_applied).length;

    // Calculate date ranges
    const allDates = [];
    parsedResults.forEach(result => {
      if (result.parse_result?.data) {
        result.parse_result.data.forEach(row => {
          const date = row.Date || row.TransactionDate || row.ValueDate;
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
      totalFiles: parsedResults.length,
      successfulFiles,
      successRate: (successfulFiles / parsedResults.length) * 100,
      bankDetectionConfidence: bankDetectionConfidence * 100,
      cleaningApplied,
      dateRange
    };
  }, [parsedResults]);

  // Extract highlights that need attention
  const highlights = useMemo(() => {
    const items = [];
    
    parsedResults.forEach((result, fileIndex) => {
      const data = result.parse_result?.data || [];
      
      // Large transactions (>$500 equivalent)
      const largeTransactions = data.filter(row => {
        const amount = Math.abs(parseFloat(row.Amount || 0));
        return amount > 500;
      });

      // Recent transactions (last 30 days)
      const recentTransactions = data.filter(row => {
        const date = new Date(row.Date || row.TransactionDate);
        const thirtyDaysAgo = new Date();
        thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
        return date > thirtyDaysAgo;
      });

      // Add to highlights
      if (largeTransactions.length > 0) {
        items.push({
          type: 'large-transactions',
          file: result.filename,
          fileIndex,
          count: largeTransactions.length,
          data: largeTransactions.slice(0, 3),
          importance: 'high'
        });
      }

      if (recentTransactions.length > 0) {
        items.push({
          type: 'recent-activity',
          file: result.filename,
          fileIndex,
          count: recentTransactions.length,
          data: recentTransactions.slice(0, 3),
          importance: 'medium'
        });
      }

      // Data quality issues
      if (result.parse_result?.cleaning_summary?.issues_fixed > 0) {
        items.push({
          type: 'data-quality',
          file: result.filename,
          fileIndex,
          count: result.parse_result.cleaning_summary.issues_fixed,
          importance: 'low'
        });
      }
    });

    return items.sort((a, b) => {
      const priority = { high: 3, medium: 2, low: 1 };
      return priority[b.importance] - priority[a.importance];
    });
  }, [parsedResults]);

  const toggleFileExpansion = (fileIndex) => {
    const newExpanded = new Set(expandedFiles);
    if (newExpanded.has(fileIndex)) {
      newExpanded.delete(fileIndex);
    } else {
      newExpanded.add(fileIndex);
    }
    setExpandedFiles(newExpanded);
  };

  const updateValidationItem = (item, checked) => {
    setValidationChecklist(prev => ({
      ...prev,
      [item]: checked
    }));
  };

  const validationProgress = Object.values(validationChecklist).filter(Boolean).length / 
    Object.keys(validationChecklist).length * 100;

  const allValidated = validationProgress === 100;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: theme.spacing.lg }}>
      {/* Header */}
      <Card padding="lg" elevated>
        <div style={{ 
          display: 'flex', 
          alignItems: 'center', 
          marginBottom: theme.spacing.lg,
          gap: theme.spacing.md 
        }}>
          <div style={{
            width: '32px',
            height: '32px',
            backgroundColor: theme.colors.primary,
            color: 'white',
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '16px',
            fontWeight: '600',
          }}>
            3
          </div>
          <div>
            <h2 style={{
              margin: 0,
              fontSize: '24px',
              fontWeight: '600',
              color: theme.colors.text.primary,
              marginBottom: '4px',
            }}>
              Review Your Financial Data
            </h2>
            <p style={{
              margin: 0,
              fontSize: '14px',
              color: theme.colors.text.secondary,
            }}>
              Verify data accuracy and review important transactions before processing
            </p>
          </div>
        </div>

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
            <div style={{ fontSize: '16px', fontWeight: '600', color: theme.colors.text.primary }}>
              {confidenceMetrics.dateRange ? 
                `${confidenceMetrics.dateRange.start} - ${confidenceMetrics.dateRange.end}` : 
                'No dates found'
              }
            </div>
            <div style={{ fontSize: '12px', color: theme.colors.text.secondary }}>
              {confidenceMetrics.dateRange ? 
                `${confidenceMetrics.dateRange.days} days` : 
                (confidenceMetrics.dateRange === null ? 'Date Range (No Dates)' : 'Date Range')}
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
        </div>
      </Card>

      {/* Validation Checklist */}
      <Card padding="lg" elevated>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: theme.spacing.md,
          marginBottom: theme.spacing.md,
        }}>
          <CheckCircle size={20} color={theme.colors.primary} />
          <h3 style={{
            margin: 0,
            fontSize: '16px',
            fontWeight: '600',
            color: theme.colors.text.primary,
          }}>
            Validation Checklist
          </h3>
        </div>

        <Progress 
          value={validationProgress} 
          style={{ marginBottom: theme.spacing.md }}
        />

        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: theme.spacing.sm 
        }}>
          {[
            { key: 'largeTransactions', label: 'Large transactions reviewed', count: highlights.filter(h => h.type === 'large-transactions').length },
            { key: 'dateRange', label: 'Date range confirmed', count: confidenceMetrics.dateRange ? 1 : 0 },
            { key: 'categories', label: 'Categories approved', count: parsedResults.length },
            { key: 'dataQuality', label: 'Data quality verified', count: confidenceMetrics.cleaningApplied }
          ].map(item => (
            <label key={item.key} style={{
              display: 'flex',
              alignItems: 'center',
              gap: theme.spacing.sm,
              padding: theme.spacing.sm,
              borderRadius: theme.borderRadius.sm,
              cursor: 'pointer',
              backgroundColor: validationChecklist[item.key] ? 
                theme.colors.success + '20' : 'transparent',
            }}>
              <input
                type="checkbox"
                checked={validationChecklist[item.key]}
                onChange={(e) => updateValidationItem(item.key, e.target.checked)}
                style={{
                  width: '16px',
                  height: '16px',
                  accentColor: theme.colors.primary,
                }}
              />
              <span style={{
                fontSize: '14px',
                color: theme.colors.text.primary,
                flex: 1,
              }}>
                {item.label}
              </span>
              {item.count > 0 && (
                <Badge variant="secondary" size="small">
                  {item.count}
                </Badge>
              )}
            </label>
          ))}
        </div>
      </Card>

      {/* View Mode Toggle */}
      <Card padding="lg" elevated>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: theme.spacing.md,
          marginBottom: theme.spacing.md,
        }}>
          <Eye size={20} color={theme.colors.primary} />
          <h3 style={{
            margin: 0,
            fontSize: '16px',
            fontWeight: '600',
            color: theme.colors.text.primary,
          }}>
            Transaction Review
          </h3>
          <div style={{ marginLeft: 'auto', display: 'flex', gap: theme.spacing.xs }}>
            {['summary', 'highlights', 'full'].map(mode => (
              <Button
                key={mode}
                variant={viewMode === mode ? 'primary' : 'outline'}
                size="small"
                onClick={() => setViewMode(mode)}
              >
                {mode.charAt(0).toUpperCase() + mode.slice(1)}
              </Button>
            ))}
          </div>
        </div>

        {/* Content based on view mode */}
        {viewMode === 'summary' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: theme.spacing.md }}>
            {parsedResults.map((result, index) => (
              <div key={index} style={{
                padding: theme.spacing.md,
                backgroundColor: theme.colors.background.elevated,
                borderRadius: theme.borderRadius.md,
                border: `1px solid ${theme.colors.border}`,
              }}>
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  marginBottom: theme.spacing.sm,
                }}>
                  <div>
                    <div style={{
                      fontSize: '16px',
                      fontWeight: '500',
                      color: theme.colors.text.primary,
                    }}>
                      {result.filename}
                    </div>
                    <div style={{
                      fontSize: '12px',
                      color: theme.colors.text.secondary,
                    }}>
                      {result.bank_info?.detected_bank || 'Unknown Bank'} • 
                      {result.parse_result?.row_count || 0} transactions
                    </div>
                  </div>
                  <Badge variant="success">
                    ✓ Parsed
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        )}

        {viewMode === 'highlights' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: theme.spacing.md }}>
            {highlights.length === 0 ? (
              <div style={{
                textAlign: 'center',
                padding: theme.spacing.xl,
                color: theme.colors.text.secondary,
              }}>
                <CheckCircle size={48} color={theme.colors.success} style={{ marginBottom: theme.spacing.md }} />
                <div style={{ fontSize: '16px', fontWeight: '500', marginBottom: theme.spacing.xs }}>
                  No issues found!
                </div>
                <div style={{ fontSize: '14px' }}>
                  Your data looks clean and ready for processing.
                </div>
              </div>
            ) : (
              highlights.map((highlight, index) => (
                <div key={index} style={{
                  padding: theme.spacing.md,
                  backgroundColor: theme.colors.background.elevated,
                  borderRadius: theme.borderRadius.md,
                  border: `1px solid ${
                    highlight.importance === 'high' ? theme.colors.error :
                    highlight.importance === 'medium' ? theme.colors.warning : theme.colors.border
                  }`,
                }}>
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: theme.spacing.sm,
                    marginBottom: theme.spacing.sm,
                  }}>
                    {highlight.type === 'large-transactions' && <DollarSign size={16} color={theme.colors.error} />}
                    {highlight.type === 'recent-activity' && <TrendingUp size={16} color={theme.colors.warning} />}
                    {highlight.type === 'data-quality' && <AlertCircle size={16} color={theme.colors.warning} />}
                    <div style={{
                      fontSize: '14px',
                      fontWeight: '500',
                      color: theme.colors.text.primary,
                    }}>
                      {highlight.type === 'large-transactions' && `${highlight.count} Large Transactions`}
                      {highlight.type === 'recent-activity' && `${highlight.count} Recent Transactions`}
                      {highlight.type === 'data-quality' && `${highlight.count} Data Issues Fixed`}
                    </div>
                    <Badge variant="secondary" size="small">
                      {highlight.file}
                    </Badge>
                  </div>
                  
                  {highlight.data && (
                    <div style={{ fontSize: '12px', color: theme.colors.text.secondary }}>
                      Sample: {highlight.data.map(item => 
                        `${item.Title || item.Description || 'Transaction'} (${item.Amount || '0'})`
                      ).join(', ')}
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        )}

        {viewMode === 'full' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: theme.spacing.lg }}>
            {parsedResults.map((result, fileIndex) => (
              <div key={fileIndex} style={{
                border: `1px solid ${theme.colors.border}`,
                borderRadius: theme.borderRadius.md,
              }}>
                <div 
                  style={{
                    padding: theme.spacing.md,
                    backgroundColor: theme.colors.background.elevated,
                    borderRadius: `${theme.borderRadius.md} ${theme.borderRadius.md} 0 0`,
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                  }}
                  onClick={() => toggleFileExpansion(fileIndex)}
                >
                  <div>
                    <div style={{
                      fontSize: '16px',
                      fontWeight: '500',
                      color: theme.colors.text.primary,
                    }}>
                      {result.filename}
                    </div>
                    <div style={{
                      fontSize: '12px',
                      color: theme.colors.text.secondary,
                    }}>
                      {result.parse_result?.row_count || 0} transactions
                    </div>
                  </div>
                  {expandedFiles.has(fileIndex) ? (
                    <Minus size={16} color={theme.colors.text.secondary} />
                  ) : (
                    <Eye size={16} color={theme.colors.text.secondary} />
                  )}
                </div>

                {expandedFiles.has(fileIndex) && result.parse_result?.data && (
                  <div style={{
                    padding: theme.spacing.md,
                    maxHeight: '400px',
                    overflowY: 'auto',
                  }}>
                    <table style={{
                      width: '100%',
                      borderCollapse: 'collapse',
                      fontSize: '12px',
                    }}>
                      <thead>
                        <tr style={{ backgroundColor: theme.colors.background.paper }}>
                          {(result.parse_result.headers || []).slice(0, 6).map((header, idx) => (
                            <th key={idx} style={{
                              padding: theme.spacing.xs,
                              textAlign: 'left',
                              borderBottom: `1px solid ${theme.colors.border}`,
                            }}>
                              {header}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {result.parse_result.data.slice(0, 10).map((row, idx) => (
                          <tr key={idx} style={{
                            borderBottom: `1px solid ${theme.colors.border}`,
                          }}>
                            {(result.parse_result.headers || []).slice(0, 6).map((header, cellIdx) => (
                              <td key={cellIdx} style={{
                                padding: theme.spacing.xs,
                              }}>
                                {row[header] || ''}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                    {result.parse_result.data.length > 10 && (
                      <div style={{
                        textAlign: 'center',
                        padding: theme.spacing.md,
                        fontSize: '12px',
                        color: theme.colors.text.secondary,
                      }}>
                        Showing 10 of {result.parse_result.data.length} transactions
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </Card>

      {/* Navigation */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginTop: theme.spacing.xl,
        paddingTop: theme.spacing.lg,
        borderTop: `1px solid ${theme.colors.border}`,
      }}>
        <Button
          variant="secondary"
          size="large"
          onClick={() => setCurrentStep(2)}
          leftIcon={<ChevronLeft size={18} />}
        >
          Back to Configuration
        </Button>
        
        <Button
          variant="primary"
          size="large"
          disabled={loading || !allValidated}
          onClick={transformAllFiles}
          rightIcon={loading ? null : <ChevronRight size={18} />}
          loading={loading}
        >
          {loading ? 'Generating Report...' : 'Generate Financial Report'}
        </Button>
      </div>
    </div>
  );
}

export default ModernDataReviewStep;