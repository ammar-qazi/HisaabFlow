import React, { useMemo } from 'react';
import { useTheme } from '../../theme/ThemeProvider';
import { Card, Badge, Progress } from '../ui';
import { CheckCircle } from '../ui/Icons';

function ValidationChecklist({
  validationChecklist,
  updateValidationItem,
  validationProgress,
  autoParseResults
}) {
  const theme = useTheme();

  // Calculate highlights for validation counts
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
          count: largeTransactions.length,
        });
      }
    });

    return items;
  }, [autoParseResults]);

  // Calculate metrics for validation
  const validationMetrics = useMemo(() => {
    if (!autoParseResults) return { dateRange: null, cleaningApplied: 0 };

    const cleaningApplied = autoParseResults.filter(result => 
      result.parse_result?.cleaning_applied).length;

    // Calculate date ranges
    const allDates = [];
    autoParseResults.forEach(result => {
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
    } : null;

    return { dateRange, cleaningApplied };
  }, [autoParseResults]);

  return (
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
          { 
            key: 'largeTransactions', 
            label: 'Large transactions reviewed', 
            count: highlights.filter(h => h.type === 'large-transactions').reduce((sum, h) => sum + h.count, 0)
          },
          { 
            key: 'dateRange', 
            label: 'Date range confirmed', 
            count: validationMetrics.dateRange ? 1 : 0 
          },
          { 
            key: 'categories', 
            label: 'Categories approved', 
            count: autoParseResults.length 
          },
          { 
            key: 'dataQuality', 
            label: 'Data quality verified', 
            count: validationMetrics.cleaningApplied 
          }
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
  );
}

export default ValidationChecklist;