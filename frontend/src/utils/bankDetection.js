/**
 * Bank detection utilities
 * Frontend filename-based bank detection with confidence scoring
 */

// Confidence threshold for unknown bank workflow (50%)
export const CONFIDENCE_THRESHOLD = 0.5;

/**
 * Detects bank type from filename patterns with confidence scoring
 */
export const detectBankFromFilename = (filename) => {
  const lowerFilename = filename.toLowerCase();
  
  if (lowerFilename.includes('nayapay')) {
    return {
      bankType: 'NayaPay',
      suggestedTemplate: 'Nayapay Configuration',
      cleanedTemplate: 'Nayapay Configuration',
      defaultStartRow: 13,
      defaultEncoding: 'utf-8',
      confidence: 0.9,
      detectedBank: 'NayaPay'
    };
  }
  
  if (lowerFilename.includes('transferwise') || lowerFilename.includes('wise')) {
    let confidence = 0.9;
    let template = '';
    
    // Determine specific Wise configuration based on filename
    if (lowerFilename.includes('usd')) {
      template = 'Wise_Usd Configuration';
    } else if (lowerFilename.includes('huf')) {
      template = 'Wise_Huf Configuration';
    } else {
      // Default to EUR for generic Wise files
      template = 'Wise_Eur Configuration';
      confidence = 0.7; // Lower confidence for generic wise files
    }
    
    return {
      bankType: 'Transferwise',
      suggestedTemplate: template,
      defaultStartRow: 0,
      defaultEncoding: 'utf-8',
      confidence: confidence,
      detectedBank: 'Transferwise'
    };
  }
  
  return {
    bankType: 'Unknown',
    suggestedTemplate: '',
    defaultStartRow: 0,
    defaultEncoding: 'utf-8',
    confidence: 0.0,
    detectedBank: null
  };
};

/**
 * Determines if unknown bank workflow should be triggered
 */
export const shouldTriggerUnknownBankWorkflow = (uploadedFiles) => {
  return uploadedFiles.some(file => 
    !file.detectedBank || (file.confidence || 0) < CONFIDENCE_THRESHOLD
  );
};

/**
 * Gets files that need unknown bank configuration
 */
export const getUnknownBankFiles = (uploadedFiles) => {
  return uploadedFiles.filter(file => 
    !file.detectedBank || (file.confidence || 0) < CONFIDENCE_THRESHOLD
  );
};

/**
 * Checks if a file needs manual bank configuration
 */
export const needsManualConfiguration = (file) => {
  const detection = file.bankDetection || detectBankFromFilename(file.fileName || file.name);
  return detection.bankType === 'Unknown' || (detection.confidence || 0) < CONFIDENCE_THRESHOLD;
};
