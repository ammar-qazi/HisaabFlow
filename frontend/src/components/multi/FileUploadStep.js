import React from 'react';

function FileUploadStep({ 
  fileInputRef, 
  handleFileSelect, 
  uploadedFiles, 
  activeTab, 
  setActiveTab, 
  removeFile 
}) {
  return (
    <div className="step">
      <div className="step-header">
        <div className="step-number">1</div>
        <h2 className="step-title">Upload Multiple CSV Files</h2>
      </div>
      
      <div 
        className="file-upload multi-file"
        onClick={() => fileInputRef.current?.click()}
      >
        <div className="file-upload-icon">📁📁📁</div>
        <div className="file-upload-text">
          Click to select multiple CSV files (Ctrl/Cmd + Click)
        </div>
        <div className="file-upload-subtext">
          Upload CSVs from different accounts/currencies for transfer detection
        </div>
      </div>
      
      <input
        type="file"
        ref={fileInputRef}
        accept=".csv"
        multiple
        style={{ display: 'none' }}
        onChange={(e) => handleFileSelect(e.target.files)}
      />
      
      {uploadedFiles.length > 0 && (
        <div className="uploaded-files">
          <h4>📋 Uploaded Files ({uploadedFiles.length})</h4>
          <div className="file-tabs">
            {uploadedFiles.map((file, index) => (
              <div 
                key={index}
                className={`file-tab ${activeTab === index ? 'active' : ''}`}
                onClick={() => setActiveTab(index)}
              >
                <span>{file.fileName}</span>
                <button 
                  className="remove-file"
                  onClick={(e) => {
                    e.stopPropagation();
                    removeFile(index);
                  }}
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default FileUploadStep;
