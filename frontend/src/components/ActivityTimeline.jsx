import { useMemo, useState } from "react";

export default function ActivityTimeline({ events, fullScreen = false }) {
  const [expandedEventId, setExpandedEventId] = useState(null);

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
    const sortedEvents = [...(events || [])].sort(
      (a, b) => new Date(b.timestamp || 0) - new Date(a.timestamp || 0)
    );

    sortedEvents.forEach((event) => {
      const date = formatDate(event.timestamp);
      if (!groups[date]) {
        groups[date] = [];
      }
      groups[date].push(event);
    });

    return groups;
  }, [events]);

  const eventDates = Object.keys(groupedEvents).sort((a, b) => {
    const dateA = new Date(a);
    const dateB = new Date(b);
    return dateB - dateA;
  });

  const toggleEventExpanded = (eventId) => {
    setExpandedEventId(expandedEventId === eventId ? null : eventId);
  };

  const renderPayloadDetails = (payload) => {
    if (!payload) return null;

    const details = [];
    if (payload.command_line) details.push({ label: "Command", value: payload.command_line });
    if (payload.process_name) details.push({ label: "Process", value: payload.process_name });
    if (payload.pid) details.push({ label: "PID", value: payload.pid });
    if (payload.username) details.push({ label: "User", value: payload.username });
    if (payload.remote_ip) details.push({ label: "Remote IP", value: payload.remote_ip });
    if (payload.remote_port) details.push({ label: "Remote Port", value: payload.remote_port });
    if (payload.local_address) details.push({ label: "Local Address", value: payload.local_address });
    if (payload.status) details.push({ label: "Status", value: payload.status });
    if (payload.rule_name) details.push({ label: "Rule", value: payload.rule_name });
    if (payload.severity) details.push({ label: "Severity", value: payload.severity });

    return details.length > 0 ? details : null;
  };

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
                <span className="event-count-small">{groupedEvents[date].length} events</span>
              </div>

              <div className="timeline-events">
                {groupedEvents[date].map((event, idx) => {
                  const eventType = event.event_type || event.type || "unknown";
                  const eventId = `${date}-${idx}`;
                  const isExpanded = expandedEventId === eventId;
                  const payloadDetails = renderPayloadDetails(event.payload);

                  return (
                    <div
                      key={eventId}
                      className={`timeline-event ${getEventColor(eventType)} ${
                        isExpanded ? "expanded" : ""
                      }`}
                    >
                      <div className="event-marker">
                        <div className="event-dot">
                          <span className="event-icon">{getEventIcon(eventType)}</span>
                        </div>
                      </div>
                      <div className="event-content">
                        <div
                          className="event-header clickable"
                          onClick={() => toggleEventExpanded(eventId)}
                          style={{ cursor: "pointer" }}
                        >
                          <span className="event-type">{eventType.toUpperCase()}</span>
                          <span className="event-time">{formatTime(event.timestamp)}</span>
                          <span className="expand-icon">{isExpanded ? "▼" : "▶"}</span>
                        </div>
                        <div className="event-title">
                          {event.title || event.description || event.message || "System Event"}
                        </div>

                        {isExpanded && (
                          <div className="event-details-expanded">
                            {payloadDetails && payloadDetails.length > 0 && (
                              <div className="details-grid">
                                {payloadDetails.map((detail, idx) => (
                                  <div key={idx} className="detail-row">
                                    <span className="detail-label">{detail.label}:</span>
                                    <span className="detail-value">
                                      {typeof detail.value === "string" &&
                                      detail.value.length > 100
                                        ? detail.value.substring(0, 100) + "..."
                                        : detail.value}
                                    </span>
                                  </div>
                                ))}
                              </div>
                            )}

                            {event.source && (
                              <div className="event-meta">
                                <span className="event-source">Source: {event.source}</span>
                              </div>
                            )}

                            {event.event_id && (
                              <div className="event-meta">
                                <span className="event-id">
                                  Event ID: {event.event_id.substring(0, 12)}
                                </span>
                              </div>
                            )}
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
