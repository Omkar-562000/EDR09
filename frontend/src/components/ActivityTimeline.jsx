import { useMemo } from "react";

export default function ActivityTimeline({ events, fullScreen = false }) {
  const getEventIcon = (eventType) => {
    const type = (eventType || "").toLowerCase();
    if (type.includes("process")) return "⚙️";
    if (type.includes("network") || type.includes("connection")) return "🌐";
    if (type.includes("file")) return "📄";
    if (type.includes("registry")) return "📋";
    if (type.includes("user")) return "👤";
    if (type.includes("alert") || type.includes("detection")) return "🚨";
    if (type.includes("response") || type.includes("action")) return "⚡";
    return "📌";
  };

  const getEventColor = (eventType) => {
    const type = (eventType || "").toLowerCase();
    if (type.includes("alert") || type.includes("detection")) return "event-alert";
    if (type.includes("response") || type.includes("action")) return "event-action";
    if (type.includes("network")) return "event-network";
    if (type.includes("process")) return "event-process";
    return "event-default";
  };

  const formatTime = (timestamp) => {
    if (!timestamp) return "N/A";
    try {
      const date = new Date(timestamp);
      return date.toLocaleTimeString([], { 
        hour: "2-digit", 
        minute: "2-digit", 
        second: "2-digit" 
      });
    } catch {
      return timestamp;
    }
  };

  const formatDate = (timestamp) => {
    if (!timestamp) return "Unknown date";
    try {
      const date = new Date(timestamp);
      return date.toLocaleDateString([], { 
        month: "short", 
        day: "numeric" 
      });
    } catch {
      return "Unknown date";
    }
  };

  const groupedEvents = useMemo(() => {
    const groups = {};
    const compacted = new Map();

    [...(events || [])].forEach((event) => {
      const payload = event.payload || {};
      const key = [
        event.event_type,
        event.title,
        event.source,
        payload.process_name || payload.remote_ip || payload.event_id || payload.path || ""
      ].join("|");
      const existing = compacted.get(key);
      if (!existing) {
        compacted.set(key, { ...event, occurrence_count: 1, last_seen: event.timestamp });
        return;
      }
      existing.occurrence_count += 1;
      if (new Date(event.timestamp || 0) > new Date(existing.last_seen || 0)) {
        existing.last_seen = event.timestamp;
        existing.timestamp = event.timestamp;
      }
    });

    Array.from(compacted.values()).reverse().forEach((event) => {
      const date = formatDate(event.timestamp);
      if (!groups[date]) {
        groups[date] = [];
      }
      groups[date].push(event);
    });
    return groups;
  }, [events]);

  const eventDates = Object.keys(groupedEvents);

  return (
    <section className={`panel activity-timeline ${fullScreen ? "fullscreen" : ""}`}>
      <div className="panel-header">
        <h2>Activity Timeline</h2>
        <span className="event-count">{events?.length || 0} recent events</span>
      </div>

      <div className="timeline-container">
        {eventDates.length === 0 ? (
          <div className="empty-state">
            <span className="empty-icon">📭</span>
            <p>No activity recorded yet</p>
          </div>
        ) : (
          eventDates.map((date) => (
            <div key={date} className="timeline-date-group">
              <div className="timeline-date-header">
                <span className="date-label">{date}</span>
                <span className="event-count-small">{groupedEvents[date].length}</span>
              </div>

              <div className="timeline-events">
                {groupedEvents[date].map((event, idx) => {
                  const eventType = event.event_type || event.type || "unknown";
                  return (
                    <div 
                      key={idx} 
                      className={`timeline-event ${getEventColor(eventType)}`}
                    >
                      <div className="event-marker">
                        <div className="event-dot">
                          <span className="event-icon">
                            {getEventIcon(eventType)}
                          </span>
                        </div>
                      </div>
                      <div className="event-content">
                        <div className="event-header">
                          <span className="event-type">{eventType.toUpperCase()}</span>
                          <span className="event-time">{formatTime(event.timestamp)}</span>
                        </div>
                        <div className="event-title">
                          {event.title || event.description || event.message || "System Event"}
                          {event.occurrence_count > 1 && (
                            <span className="occurrence-chip">{event.occurrence_count}x</span>
                          )}
                        </div>
                        {event.details && (
                          <div className="event-details">
                            {typeof event.details === "string" 
                              ? event.details 
                              : JSON.stringify(event.details, null, 2)
                            }
                          </div>
                        )}
                        {event.source && (
                          <div className="event-meta">
                            <span className="event-source">Source: {event.source}</span>
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          ))
        )}
      </div>
    </section>
  );
}
