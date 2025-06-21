import React, { useMemo } from 'react';
import { useTheme } from '../../../theme/ThemeProvider'; // Ensure useMemo is imported
import { Card, Button, Badge } from '../../ui';
import { Settings, FileText, AlertCircle, CheckCircle } from '../../ui/Icons';
function AdvancedConfigPanel({
  uploadedFiles,
  autoParseResults,
  templates,
  updateFileConfig,
  applyTemplate,
  previewFile,
  loading
}) {
  const theme = useTheme();

  const getFileStatus = (file) => {
    const hasConfig = !!file.selectedConfiguration;
    const hasPreview = !!file.preview;
    const hasColumnMapping = Object.keys(file.columnMapping || {}).length > 0;
    
    if (hasConfig && hasPreview && hasColumnMapping) {
      return { status: 'configured', label: 'Ready', variant: 'success', icon: CheckCircle };
    }
    if (hasConfig || hasPreview) {
      return { status: 'partial', label: 'In Progress', variant: 'warning', icon: AlertCircle };
    }
    return { status: 'pending', label: 'Needs Setup', variant: 'error', icon: AlertCircle };
  };

  // Step 1: Create a Results Map for efficient lookups
  const resultsMap = useMemo(() =>
    new Map(autoParseResults?.map(r => [r.filename, r]) || [])
  , [autoParseResults]);

  const LOW_CONFIDENCE_THRESHOLD = 0.8;
  const hasLowConfidenceFile = uploadedFiles.some(
    file => (file.confidence || 0) < LOW_CONFIDENCE_THRESHOLD
  );

  return (
    <Card padding="lg" elevated>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: theme.spacing.md,
        marginBottom: theme.spacing.md,
      }}>
        <Settings size={20} color={theme.colors.primary} />
        <h3 style={{
          margin: 0,
          fontSize: '16px',
          fontWeight: '600',
          color: theme.colors.text.primary,
        }}>
          Advanced Configuration
        </h3>
        {hasLowConfidenceFile && (
          <Badge variant="warning" size="small">
            Low Confidence Detected
          </Badge>
        )}
      </div>

      {/* File Configuration Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))',
        gap: theme.spacing.md,
      }}>
        {uploadedFiles.map((file, index) => {
          const fileStatus = getFileStatus(file);
          const StatusIcon = fileStatus.icon;
          const confidence = file.confidence || 0;

          // Find the full parse result for this file to get the accurate row count
          const resultForFile = resultsMap.get(file.fileName); // Step 2: Use the Map for Lookups
          const finalRowCount = resultForFile?.parse_result?.row_count;
          const displayRowCount = finalRowCount ?? file.preview?.total_rows ?? 0;
          
          return (
            <div key={index} style={{
              padding: theme.spacing.md,
              backgroundColor: theme.colors.background.elevated,
              borderRadius: theme.borderRadius.md,
              border: confidence < 0.8 ? `2px solid ${theme.colors.warning}` : `1px solid ${theme.colors.border}`,
            }}>
              {/* File Header */}
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: theme.spacing.sm,
                marginBottom: theme.spacing.md,
              }}>
                <FileText size={16} color={theme.colors.primary} />
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{
                    fontSize: '14px',
                    fontWeight: '500',
                    color: theme.colors.text.primary,
                    wordBreak: 'break-word',
                  }}>
                    {file.fileName}
                  </div>
                  <div style={{
                    fontSize: '12px',
                    color: confidence < 0.8 ? theme.colors.warning : theme.colors.success,
                  }}>
                    {Math.round(confidence * 100)}% confidence
                  </div>
                </div>
                <Badge variant={fileStatus.variant} size="small">
                  <StatusIcon size={10} />
                </Badge>
              </div>

              {/* Quick Config */}
              <div style={{ display: 'flex', gap: theme.spacing.xs, marginBottom: theme.spacing.sm }}>
                <select 
                  value={file.selectedConfiguration || ''} 
                  onChange={(e) => {
                    updateFileConfig(index, 'selectedConfiguration', e.target.value);
                    if (e.target.value) {
                      applyTemplate(index, e.target.value);
                    }
                  }}
                  style={{
                    flex: 1,
                    padding: theme.spacing.xs,
                    border: `1px solid ${theme.colors.border}`,
                    borderRadius: theme.borderRadius.sm,
                    fontSize: '12px',
                  }}
                >
                  <option value="">Select bank...</option>
                  {templates.map(config => (
                    <option key={config} value={config}>{config}</option>
                  ))}
                </select>
                <Button 
                  variant="secondary"
                  size="small"
                  // Pass true to indicate re-parse
                  onClick={() => previewFile(index, true)} 
                  disabled={loading}
                >
                  Reparse
                </Button>
              </div>

              {/* Bank Detection Info */}
              {file.detectedBank && (
                <div style={{
                  fontSize: '12px',
                  color: theme.colors.text.secondary,
                  backgroundColor: theme.colors.background.paper,
                  padding: theme.spacing.xs,
                  borderRadius: theme.borderRadius.sm,
                }}>
                  Detected: {file.detectedBank} | 
                  Rows: {displayRowCount}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </Card>
  );
}

export default AdvancedConfigPanel;