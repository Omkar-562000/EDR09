import { useMemo, useState } from "react";

export default function LogsViewer({ events }) {
  const [filterType, setFilterType] = useState("all");
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedLog, setSelectedLog] = useState(null);

  const getEventType = (event) => {
    return (event.event_type || event.type || "unknown").toLowerCase();
  };

  const eventTypes = useMemo(() => {
    const types = new Set();
    events?.forEach(e => {
      types.add(getEventType(e));
    });
    return Array.from(types).sort();
  }, [events]);

  const filtered = useMemo(() => {
    let result = [...(events || [])].reverse();

    // Filter by type
    if (filterType !== "all") {
      result = result.filter(e => getEventType(e) === filterType);
    }

    // Search
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      result = result.filter(e => 
        (e.title || "").toLowerCase().includes(term) ||
        (e.description || "").toLowerCase().includes(term) ||
        (e.message || "").toLowerCase().includes(term) ||
        (e.source || "").toLowerCase().includes(term)
      );
    }

    return result;
  }, [events, filterType, searchTerm]);

  const formatTime = (timestamp) => {
    if (!timestamp) return "N/A";
    try {
      const date = new Date(timestamp);
      return date.toLocaleString([], {
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit"
      });
    } catch {
      return timestamp;
    }
  };

  return (
    <section className="panel logs-panel fullscreen">
      <div className="panel-header">
        <h2>Logs Viewer</h2>
        <div className="panel-controls">
          <input 
            type="text"
            className="search-input"
            placeholder="Search logs..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          <select 
            className="filter-select"
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
          >
            <option value="all">All Types</option>
            {eventTypes.map(type => (
              <option key={type} value={type}>
                {type.charAt(0).toUpperCase() + type.slice(1)}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="logs-container">
        <div className="logs-list">
          {filtered.length === 0 ? (
            <div className="empty-state">
              <span className="empty-icon">📝</span>
              <p>No logs match your criteria</p>
            </div>
          ) : (
            filtered.map((log, idx) => (
              <div 
                key={idx}
                className={`log-entry ${selectedLog === idx ? "selected" : ""}`}
                onClick={() => setSelectedLog(selectedLog === idx ? null : idx)}
              >
                <div className="log-timestamp">{formatTime(log.timestamp)}</div>
                <div className="log-type">[{getEventType(log).toUpperCase()}]</div>
                <div className="log-message">
                  {log.title || log.message || log.description || "No message"}
                </div>
              </div>
            ))
          )}
        </div>

        {selectedLog !== null && filtered[selectedLog] && (
          <div className="log-detail">
            <div className="log-detail-header">
              <h3>Log Details</h3>
              <button 
                className="btn-close"
                onClick={() => setSelectedLog(null)}
              >
                ✕
              </button>
            </div>
            <div className="log-detail-content">
              <div className="detail-section">
                <label>Timestamp:</label>
                <code>{formatTime(filtered[selectedLog].timestamp)}</code>
              </div>
              <div className="detail-section">
                <label>Type:</label>
                <code>{getEventType(filtered[selectedLog])}</code>
              </div>
              <div className="detail-section">
                <label>Title:</label>
                <code>{filtered[selectedLog].title || "N/A"}</code>
              </div>
              {filtered[selectedLog].source && (
                <div className="detail-section">
                  <label>Source:</label>
                  <code>{filtered[selectedLog].source}</code>
                </div>
              )}
              <div className="detail-section">
                <label>Full Details:</label>
                <pre>{JSON.stringify(filtered[selectedLog], null, 2)}</pre>
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="panel-footer">
        <span>{filtered.length} of {events?.length || 0} logs</span>
      </div>
    </section>
  );
}
