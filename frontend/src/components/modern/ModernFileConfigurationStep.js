import React, { useState } from 'react';
import { useTheme } from '../../theme/ThemeProvider';
import { Card, Button, Badge } from '../ui';
import { 
  ChevronLeft, ChevronRight, Settings, Eye, FileText, 
  Building, CheckCircle, AlertCircle, Plus, Minus 
} from '../ui/Icons';

function ModernFileConfigurationStep({ 
  currentStep,
  uploadedFiles,
  activeTab,
  setActiveTab,
  templates,
  loading,
  updateFileConfig,
  updateColumnMapping,
  applyTemplate,
  previewFile,
  parseAllFiles,
  setCurrentStep
}) {
  const theme = useTheme();
  const [selectedFileIndex, setSelectedFileIndex] = useState(null);
  const [expandedSections, setExpandedSections] = useState({});

  if (currentStep < 2 || uploadedFiles.length === 0) return null;

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

  const allFilesConfigured = uploadedFiles.every(file => getFileStatus(file).status === 'configured');

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  // Dashboard View - Show all files
  if (selectedFileIndex === null) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: theme.spacing.lg }}>
        {/* Step Header */}
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
              2
            </div>
            <div>
              <h2 style={{
                margin: 0,
                fontSize: '24px',
                fontWeight: '600',
                color: theme.colors.text.primary,
                marginBottom: '4px',
              }}>
                Configure File Parsing
              </h2>
              <p style={{
                margin: 0,
                fontSize: '14px',
                color: theme.colors.text.secondary,
              }}>
                Set up bank detection and column mapping for each file
              </p>
            </div>
          </div>

          {/* Progress Summary */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: theme.spacing.md,
            padding: theme.spacing.md,
            backgroundColor: theme.colors.background.elevated,
            borderRadius: theme.borderRadius.md,
            marginBottom: theme.spacing.lg,
          }}>
            <Settings size={20} color={theme.colors.primary} />
            <div style={{ flex: 1 }}>
              <div style={{
                fontSize: '14px',
                fontWeight: '500',
                color: theme.colors.text.primary,
                marginBottom: '4px',
              }}>
                Configuration Progress
              </div>
              <div style={{
                fontSize: '12px',
                color: theme.colors.text.secondary,
              }}>
                {uploadedFiles.filter(f => getFileStatus(f).status === 'configured').length} of {uploadedFiles.length} files configured
              </div>
            </div>
            <Badge 
              variant={allFilesConfigured ? 'success' : 'warning'}
              style={{ display: 'flex', alignItems: 'center', gap: '4px' }}
            >
              {allFilesConfigured ? (
                <>
                  <CheckCircle size={12} />
                  All Ready
                </>
              ) : (
                <>
                  <AlertCircle size={12} />
                  {uploadedFiles.length - uploadedFiles.filter(f => getFileStatus(f).status === 'configured').length} Pending
                </>
              )}
            </Badge>
          </div>
        </Card>

        {/* File Grid */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))',
          gap: theme.spacing.lg,
        }}>
          {uploadedFiles.map((file, index) => {
            const fileStatus = getFileStatus(file);
            const StatusIcon = fileStatus.icon;
            
            return (
              <Card 
                key={index}
                padding="lg" 
                elevated 
                style={{
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                  border: `2px solid ${fileStatus.status === 'configured' ? theme.colors.success : theme.colors.border}`,
                }}
                onClick={() => setSelectedFileIndex(index)}
              >
                {/* File Header */}
                <div style={{
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: theme.spacing.sm,
                  marginBottom: theme.spacing.md,
                }}>
                  <FileText size={20} color={theme.colors.primary} />
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{
                      fontSize: '16px',
                      fontWeight: '500',
                      color: theme.colors.text.primary,
                      marginBottom: '4px',
                      wordBreak: 'break-word',
                    }}>
                      {file.fileName}
                    </div>
                    <div style={{
                      fontSize: '12px',
                      color: theme.colors.text.secondary,
                    }}>
                      Click to configure
                    </div>
                  </div>
                  <Badge 
                    variant={fileStatus.variant}
                    style={{ display: 'flex', alignItems: 'center', gap: '4px' }}
                  >
                    <StatusIcon size={12} />
                    {fileStatus.label}
                  </Badge>
                </div>

                {/* Quick Status */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: theme.spacing.xs }}>
                  {/* Bank Detection */}
                  <div style={{ display: 'flex', alignItems: 'center', gap: theme.spacing.sm }}>
                    <Building size={14} color={theme.colors.text.secondary} />
                    <span style={{ fontSize: '12px', color: theme.colors.text.secondary }}>
                      Bank: {file.preview?.bank_detection?.detected_bank || 'Not detected'}
                    </span>
                    {file.preview?.bank_detection?.confidence && (
                      <span style={{ fontSize: '12px', color: theme.colors.success }}>
                        ({Math.round(file.preview.bank_detection.confidence * 100)}%)
                      </span>
                    )}
                  </div>

                  {/* Configuration */}
                  <div style={{ display: 'flex', alignItems: 'center', gap: theme.spacing.sm }}>
                    <Settings size={14} color={theme.colors.text.secondary} />
                    <span style={{ fontSize: '12px', color: theme.colors.text.secondary }}>
                      Config: {file.selectedConfiguration || 'Not selected'}
                    </span>
                  </div>

                  {/* Column Mapping */}
                  <div style={{ display: 'flex', alignItems: 'center', gap: theme.spacing.sm }}>
                    <Eye size={14} color={theme.colors.text.secondary} />
                    <span style={{ fontSize: '12px', color: theme.colors.text.secondary }}>
                      Columns: {Object.keys(file.columnMapping || {}).length} mapped
                    </span>
                  </div>
                </div>
              </Card>
            );
          })}
        </div>

        {/* Navigation Buttons */}
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
            onClick={() => setCurrentStep(1)}
            leftIcon={<ChevronLeft size={18} />}
          >
            Back to Upload
          </Button>
          
          <Button
            variant="primary"
            size="large"
            disabled={loading || !allFilesConfigured}
            onClick={parseAllFiles}
            rightIcon={loading ? null : <ChevronRight size={18} />}
            loading={loading}
          >
            {loading ? 'Parsing Files...' : 'Parse Files'}
          </Button>
        </div>
      </div>
    );
  }

  // Detail View - Configure specific file
  const currentFile = uploadedFiles[selectedFileIndex];
  if (!currentFile) return null;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: theme.spacing.lg }}>
      {/* Detail Header */}
      <Card padding="lg" elevated>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: theme.spacing.md,
          marginBottom: theme.spacing.lg,
        }}>
          <Button
            variant="outline"
            size="small"
            onClick={() => setSelectedFileIndex(null)}
            leftIcon={<ChevronLeft size={16} />}
          >
            Back to Overview
          </Button>
          <div style={{ flex: 1 }}>
            <h3 style={{
              margin: 0,
              fontSize: '18px',
              fontWeight: '600',
              color: theme.colors.text.primary,
            }}>
              Configure: {currentFile.fileName}
            </h3>
          </div>
          <Badge variant={getFileStatus(currentFile).variant}>
            {getFileStatus(currentFile).label}
          </Badge>
        </div>
      </Card>

      {/* Configuration Sections */}
      <Card padding="lg" elevated>
        {/* Bank Detection */}
        <div style={{
          padding: theme.spacing.md,
          backgroundColor: theme.colors.background.elevated,
          borderRadius: theme.borderRadius.md,
          marginBottom: theme.spacing.md,
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: theme.spacing.sm,
            marginBottom: theme.spacing.sm,
          }}>
            <Building size={18} color={theme.colors.primary} />
            <span style={{ fontWeight: '500', color: theme.colors.text.primary }}>
              Bank Detection
            </span>
          </div>
          {currentFile.preview?.bank_detection ? (
            <div style={{ fontSize: '14px', color: theme.colors.text.primary }}>
              <strong>{currentFile.preview.bank_detection.detected_bank}</strong>
              <span style={{ color: theme.colors.text.secondary, marginLeft: theme.spacing.sm }}>
                ({Math.round(currentFile.preview.bank_detection.confidence * 100)}% confidence)
              </span>
            </div>
          ) : (
            <div style={{ fontSize: '14px', color: theme.colors.text.secondary }}>
              Click Preview to detect bank
            </div>
          )}
        </div>

        {/* Configuration Selection */}
        <div style={{
          padding: theme.spacing.md,
          backgroundColor: theme.colors.background.elevated,
          borderRadius: theme.borderRadius.md,
          marginBottom: theme.spacing.md,
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: theme.spacing.sm,
            marginBottom: theme.spacing.sm,
          }}>
            <Settings size={18} color={theme.colors.primary} />
            <span style={{ fontWeight: '500', color: theme.colors.text.primary }}>
              Bank Configuration
            </span>
          </div>
          <div style={{ display: 'flex', gap: theme.spacing.sm, alignItems: 'center' }}>
            <select 
              value={currentFile.selectedConfiguration || ''} 
              onChange={(e) => {
                updateFileConfig(selectedFileIndex, 'selectedConfiguration', e.target.value);
                if (e.target.value) {
                  applyTemplate(selectedFileIndex, e.target.value);
                }
              }}
              style={{
                flex: 1,
                padding: theme.spacing.sm,
                border: `1px solid ${theme.colors.border}`,
                borderRadius: theme.borderRadius.sm,
                fontSize: '14px',
              }}
            >
              <option value="">Select configuration...</option>
              {templates.map(config => (
                <option key={config} value={config}>{config}</option>
              ))}
            </select>
            <Button 
              variant="secondary"
              size="small"
              onClick={() => previewFile(selectedFileIndex)}
              disabled={loading}
            >
              Preview
            </Button>
          </div>
        </div>

        {/* Column Mapping Summary */}
        <div style={{
          padding: theme.spacing.md,
          backgroundColor: theme.colors.background.elevated,
          borderRadius: theme.borderRadius.md,
          marginBottom: theme.spacing.md,
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: theme.spacing.sm,
            marginBottom: theme.spacing.sm,
          }}>
            <Eye size={18} color={theme.colors.primary} />
            <span style={{ fontWeight: '500', color: theme.colors.text.primary }}>
              Column Mapping
            </span>
          </div>
          <div style={{ fontSize: '14px', color: theme.colors.text.secondary }}>
            {Object.keys(currentFile.columnMapping || {}).length} columns mapped
            {Object.keys(currentFile.columnMapping || {}).length > 0 && (
              <div style={{ marginTop: theme.spacing.xs }}>
                {Object.entries(currentFile.columnMapping || {}).slice(0, 3).map(([key, value]) => (
                  <span key={key} style={{ 
                    display: 'inline-block',
                    margin: '2px 4px 2px 0',
                    padding: '2px 6px',
                    backgroundColor: theme.colors.primary + '20',
                    borderRadius: theme.borderRadius.sm,
                    fontSize: '12px',
                  }}>
                    {key} → {value}
                  </span>
                ))}
                {Object.keys(currentFile.columnMapping || {}).length > 3 && (
                  <span style={{ fontSize: '12px', color: theme.colors.text.secondary }}>
                    +{Object.keys(currentFile.columnMapping || {}).length - 3} more
                  </span>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Preview Data (Expandable) */}
        {currentFile.preview && (
          <div style={{
            padding: theme.spacing.md,
            backgroundColor: theme.colors.background.elevated,
            borderRadius: theme.borderRadius.md,
          }}>
            <div 
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: theme.spacing.sm,
                cursor: 'pointer',
              }}
              onClick={() => toggleSection('preview')}
            >
              <Eye size={18} color={theme.colors.primary} />
              <span style={{ fontWeight: '500', color: theme.colors.text.primary }}>
                Data Preview
              </span>
              {expandedSections.preview ? (
                <Minus size={16} color={theme.colors.text.secondary} />
              ) : (
                <Plus size={16} color={theme.colors.text.secondary} />
              )}
            </div>
            {expandedSections.preview && (
              <div style={{
                marginTop: theme.spacing.md,
                overflowX: 'auto',
                border: `1px solid ${theme.colors.border}`,
                borderRadius: theme.borderRadius.md,
              }}>
                <table style={{
                  width: '100%',
                  borderCollapse: 'collapse',
                  fontSize: '12px',
                }}>
                  <thead>
                    <tr style={{ backgroundColor: theme.colors.background.paper }}>
                      <th style={{ padding: theme.spacing.xs, textAlign: 'left', minWidth: '40px' }}>Row</th>
                      {currentFile.preview.column_names.slice(0, 6).map((col, idx) => (
                        <th key={idx} style={{ 
                          padding: theme.spacing.xs, 
                          textAlign: 'left',
                          borderLeft: `1px solid ${theme.colors.border}`,
                        }}>
                          {col}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {currentFile.preview.preview_data.slice(0, 3).map((row, idx) => (
                      <tr key={idx} style={{
                        borderTop: `1px solid ${theme.colors.border}`,
                      }}>
                        <td style={{ 
                          padding: theme.spacing.xs, 
                          fontWeight: '500',
                          backgroundColor: theme.colors.background.elevated,
                        }}>
                          {idx}
                        </td>
                        {Object.values(row).slice(0, 6).map((cell, cellIdx) => (
                          <td key={cellIdx} style={{ 
                            padding: theme.spacing.xs,
                            borderLeft: `1px solid ${theme.colors.border}`,
                          }}>
                            {cell || ''}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}
      </Card>
    </div>
  );
}

export default ModernFileConfigurationStep;
