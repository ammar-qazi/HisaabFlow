import axios from 'axios';
import toast from 'react-hot-toast';

const API_BASE = 'http://127.0.0.1:8000';
const API_V1_BASE = `${API_BASE}/api/v1`;

// Processing functions
export const createProcessingHandlers = (state) => {
  const { 
    uploadedFiles, 
    setUploadedFiles, 
    setLoading, 
    setError, 
    setParsedResults,
    setTransformedData,
    setTransferAnalysis,
    setCurrentStep
  } = state;

  // parseAllFiles function remains the same...
  const parseAllFiles = async () => {
    if (uploadedFiles.length === 0) return;
    
    setError(null);
    setLoading(true);
    
    try {
      const fileIds = uploadedFiles.map(f => f.fileId);
      
      const parseConfigs = await Promise.all(uploadedFiles.map(async (file) => {
        let finalConfig = { ...file.parseConfig };
        
        if (file.preview && file.preview.suggested_data_start_row !== undefined) {
          finalConfig.start_row = file.preview.suggested_data_start_row;
        } else if (file.preview && file.preview.suggested_header_row !== undefined) {
          finalConfig.start_row = file.preview.suggested_header_row + 1;
        }
        
        return finalConfig;
      }));
      
      const response = await axios.post(`${API_V1_BASE}/multi-csv/parse`, {
        file_ids: fileIds,
        parse_configs: parseConfigs
      });
      
      const results = response.data.parsed_csvs;
      
      setUploadedFiles(prev => {
        return prev.map((file, index) => {
          const result = results.find(r => r.file_id === file.fileId);
          if (result) {
            return { ...file, parsedData: result.parse_result || {} };
          }
          return file;
        });
      });
      
      setParsedResults(results);
      setCurrentStep(2);
      
    } catch (err) {
      setError(`Parsing failed: ${err.response?.data?.detail || err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const transformAllFiles = async () => {
    if (uploadedFiles.length === 0) return;
    
    setError(null);
    setLoading(true);
    
    try {
      // **FIX:** Filter for files with valid parsedData and construct the list safely.
      const csvDataList = uploadedFiles
        .filter(file => file.parsedData && file.parsedData.success)
        .map(file => ({
          filename: file.fileName,
          data: file.parsedData.data,
          headers: file.parsedData.headers,
          bank_info: file.parsedData.bank_info || {},
          // Add other necessary fields if the backend needs them
        }));

      if (csvDataList.length === 0) {
        setError("No successfully parsed files available to transform.");
        setLoading(false);
        return;
      }
      
      const response = await axios.post(`${API_V1_BASE}/multi-csv/transform`, {
        csv_data_list: csvDataList
      });
      
      setTransformedData(response.data.transformed_data);
      setTransferAnalysis(response.data.transfer_analysis);
      toast.success(`Transformation complete! ${response.data.transformation_summary.total_transactions} transactions processed.`);
      setCurrentStep(3);
      
    } catch (err) {
      setError(`Transformation failed: ${err.response?.data?.detail || err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return { parseAllFiles, transformAllFiles };
};