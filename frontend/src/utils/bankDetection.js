/**
 * Bank detection utilities
 * Frontend filename-based bank detection
 */

/**
 * Detects bank type from filename patterns
 */
export const detectBankFromFilename = (filename) => {
  const lowerFilename = filename.toLowerCase();
  
  if (lowerFilename.includes('nayapay')) {
    return {
      bankType: 'NayaPay',
      suggestedTemplate: 'Nayapay Configuration',
      cleanedTemplate: 'Nayapay Configuration',
      defaultStartRow: 13,
      defaultEncoding: 'utf-8'
    };
  }
  
  if (lowerFilename.includes('transferwise') || lowerFilename.includes('wise')) {
    // Determine specific Wise configuration based on filename
    if (lowerFilename.includes('usd')) {
      return {
        bankType: 'Transferwise',
        suggestedTemplate: 'Wise_Usd Configuration',
        defaultStartRow: 0,
        defaultEncoding: 'utf-8'
      };
    } else if (lowerFilename.includes('huf')) {
      return {
        bankType: 'Transferwise',
        suggestedTemplate: 'Wise_Huf Configuration',
        defaultStartRow: 0,
        defaultEncoding: 'utf-8'
      };
    } else {
      // Default to EUR for generic Wise files
      return {
        bankType: 'Transferwise',
        suggestedTemplate: 'Wise_Eur Configuration',
        defaultStartRow: 0,
        defaultEncoding: 'utf-8'
      };
    }
  }
  
  return {
    bankType: 'Unknown',
    suggestedTemplate: '',
    defaultStartRow: 0,
    defaultEncoding: 'utf-8'
  };
};
