import React from 'react';

function UserSettings({ 
  userName, 
  setUserName, 
  dateTolerance, 
  setDateTolerance, 
  enableTransferDetection, 
  setEnableTransferDetection 
}) {
  return (
    <div className="settings-section">
      <h3>⚙️ Transfer Detection Settings</h3>
      <div className="settings-grid">
        <div className="setting-item">
          <label>Your Name (for transfer matching)</label>
          <input
            type="text"
            value={userName}
            onChange={(e) => setUserName(e.target.value)}
            placeholder="Enter your full name"
          />
        </div>
        <div className="setting-item">
          <label>Date Tolerance (hours)</label>
          <input
            type="number"
            value={dateTolerance}
            onChange={(e) => setDateTolerance(parseInt(e.target.value))}
            min="1"
            max="168"
          />
        </div>
        <div className="setting-item">
          <label>
            <input
              type="checkbox"
              checked={enableTransferDetection}
              onChange={(e) => setEnableTransferDetection(e.target.checked)}
            />
            Enable Transfer Detection
          </label>
        </div>
      </div>
    </div>
  );
}

export default UserSettings;
