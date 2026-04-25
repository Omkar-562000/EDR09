import { useMemo, useState } from "react";

export default function AlertsPanel({ detections, onSelectAlert, fullScreen = false }) {
  const [sortBy, setSortBy] = useState("timestamp");
  const [filterSeverity, setFilterSeverity] = useState("all");
  const [filterStatus, setFilterStatus] = useState("all");
  const [searchTerm, setSearchTerm] = useState("");

  // Map severity levels to numeric values for sorting
  const severityMap = { critical: 3, high: 2, medium: 1, low: 0 };

  const filtered = useMemo(() => {
    let result = [...detections];

    // Filter by severity
    if (filterSeverity !== "all") {
      result = result.filter(d => 
        (d.severity || "low").toLowerCase() === filterSeverity
      );
    }

    // Filter by status
    if (filterStatus !== "all") {
      // Status filtering - we'll consider "critical" and "high" as "active" 
      if (filterStatus === "active") {
        result = result.filter(d => 
          ["critical", "high", "medium"].includes((d.severity || "low").toLowerCase())
        );
      } else if (filterStatus === "resolved") {
        result = result.filter(d => 
          (d.severity || "low").toLowerCase() === "low"
        );
      }
    }

    // Search
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      result = result.filter(d => 
        (d.detection_id || "").toLowerCase().includes(term) ||
        (d.rule_name || "").toLowerCase().includes(term) ||
        (d.description || "").toLowerCase().includes(term) ||
        (d.event?.title || "").toLowerCase().includes(term)
      );
    }

    // Sort
    result.sort((a, b) => {
      if (sortBy === "timestamp") {
        return new Date(b.timestamp || 0) - new Date(a.timestamp || 0);
      } else if (sortBy === "severity") {
        const aSev = severityMap[(a.severity || "low").toLowerCase()] || 0;
        const bSev = severityMap[(b.severity || "low").toLowerCase()] || 0;
        return bSev - aSev;
      }
      return 0;
    });

    return result;
  }, [detections, filterSeverity, filterStatus, searchTerm, sortBy]);

  const getSeverityClass = (severity) => {
    const level = (severity || "low").toLowerCase();
    if (level === "critical" || level === "high") return "severity-critical";
    if (level === "medium") return "severity-medium";
    return "severity-low";
  };

  const formatTime = (timestamp) => {
    if (!timestamp) return "N/A";
    try {
      return new Date(timestamp).toLocaleTimeString();
    } catch {
      return timestamp;
    }
  };

  return (
    <section className={`panel alerts-panel ${fullScreen ? "fullscreen" : ""}`}>
      <div className="panel-header">
        <h2>Alerts</h2>
        <div className="panel-controls">
          <input 
            type="text"
            className="search-input"
            placeholder="Search alerts..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          <select 
            className="filter-select"
            value={filterSeverity}
            onChange={(e) => setFilterSeverity(e.target.value)}
          >
            <option value="all">All Severities</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
          <select 
            className="filter-select"
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
          >
            <option value="all">All Status</option>
            <option value="active">Active</option>
            <option value="resolved">Resolved</option>
          </select>
          <select 
            className="sort-select"
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
          >
            <option value="timestamp">Latest First</option>
            <option value="severity">Highest Severity</option>
          </select>
        </div>
      </div>

      <div className="alerts-table-container">
        {filtered.length === 0 ? (
          <div className="empty-state">
            <span className="empty-icon">🎯</span>
            <p>No alerts match your criteria</p>
          </div>
        ) : (
          <table className="alerts-table">
            <thead>
              <tr>
                <th>Alert ID</th>
                <th>Threat Type</th>
                <th>Severity</th>
                <th>Process</th>
                <th>Timestamp</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((detection, idx) => (
                <tr 
                  key={idx} 
                  className={`alert-row ${getSeverityClass(detection.severity)}`}
                  onClick={() => onSelectAlert && onSelectAlert(detection)}
                  style={{ cursor: onSelectAlert ? "pointer" : "default" }}
                >
                  <td className="cell-id">{detection.detection_id?.substring(0, 8) || `ALT-${idx}`}</td>
                  <td className="cell-threat">{detection.rule_name || detection.description || "Unknown"}</td>
                  <td className="cell-severity">
                    <span className={`severity-badge ${getSeverityClass(detection.severity)}`}>
                      {(detection.severity || "low").toUpperCase()}
                    </span>
                  </td>
                  <td className="cell-process">{detection.event?.title || detection.event?.payload?.process_name || "System"}</td>
                  <td className="cell-timestamp">{formatTime(detection.timestamp)}</td>
                  <td className="cell-status">
                    <span className={`status-badge status-active`}>
                      ACTIVE
                    </span>
                  </td>
                  <td className="cell-action">
                    <button 
                      className="btn-view"
                      onClick={(e) => {
                        e.stopPropagation();
                        onSelectAlert && onSelectAlert(detection);
                      }}
                    >
                      View
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
      <div className="panel-footer">
        <span>{filtered.length} of {detections.length} alerts</span>
      </div>
    </section>
  );
}
