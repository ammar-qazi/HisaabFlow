import axios from 'axios';

const API_BASE = 'http://127.0.0.1:8000';
const API_V1_BASE = `${API_BASE}/api/v1`;

// Processing functions
export const createProcessingHandlers = (state) => {
  const { 
    uploadedFiles, 
    setUploadedFiles, 
    setLoading, 
    setError, 
    setSuccess,
    setParsedResults,
    setTransformedData,
    setTransferAnalysis,
    setCurrentStep
  } = state;

  // parseAllFiles function remains the same...
  const parseAllFiles = async () => {
    if (uploadedFiles.length === 0) return;
    
    setError(null);
    setSuccess(null);
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
      setSuccess(`Successfully parsed ${results.length} CSV files`);
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
    setSuccess(null);
    setLoading(true);
    
    try {
      // **FIX:** Filter for files with valid parsedData and include bank detection from preview
      const csvDataList = uploadedFiles
        .filter(file => file.parsedData && file.parsedData.success)
        .map(file => ({
          filename: file.fileName,
          data: file.parsedData.data,
          headers: file.parsedData.headers,
          // **KEY FIX:** Use bank detection from preview instead of parsedData
          bank_info: file.preview?.bank_detection || file.parsedData.bank_info || {},
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
      setSuccess(`Transformation complete! ${response.data.transformation_summary.total_transactions} transactions processed`);
      setCurrentStep(3);
      
    } catch (err) {
      setError(`Transformation failed: ${err.response?.data?.detail || err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return { parseAllFiles, transformAllFiles };
};