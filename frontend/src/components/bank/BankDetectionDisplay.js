import React from 'react';

/**
 * Component for displaying bank detection results
 * Shows detected bank, confidence level, and auto-configuration status
 */
function BankDetectionDisplay({ bankDetection, preview, parsedData, loading }) {
  console.log(' DEBUG: BankDetectionDisplay render with:', {
    bankDetection: bankDetection,
    preview: preview ? 'preview exists' : 'no preview',
    parsedData: parsedData ? 'parsedData exists' : 'no parsedData',
    loading: loading
  });
  
  // Determine display information source priority: parsed data > preview > filename detection
  let displayInfo = null;
  let source = 'frontend';
  
  if (parsedData?.bank_info && Object.keys(parsedData.bank_info).length > 0) {
    displayInfo = {
      bankType: parsedData.bank_info.bank_type || parsedData.bank_info.detected_bank || 'Unknown',
      confidence: parsedData.bank_info.confidence,
      source: 'Backend (Parse)'
    };
    source = 'backend';
    console.log(' DEBUG: Using bank info from parsed data:', parsedData.bank_info);
  } else if (preview?.bank_detection && preview.bank_detection.detected_bank) {
    // Use 'bank_detection' from preview response
    displayInfo = {
      bankType: preview.bank_detection.detected_bank || 'Unknown',
      confidence: preview.bank_detection.confidence,
      source: 'Backend (Preview)'
    };
    source = 'backend';
    console.log(' DEBUG: Using bank_detection from preview:', preview.bank_detection);
  } else if (preview?.bank_info && Object.keys(preview.bank_info).length > 0) {
    // Fallback: original bank_info check for backward compatibility
    displayInfo = {
      bankType: preview.bank_info.bank_type || preview.bank_info.detected_bank || 'Unknown',
      confidence: preview.bank_info.confidence,
      source: 'Backend (Preview)'
    };
    source = 'backend';
    console.log(' DEBUG: Using bank info from preview:', preview.bank_info);
  } else if (bankDetection && bankDetection.detected_bank) {
    // Check if bankDetection has detected_bank (from stored bank detection data)
    displayInfo = {
      bankType: bankDetection.detected_bank || 'Unknown',
      confidence: bankDetection.confidence,
      source: 'Backend (Stored)'
    };
    source = 'backend';
    console.log(' DEBUG: Using stored bank detection:', bankDetection);
  } else if (bankDetection && bankDetection.bankType) {
    // Legacy frontend detection
    displayInfo = {
      bankType: bankDetection.bankType || 'Unknown',
      confidence: null,
      source: 'Frontend (Filename)'
    };
    console.log(' DEBUG: Using frontend bank detection:', bankDetection);
  } else {
    console.log(' DEBUG: No bank detection data found anywhere');
  }
  
  // Loading state
  if (!displayInfo && loading) {
    return (
      <div className="bank-detection">
        <h5> Bank Detection</h5>
        <div className="detection-results">
          <span className="bank-badge detecting">
             Detecting...
          </span>
          <span className="detection-source">
            (Analyzing file content)
          </span>
        </div>
      </div>
    );
  }
  
  // No detection data available
  if (!displayInfo) {
    return (
      <div className="bank-detection">
        <h5> Bank Detection</h5>
        <div className="detection-results">
          <span className="bank-badge unknown">
            UNKNOWN
          </span>
          <span className="detection-source">
            (Click Preview to detect)
          </span>
        </div>
      </div>
    );
  }
  
  const displayBankType = formatBankType(displayInfo.bankType);
  const isDetected = displayBankType !== 'Unknown';
  
  return (
    <div className="bank-detection">
      <h5> Bank Detection</h5>
      <div className="detection-results">
        <span className={`bank-badge ${displayBankType.toLowerCase().replace(/\s+/g, '-')}`}>
          {displayBankType}
        </span>
        {displayInfo.confidence !== null && (
          <span className="confidence-score">
            {Math.round(displayInfo.confidence * 100)}% confidence
          </span>
        )}
        <span className="detection-source">
          ({displayInfo.source})
        </span>
        {isDetected && preview && (
          <span className="detection-note">
            [SUCCESS] Auto-configured: Headers Row {preview.suggested_header_row || 0}, Data Row {preview.suggested_data_start_row || 0}
          </span>
        )}
      </div>
    </div>
  );
}

/**
 * Formats bank type for user display
 */
const formatBankType = (bankType) => {
  if (!bankType || bankType === 'Unknown') return 'Unknown';
  
  // Handle backend bank types
  if (bankType === 'nayapay') return 'NayaPay';
  if (bankType === 'forint_bank') return 'Forint Bank';
  if (bankType === 'wise_usd') return 'Wise USD';
  if (bankType === 'wise_eur') return 'Wise EUR';
  if (bankType === 'wise_huf') return 'Wise HUF';
  if (bankType === 'wise_family') return 'Wise Family';
  
  // Handle frontend bank types
  if (bankType === 'Transferwise') return 'Wise';
  
  return bankType;
};

export default BankDetectionDisplay;
