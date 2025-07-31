import React, { useState, useCallback } from 'react';
import { useTheme } from '../../theme/ThemeProvider';
import { Card, Button, Badge } from '../ui';
import { Upload, FileText, Trash2, X, ChevronRight } from '../ui/Icons';

function FileUploadStep({ 
  fileInputRef, 
  handleFileSelect, 
  uploadedFiles, 
  activeTab, 
  setActiveTab, 
  removeFile,
  currentStep,
  setCurrentStep 
}) {
  const theme = useTheme();
  const [dragOver, setDragOver] = useState(false);
  const [dragCounter, setDragCounter] = useState(0);

  // Drag and drop handlers
  const handleDragEnter = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragCounter(prev => prev + 1);
    setDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragCounter(prev => {
      const newCounter = prev - 1;
      if (newCounter === 0) {
        setDragOver(false);
      }
      return newCounter;
    });
  }, []);

  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragOver(false);
    setDragCounter(0);
    
    const files = Array.from(e.dataTransfer.files).filter(file => 
      file.name.toLowerCase().endsWith('.csv')
    );
    
    if (files.length > 0) {
      handleFileSelect(files);
    }
  }, [handleFileSelect]);

  // File upload zone styles
  const uploadZoneStyle = {
    border: `2px dashed ${dragOver ? theme.colors.primary : theme.colors.border}`,
    borderRadius: theme.borderRadius.lg,
    padding: theme.spacing.xl,
    textAlign: 'center',
    backgroundColor: dragOver 
      ? theme.colors.primary + '10' 
      : theme.colors.background.elevated,
    transition: 'all 0.3s ease',
    cursor: 'pointer',
    position: 'relative',
    overflow: 'hidden',
  };

  const uploadIconStyle = {
    fontSize: '48px',
    marginBottom: theme.spacing.md,
    color: dragOver ? theme.colors.primary : theme.colors.text.secondary,
    transition: 'all 0.3s ease',
    transform: dragOver ? 'scale(1.1)' : 'scale(1)',
  };

  const fileCardStyle = (isActive) => ({
    backgroundColor: isActive 
      ? theme.colors.primary + '15' 
      : theme.colors.background.paper,
    border: `1px solid ${isActive ? theme.colors.primary : theme.colors.border}`,
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.md,
    marginBottom: theme.spacing.sm,
    cursor: 'pointer',
    transition: 'all 0.2s ease',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    position: 'relative',
    transform: isActive ? 'translateX(4px)' : 'translateX(0)',
    boxShadow: isActive ? theme.shadows.md : theme.shadows.sm,
  });

  const hoverStyles = `
    .modern-file-card:hover {
      transform: translateX(2px) !important;
      box-shadow: ${theme.shadows.md} !important;
      border-color: ${theme.colors.primary} !important;
    }
    .modern-upload-zone:hover .upload-icon {
      transform: scale(1.05);
      color: ${theme.colors.primary};
    }
    .remove-btn:hover {
      background-color: ${theme.colors.error} !important;
      color: white !important;
      transform: scale(1.1);
    }
  `;

  return (
    <>
      <style>{hoverStyles}</style>
      
      <Card padding="xl" elevated style={{ marginBottom: theme.spacing.lg }}>
        {/* Step Header */}
        <div style={{ 
          display: 'flex', 
          alignItems: 'center', 
          marginBottom: theme.spacing.xl,
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
            1
          </div>
          <div>
            <h2 style={{
              margin: 0,
              fontSize: '24px',
              fontWeight: '600',
              color: theme.colors.text.primary,
              marginBottom: '4px',
            }}>
              Upload Bank Statements
            </h2>
            <p style={{
              margin: 0,
              fontSize: '14px',
              color: theme.colors.text.secondary,
            }}>
              Select CSV files from different accounts for comprehensive transfer detection
            </p>
          </div>
        </div>

        {/* Upload Zone */}
        <div
          className="modern-upload-zone"
          style={uploadZoneStyle}
          onDragEnter={handleDragEnter}
          onDragLeave={handleDragLeave}
          onDragOver={handleDragOver}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          <div className="upload-icon" style={uploadIconStyle}>
            <Upload size={48} />
          </div>
          <div style={{
            fontSize: '18px',
            fontWeight: '500',
            color: theme.colors.text.primary,
            marginBottom: theme.spacing.xs,
          }}>
            {dragOver ? 'Drop CSV files here' : 'Drag & drop CSV files here'}
          </div>
          <div style={{
            fontSize: '14px',
            color: theme.colors.text.secondary,
            marginBottom: theme.spacing.md,
          }}>
            Or click to browse files • Supports multiple file selection
          </div>
          <Button variant="outline" size="small">
            <Upload size={16} />
            Choose Files
          </Button>
        </div>

        {/* Hidden file input */}
        <input
          type="file"
          ref={fileInputRef}
          accept=".csv"
          multiple
          style={{ display: 'none' }}
          onChange={(e) => handleFileSelect(e.target.files)}
        />
      </Card>

      {/* Uploaded Files Section */}
      {uploadedFiles.length > 0 && (
        <Card padding="lg" elevated>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            marginBottom: theme.spacing.lg,
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: theme.spacing.sm }}>
              <FileText size={20} color={theme.colors.primary} />
              <h3 style={{
                margin: 0,
                fontSize: '18px',
                fontWeight: '600',
                color: theme.colors.text.primary,
              }}>
                Uploaded Files
              </h3>
            </div>
            <Badge variant="primary">
              {uploadedFiles.length} file{uploadedFiles.length !== 1 ? 's' : ''}
            </Badge>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: theme.spacing.xs }}>
            {uploadedFiles.map((file, index) => (
              <div 
                key={index}
                className="modern-file-card"
                style={fileCardStyle(activeTab === index)}
                onClick={() => setActiveTab(index)}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: theme.spacing.sm }}>
                  <FileText 
                    size={18} 
                    color={activeTab === index ? theme.colors.primary : theme.colors.text.secondary} 
                  />
                  <div>
                    <div style={{
                      fontSize: '14px',
                      fontWeight: '500',
                      color: theme.colors.text.primary,
                      marginBottom: '2px',
                    }}>
                      {file.fileName}
                    </div>
                    <div style={{
                      fontSize: '12px',
                      color: theme.colors.text.secondary,
                    }}>
                      CSV File • Ready for configuration
                    </div>
                  </div>
                </div>

                <Button 
                  variant="secondary"
                  size="small"
                  className="remove-btn"
                  onClick={(e) => {
                    e.stopPropagation();
                    removeFile(index);
                  }}
                  style={{
                    minWidth: 'auto',
                    padding: theme.spacing.xs,
                    borderRadius: '50%',
                    border: 'none',
                    backgroundColor: theme.colors.background.elevated,
                    color: theme.colors.text.secondary,
                    transition: 'all 0.2s ease',
                  }}
                >
                  <X size={14} />
                </Button>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Navigation Buttons */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginTop: theme.spacing.xl,
        paddingTop: theme.spacing.lg,
        borderTop: `1px solid ${theme.colors.border}`,
      }}>
        <div>
          {/* Back button placeholder - Step 1 has no back */}
        </div>
        
        <Button
          variant="primary"
          size="large"
          disabled={uploadedFiles.length === 0}
          onClick={() => setCurrentStep(2)}
          rightIcon={<ChevronRight size={18} />}
        >
          Continue to Configuration
        </Button>
      </div>
    </>
  );
}

export default FileUploadStep;
