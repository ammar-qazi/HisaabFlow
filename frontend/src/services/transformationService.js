/**
 * Transformation API Service
 * Handles transformation and categorization operations
 */
import axios from 'axios';

const API_BASE = 'http://127.0.0.1:8000';
const API_V1_BASE = `${API_BASE}/api/v1`;

export class TransformationService {
  /**
   * Apply transfer categorization to existing transformed data
   * @param {Object} params - Categorization parameters
   * @param {Array} params.transformedData - Existing transformed data
   * @param {Array} params.manuallyConfirmedPairs - Manual transfer confirmations
   * @param {Object} params.transferAnalysis - Transfer analysis object
   * @returns {Promise<Object>} Updated transformed data
   */
  static async applyTransferCategorization({ transformedData, manuallyConfirmedPairs, transferAnalysis }) {
    try {
      console.log(`Applying categorization for ${manuallyConfirmedPairs.length} manually confirmed pairs`);
      
      const response = await axios.post(`${API_V1_BASE}/apply-transfer-categorization`, {
        transformed_data: transformedData,
        manually_confirmed_pairs: manuallyConfirmedPairs,
        transfer_analysis: transferAnalysis
      });
      
      if (response.data.success) {
        console.log(`Successfully updated ${response.data.updated_transactions} transactions`);
        return {
          success: true,
          transformedData: response.data.transformed_data,
          updatedTransactions: response.data.updated_transactions,
          categoryApplied: response.data.category_applied
        };
      } else {
        throw new Error(response.data.error || 'Categorization failed');
      }
      
    } catch (error) {
      console.error('Transfer categorization error:', error);
      throw new Error(
        error.response?.data?.detail || 
        error.message || 
        'Failed to apply transfer categorization'
      );
    }
  }
}