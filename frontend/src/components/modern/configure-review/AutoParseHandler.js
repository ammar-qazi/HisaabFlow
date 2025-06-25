import React, { useEffect } from 'react';
import { useTheme } from '../../../theme/ThemeProvider';
import { Card } from '../../ui';

function AutoParseHandler({ 
  uploadedFiles,
  parseAllFiles,
  autoParseResults,
  setShowAdvancedConfig,
  loading
}) {
  const theme = useTheme();

  // Auto-parse when component mounts or files change
  useEffect(() => {
    // Check if we have new files that aren't in the parsed results
    // Note: autoParseResults is now pre-filtered in parent component to match current files
    const currentFileIds = new Set(uploadedFiles.map(f => f.fileId));
    const parsedFileIds = new Set(autoParseResults?.map(r => r.file_id) || []);
    const unparsedFiles = uploadedFiles.filter(file => !parsedFileIds.has(file.fileId));
    
    const shouldParse = uploadedFiles.length > 0 && unparsedFiles.length > 0;
    
    if (shouldParse) {
      console.log('[START] Auto-parsing files with smart defaults...');
      console.log(`[DEBUG] Files to parse: ${uploadedFiles.length}, Currently parsed: ${autoParseResults?.length || 0}`);
      console.log(`[DEBUG] Unparsed files: ${unparsedFiles.length}`, unparsedFiles.map(f => f.fileName));
      
      // Add a small delay to allow auto-detection to complete first
      const timeoutId = setTimeout(() => {
        parseAllFilesWithDefaults();
      }, 2000); // Increased to 2 seconds to allow more time for auto-detection
      
      return () => clearTimeout(timeoutId);
    } else {
      console.log('[DEBUG] Skipping auto-parse - all files already processed');
      console.log(`[DEBUG] Files: ${uploadedFiles.length}, Parsed: ${autoParseResults?.length || 0}`);
      console.log('[DEBUG] All current files have parsing results');
    }
  }, [uploadedFiles, autoParseResults]);

  // Check for advanced config needs when we get results
  useEffect(() => {
    if (autoParseResults && autoParseResults.length > 0) {
      const needsConfig = autoParseResults.some(result => { // This logic already correctly accesses bank_info.confidence and parse_result.row_count
        const confidence = result.bank_info?.confidence || 0;
        const hasData = result.parse_result?.row_count > 0;
        return confidence < 0.8 || !hasData;
      });
      
      console.log('[DATA] Checking parsed results for config needs:', autoParseResults.length, 'files');
      console.log('[DATA] AutoParseResults content:', autoParseResults);
      console.log(' Needs manual config:', needsConfig);
      setShowAdvancedConfig(needsConfig);
    } else {
      console.log('[DATA] No autoParseResults yet, current value:', autoParseResults);
    }
  }, [autoParseResults]);

  const parseAllFilesWithDefaults = async () => {
    try {
      // Call parseAllFiles - it will update parsedResults in parent state
      await parseAllFiles(true); // Pass true to indicate auto-parse
      console.log('[DATA] Auto-parse call completed');
      
    } catch (error) {
      console.error('[ERROR]  Auto-parse failed:', error);
      setShowAdvancedConfig(true); // Show config panel on error
    }
  };

  // Step Header with loading state
  return (
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
            {autoParseResults ? 'Review Your Financial Data' : 'Processing Files...'}
          </h2>
          <p style={{
            margin: 0,
            fontSize: '14px',
            color: theme.colors.text.secondary,
          }}>
            {autoParseResults ? 
              'Verify data accuracy and review important transactions before processing' :
              'Auto-parsing files with smart defaults...'
            }
          </p>
        </div>
      </div>

      {/* Show loading state while parsing OR when we have no results yet */}
      {(loading || (!autoParseResults || autoParseResults.length === 0)) && (
        <div style={{
          padding: theme.spacing.xl,
          textAlign: 'center',
          color: theme.colors.text.secondary,
        }}>
          <div style={{
            width: '40px',
            height: '40px',
            border: `4px solid ${theme.colors.border}`,
            borderTop: `4px solid ${theme.colors.primary}`,
            borderRadius: '50%',
            animation: 'spin 1s linear infinite',
            margin: '0 auto 16px',
          }} />
          <div>
            {loading ? 
              `Parsing ${uploadedFiles.length} files with smart defaults...` :
              'Waiting for parsing results...'
            }
          </div>
        </div>
      )}
    </Card>
  );
}

export default AutoParseHandler;