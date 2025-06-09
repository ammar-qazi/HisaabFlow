import React from 'react';

function TransferSummaryStats({ summary }) {
  return (
    <div className="summary-stats">
      <div className="stat-card">
        <span className="stat-number">{summary.transfer_pairs_found}</span>
        <span className="stat-label">Transfer Pairs</span>
      </div>
      <div className="stat-card">
        <span className="stat-number">{summary.potential_transfers}</span>
        <span className="stat-label">Potential Transfers</span>
      </div>
      <div className="stat-card">
        <span className="stat-number">{summary.conflicts}</span>
        <span className="stat-label">Conflicts</span>
      </div>
      <div className="stat-card">
        <span className="stat-number">{summary.flagged_for_review}</span>
        <span className="stat-label">Flagged for Review</span>
      </div>
    </div>
  );
}

function DetectedTransfers({ transfers }) {
  if (!transfers || transfers.length === 0) return null;
  
  return (
    <div className="detected-transfers">
      <h5>💸 Detected Transfer Pairs</h5>
      {transfers.map((pair, index) => (
        <div key={index} className="transfer-pair">
          <div className="transfer-out">
            <span className="transfer-label">📤 OUT:</span>
            <span className="transfer-desc">{pair.outgoing.Description}</span>
            <span className="transfer-amount">-{pair.amount}</span>
            <span className="transfer-account">({pair.outgoing._csv_name})</span>
          </div>
          <div className="transfer-arrow">↓</div>
          <div className="transfer-in">
            <span className="transfer-label">📥 IN:</span>
            <span className="transfer-desc">{pair.incoming.Description}</span>
            <span className="transfer-amount">+{pair.incoming.Amount}</span>
            <span className="transfer-account">({pair.incoming._csv_name})</span>
          </div>
          <div className="transfer-confidence">
            Confidence: {(pair.confidence * 100).toFixed(0)}%
          </div>
        </div>
      ))}
    </div>
  );
}

function TransferConflicts({ conflicts }) {
  if (!conflicts || conflicts.length === 0) return null;
  
  return (
    <div className="transfer-conflicts">
      <h5>⚠️ Transfer Conflicts</h5>
      <p>These transactions have multiple potential matches and need manual review:</p>
      {conflicts.map((conflict, index) => (
        <div key={index} className="conflict-item">
          <p><strong>Transaction:</strong> {conflict.outgoing_transaction.Description}</p>
          <p><strong>Potential matches:</strong> {conflict.potential_matches.length}</p>
        </div>
      ))}
    </div>
  );
}

function TransferAnalysis({ transferAnalysis }) {
  if (!transferAnalysis) return null;
  
  return (
    <div className="transfer-analysis">
      <h4>🔄 Transfer Detection Results</h4>
      <div className="transfer-summary">
        <TransferSummaryStats summary={transferAnalysis.summary} />
        <DetectedTransfers transfers={transferAnalysis.transfers} />
        <TransferConflicts conflicts={transferAnalysis.conflicts} />
      </div>
    </div>
  );
}

export default TransferAnalysis;
