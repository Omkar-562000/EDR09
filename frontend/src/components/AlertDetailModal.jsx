import { useState } from "react";

export default function AlertDetailModal({ alert, onClose }) {
  const [expandedSection, setExpandedSection] = useState(null);

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

  const toggleSection = (section) => {
    setExpandedSection(expandedSection === section ? null : section);
  };

  const payload = alert.event?.payload || {};
  const commandLine = payload.command_line || payload.cmdline || null;
  const processName = payload.process_name || payload.process || null;

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

            {(commandLine || processName) && (
              <div className="detail-item full-width command-details">
                <label
                  style={{
                    cursor: "pointer",
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center"
                  }}
                  onClick={() => toggleSection("command")}
                >
                  <span>Suspicious Activity Details</span>
                  <span style={{ fontSize: "0.8em" }}>
                    {expandedSection === "command" ? "▼" : "▶"}
                  </span>
                </label>

                {expandedSection === "command" && (
                  <div
                    style={{
                      marginTop: "10px",
                      padding: "10px",
                      backgroundColor: "#f5f5f5",
                      borderRadius: "4px"
                    }}
                  >
                    {processName && (
                      <div style={{ marginBottom: "8px" }}>
                        <strong>Process:</strong>
                        <div
                          style={{
                            wordBreak: "break-all",
                            color: "#d63031",
                            fontFamily: "monospace"
                          }}
                        >
                          {processName}
                        </div>
                      </div>
                    )}

                    {commandLine && (
                      <div>
                        <strong>Command Executed:</strong>
                        <div
                          style={{
                            wordBreak: "break-all",
                            color: "#d63031",
                            fontFamily: "monospace",
                            backgroundColor: "#fff",
                            padding: "8px",
                            borderRadius: "4px",
                            border: "1px solid #ddd",
                            maxHeight: "150px",
                            overflowY: "auto"
                          }}
                        >
                          {commandLine}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}

            {alert.event && (
              <div className="detail-item full-width">
                <label
                  style={{
                    cursor: "pointer",
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center"
                  }}
                  onClick={() => toggleSection("event")}
                >
                  <span>Event Details</span>
                  <span style={{ fontSize: "0.8em" }}>
                    {expandedSection === "event" ? "▼" : "▶"}
                  </span>
                </label>

                {expandedSection === "event" && (
                  <div style={{ marginTop: "10px", color: "var(--muted)", fontSize: "0.85rem" }}>
                    {alert.event.event_type && (
                      <div>
                        <strong>Event Type:</strong> {alert.event.event_type}
                      </div>
                    )}
                    {alert.event.title && (
                      <div>
                        <strong>Title:</strong> {alert.event.title}
                      </div>
                    )}
                    {alert.event.host && (
                      <div>
                        <strong>Host:</strong> {alert.event.host}
                      </div>
                    )}
                    {payload.pid && (
                      <div>
                        <strong>Process ID (PID):</strong> {payload.pid}
                      </div>
                    )}
                    {payload.username && (
                      <div>
                        <strong>User:</strong> {payload.username}
                      </div>
                    )}
                    {payload.remote_ip && (
                      <div>
                        <strong>Remote IP:</strong> {payload.remote_ip}
                      </div>
                    )}
                    {payload.remote_port && (
                      <div>
                        <strong>Remote Port:</strong> {payload.remote_port}
                      </div>
                    )}
                    {payload.status && (
                      <div>
                        <strong>Status:</strong> {payload.status}
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}

            {alert.tactics && alert.tactics.length > 0 && (
              <div className="detail-item full-width">
                <label>MITRE ATT&CK Tactics</label>
                <div className="tags">
                  {alert.tactics.map((tactic, idx) => (
                    <span key={idx} className="tag">
                      {tactic}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {alert.techniques && alert.techniques.length > 0 && (
              <div className="detail-item full-width">
                <label>MITRE ATT&CK Techniques</label>
                <div className="tags">
                  {alert.techniques.map((technique, idx) => (
                    <span key={idx} className="tag">
                      {technique}
                    </span>
                  ))}
                </div>
              </div>
            )}

            <div className="detail-item full-width">
              <label
                style={{
                  cursor: "pointer",
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center"
                }}
                onClick={() => toggleSection("raw")}
              >
                <span>Raw Data</span>
                <span style={{ fontSize: "0.8em" }}>
                  {expandedSection === "raw" ? "▼" : "▶"}
                </span>
              </label>

              {expandedSection === "raw" && (
                <pre className="raw-data" style={{ maxHeight: "300px", overflowY: "auto" }}>
                  {JSON.stringify(alert, null, 2)}
                </pre>
              )}
            </div>
          </div>
        </div>

        <div className="modal-footer">
          <button className="btn-secondary" onClick={onClose}>
            Close
          </button>
          {alert.status !== "resolved" && (
            <button className="btn-primary">Mark as Resolved</button>
          )}
        </div>
      </div>
    </div>
  );
}
