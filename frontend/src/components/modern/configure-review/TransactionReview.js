import React, { useState, useMemo } from 'react';
import { useTheme } from '../../../theme/ThemeProvider';
import { Card, Button, Badge } from '../../ui';
import { 
  Eye, Minus, CheckCircle, DollarSign, TrendingUp, AlertCircle
} from '../../ui/Icons';

function TransactionReview({ autoParseResults, uploadedFiles }) {
  const theme = useTheme();
  const [viewMode, setViewMode] = useState('summary'); // 'summary' | 'highlights' | 'full'
  const [expandedFiles, setExpandedFiles] = useState(new Set());

  // Extract highlights that need attention
  const highlights = useMemo(() => {
    if (!autoParseResults) return [];
    
    const items = [];
    
    autoParseResults.forEach((result, fileIndex) => {
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
  }, [autoParseResults]);

  const toggleFileExpansion = (fileIndex) => {
    const newExpanded = new Set(expandedFiles);
    if (newExpanded.has(fileIndex)) {
      newExpanded.delete(fileIndex);
    } else {
      newExpanded.add(fileIndex);
    }
    setExpandedFiles(newExpanded);
  };

  return (
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
          {autoParseResults.map((result, index) => (
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
                    {(uploadedFiles.find(f => f.fileName === result.filename)?.detectedBank) || 'Unknown Bank'} •
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
          {autoParseResults.map((result, fileIndex) => (
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
  );
}

export default TransactionReview;