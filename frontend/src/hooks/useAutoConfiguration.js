import { useState } from 'react';

/**
 * Custom hook for auto-configuration logic
 * Handles bank detection mapping and auto-application of configurations
 */
export const useAutoConfiguration = () => {
  // Dynamic bank mapping - will be populated from available configurations
  const [bankConfigMapping, setBankConfigMapping] = useState({});

  // Minimum confidence threshold for auto-configuration
  const CONFIDENCE_THRESHOLD = 0.5;

  /**
   * Updates the bank configuration mapping from available configurations
   * Dynamically maps backend bank names to frontend configuration display names
   */
  const updateBankConfigMapping = (configurations, rawBankNames) => {
    if (!configurations || !rawBankNames || !Array.isArray(configurations) || !Array.isArray(rawBankNames)) {
      console.log('[WARNING] Missing or invalid configurations/rawBankNames for mapping update');
      return;
    }

    const mapping = {};
    
    // Create mapping from raw bank names to display names
    rawBankNames.forEach((bankName, index) => {
      if (configurations[index]) {
        mapping[bankName] = configurations[index];
        console.log(` Bank mapping: '${bankName}' → '${configurations[index]}'`);
      }
    });
    
    setBankConfigMapping(mapping);
    console.log(' Updated bank config mapping:', mapping);
  };

  /**
   * Maps backend detected bank to frontend configuration name
   */
  const mapBankToConfiguration = (detectedBank) => {
    return bankConfigMapping[detectedBank] || null;
  };

  /**
   * Determines if bank detection confidence is sufficient for auto-config
   */
  const shouldAutoApply = (confidence) => {
    return confidence > CONFIDENCE_THRESHOLD;
  };

  /**
   * Processes bank detection result and returns auto-config decision
   */
  const processDetectionResult = (bankDetection) => {
    if (!bankDetection || bankDetection.detected_bank === 'unknown') {
      return {
        shouldApply: false,
        configName: null,
        message: 'No bank detected'
      };
    }

    const { detected_bank: detectedBank, confidence } = bankDetection;
    const configName = mapBankToConfiguration(detectedBank);
    const shouldApply = shouldAutoApply(confidence);

    if (!configName) {
      return {
        shouldApply: false,
        configName: null,
        message: `Bank detected (${detectedBank}) but no configuration available`
      };
    }

    if (!shouldApply) {
      return {
        shouldApply: false,
        configName,
        message: `Bank detected: ${detectedBank} (${(confidence * 100).toFixed(0)}% confidence), but confidence too low for auto-configuration`
      };
    }

    return {
      shouldApply: true,
      configName,
      detectedBank,
      confidence,
      message: `Smart detection: ${detectedBank} bank detected (${(confidence * 100).toFixed(0)}% confidence). Auto-applied "${configName}".`
    };
  };

  /**
   * Generates success message for auto-configuration
   */
  const generateSuccessMessage = (detectedBank, confidence, configName, headerRow, dataRow) => {
    let message = `Smart detection: ${detectedBank} bank detected (${(confidence * 100).toFixed(0)}% confidence). Auto-applied "${configName}".`;
    
    if (headerRow !== undefined && dataRow !== undefined) {
      message += ` Headers at row ${headerRow}, data starts at row ${dataRow}.`;
    }
    
    return message;
  };

  return {
    processDetectionResult,
    mapBankToConfiguration,
    shouldAutoApply,
    generateSuccessMessage,
    updateBankConfigMapping,
    bankConfigMapping,
    CONFIDENCE_THRESHOLD
  };
};
