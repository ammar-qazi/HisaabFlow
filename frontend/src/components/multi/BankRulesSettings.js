import React from 'react';

function BankRulesSettings({ bankRulesSettings, setBankRulesSettings }) {
  return (
    <div className="settings-section">
      <h3>🏦 Bank-Specific Rules</h3>
      <p className="settings-description">
        Choose which bank-specific rules to apply during transformation. 
        This helps avoid conflicts and gives you control over categorization.
      </p>
      <div className="bank-rules-grid">
        <div className="bank-rule-item">
          <label>
            <input
              type="checkbox"
              checked={bankRulesSettings.enableNayaPayRules}
              onChange={(e) => setBankRulesSettings(prev => ({ 
                ...prev, 
                enableNayaPayRules: e.target.checked 
              }))}
            />
            <span className="bank-logo">🇵🇰</span>
            NayaPay Rules
            <small>Ride-hailing detection, mobile recharges, Pakistani context</small>
          </label>
        </div>
        
        <div className="bank-rule-item">
          <label>
            <input
              type="checkbox"
              checked={bankRulesSettings.enableTransferwiseRules}
              onChange={(e) => setBankRulesSettings(prev => ({ 
                ...prev, 
                enableTransferwiseRules: e.target.checked 
              }))}
            />
            <span className="bank-logo">🌍</span>
            Transferwise Rules
            <small>Card transaction cleaning, Hungarian merchants, EU context</small>
          </label>
        </div>
        
        <div className="bank-rule-item">
          <label>
            <input
              type="checkbox"
              checked={bankRulesSettings.enableUniversalRules}
              onChange={(e) => setBankRulesSettings(prev => ({ 
                ...prev, 
                enableUniversalRules: e.target.checked 
              }))}
            />
            <span className="bank-logo">🌐</span>
            Universal Rules
            <small>Cross-bank categorization (groceries, travel, dining, etc.)</small>
          </label>
        </div>
      </div>
    </div>
  );
}

export default BankRulesSettings;
