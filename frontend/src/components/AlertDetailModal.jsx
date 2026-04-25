export default function AlertDetailModal({ alert, onClose }) {
  const getSeverityClass = (severity) => {
    const level = (severity || "low").toLowerCase();
    if (level === "critical" || level === "high") return "severity-critical";
    if (level === "medium") return "severity-medium";
    return "severity-low";
  };

  const formatTime = (timestamp) => {
    if (!timestamp) return "N/A";
    try {
      return new Date(timestamp).toLocaleString();
    } catch {
      return timestamp;
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Alert Details</h2>
          <button className="btn-close" onClick={onClose}>✕</button>
        </div>

        <div className="modal-body">
          <div className="detail-grid">
            <div className="detail-item">
              <label>Detection ID</label>
              <div className="value">{alert.detection_id?.substring(0, 12) || "N/A"}</div>
            </div>

            <div className="detail-item">
              <label>Rule Name</label>
              <div className="value">{alert.rule_name || "Unknown"}</div>
            </div>

            <div className="detail-item">
              <label>Severity</label>
              <div className="value">
                <span className={`severity-badge ${getSeverityClass(alert.severity)}`}>
                  {(alert.severity || "LOW").toUpperCase()}
                </span>
              </div>
            </div>

            <div className="detail-item">
              <label>Confidence</label>
              <div className="value">{alert.confidence || 0}%</div>
            </div>

            <div className="detail-item">
              <label>Timestamp</label>
              <div className="value">{formatTime(alert.timestamp)}</div>
            </div>

            <div className="detail-item">
              <label>Detection Source</label>
              <div className="value">{alert.event?.source || alert.source || "N/A"}</div>
            </div>

            <div className="detail-item">
              <label>Rule ID</label>
              <div className="value">{alert.rule_id || "N/A"}</div>
            </div>

            <div className="detail-item full-width">
              <label>Description</label>
              <div className="value">
                {alert.description || "No description available"}
              </div>
            </div>

            {alert.tactics && alert.tactics.length > 0 && (
              <div className="detail-item full-width">
                <label>MITRE ATT&CK Tactics</label>
                <div className="tags">
                  {alert.tactics.map((tactic, idx) => (
                    <span key={idx} className="tag">{tactic}</span>
                  ))}
                </div>
              </div>
            )}

            {alert.techniques && alert.techniques.length > 0 && (
              <div className="detail-item full-width">
                <label>MITRE ATT&CK Techniques</label>
                <div className="tags">
                  {alert.techniques.map((technique, idx) => (
                    <span key={idx} className="tag">{technique}</span>
                  ))}
                </div>
              </div>
            )}

            {alert.event && (
              <div className="detail-item full-width">
                <label>Related Event</label>
                <div style={{ color: 'var(--muted)', fontSize: '0.85rem' }}>
                  <div><strong>Event Type:</strong> {alert.event.event_type}</div>
                  <div><strong>Title:</strong> {alert.event.title}</div>
                  <div><strong>Host:</strong> {alert.event.host}</div>
                </div>
              </div>
            )}

            <div className="detail-item full-width">
              <label>Raw Data</label>
              <pre className="raw-data">
                {JSON.stringify(alert, null, 2)}
              </pre>
            </div>
          </div>
        </div>

        <div className="modal-footer">
          <button className="btn-secondary" onClick={onClose}>Close</button>
          {alert.status !== "resolved" && (
            <button className="btn-primary">Mark as Resolved</button>
          )}
        </div>
      </div>
    </div>
  );
}
