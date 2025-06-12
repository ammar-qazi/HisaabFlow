/**
 * Export utilities
 * Handles data export functionality
 */
import axios from 'axios';

const API_BASE = 'http://127.0.0.1:8000';

/**
 * Exports transformed data as CSV file
 */
export const exportData = async (transformedData, setSuccess, setError) => {
  if (!transformedData) return;
  
  try {
    const response = await axios.post(`${API_BASE}/export`, transformedData, {
      responseType: 'blob'
    });
    
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `multi_csv_converted_${new Date().toISOString().split('T')[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
    
    setSuccess('Multi-CSV export completed successfully');
    
  } catch (err) {
    setError(`Export failed: ${err.response?.data?.detail || err.message}`);
  }
};
