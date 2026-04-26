import { useMemo } from "react";

export default function ResponsePanel({ actions }) {
  const getActionIcon = (actionType) => {
    const type = (actionType || "").toLowerCase();
    if (type.includes("terminate") || type.includes("kill")) return "⚡";
    if (type.includes("isolate") || type.includes("block")) return "🚫";
    if (type.includes("alert")) return "🚨";
    if (type.includes("quarantine")) return "🔒";
    return "⚙️";
  };

  const getActionColor = (actionType) => {
    const type = (actionType || "").toLowerCase();
    if (type.includes("terminate") || type.includes("kill")) return "action-terminate";
    if (type.includes("isolate") || type.includes("block")) return "action-isolate";
    if (type.includes("alert")) return "action-alert";
    return "action-default";
  };

  const formatTime = (timestamp) => {
    if (!timestamp) return "N/A";
    try {
      return new Date(timestamp).toLocaleTimeString();
    } catch {
      return timestamp;
    }
  };

  const sortedActions = useMemo(() => {
    const groups = new Map();

    [...(actions || [])].forEach((action) => {
      const key = [action.action_type, action.status, action.target].join("|");
      const existing = groups.get(key);
      if (!existing) {
        groups.set(key, { ...action, occurrence_count: 1, last_seen: action.timestamp });
        return;
      }
      existing.occurrence_count += 1;
      if (new Date(action.timestamp || 0) > new Date(existing.last_seen || 0)) {
        existing.last_seen = action.timestamp;
        existing.timestamp = action.timestamp;
        existing.details = action.details;
      }
    });

    return Array.from(groups.values()).sort((a, b) =>
      new Date(b.last_seen || 0) - new Date(a.last_seen || 0)
    );
  }, [actions]);

  return (
    <section className="panel response-panel fullscreen">
      <div className="panel-header">
        <h2>Response Actions</h2>
        <span className="action-count">{actions?.length || 0} actions</span>
      </div>

      <div className="actions-container">
        {sortedActions.length === 0 ? (
          <div className="empty-state">
            <span className="empty-icon">✅</span>
            <p>No response actions taken yet</p>
          </div>
        ) : (
          <div className="actions-list">
            {sortedActions.map((action, idx) => {
              const actionType = action.action_type || action.type || "unknown";
              return (
                <div 
                  key={idx}
                  className={`action-item ${getActionColor(actionType)}`}
                >
                  <div className="action-icon">
                    {getActionIcon(actionType)}
                  </div>
                  <div className="action-details">
                    <div className="action-header">
                      <span className="action-type">
                        {(actionType).toUpperCase()}
                        {action.occurrence_count > 1 && (
                          <span className="occurrence-chip">{action.occurrence_count}x</span>
                        )}
                      </span>
                      <span className="action-time">
                        {formatTime(action.timestamp)}
                      </span>
                    </div>
                    <div className="action-description">
                      {action.target ? `Target: ${action.target}` : "System action"}
                    </div>
                    {action.status && (
                      <div className="action-result">
                        <span className="result-label">Status:</span>
                        <span className="result-value">{action.status}</span>
                      </div>
                    )}
                    {action.details && (
                      <div className="action-result">
                        <span className="result-label">Details:</span>
                        <span className="result-value">{JSON.stringify(action.details).substring(0, 100)}</span>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      <div className="panel-footer">
        <span>{sortedActions.length} grouped actions from {actions?.length || 0} recent records</span>
      </div>
    </section>
  );
}
