import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api";
import ActivityTimeline from "./ActivityTimeline";
import AlertDetailModal from "./AlertDetailModal";
import AlertsPanel from "./AlertsPanel";
import EndpointsView from "./EndpointsView";
import LogsViewer from "./LogsViewer";
import ResponsePanel from "./ResponsePanel";

export default function SOCDashboard() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [stats, setStats] = useState(null);
  const [detections, setDetections] = useState([]);
  const [actions, setActions] = useState([]);
  const [events, setEvents] = useState([]);
  const [activeNav, setActiveNav] = useState("dashboard");
  const [refreshInterval, setRefreshInterval] = useState(10000);
  const [eventLimit, setEventLimit] = useState(50);
  const [alertLimit, setAlertLimit] = useState(25);
  const [actionLimit, setActionLimit] = useState(25);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [selectedAlert, setSelectedAlert] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [systemStatus, setSystemStatus] = useState("secure");
  const [agent, setAgent] = useState(null);
  const [agentBusy, setAgentBusy] = useState("");
  const [agentIntervalDraft, setAgentIntervalDraft] = useState(60);
  const [isEditingAgentInterval, setIsEditingAgentInterval] = useState(false);
  const [agentMessage, setAgentMessage] = useState("");
  const [firewallIp, setFirewallIp] = useState("");
  const [firewallDirection, setFirewallDirection] = useState("both");
  const [firewallMessage, setFirewallMessage] = useState("");

  // Fetch data
  const fetchData = async () => {
    try {
      setIsRefreshing(true);
      const promises = [
        api.me(),
        api.status(),
        api.detections(alertLimit),
        api.actions(actionLimit),
        api.events(eventLimit),
      ];
      const results = await Promise.allSettled(promises);

      const meData = results[0].status === "fulfilled" ? results[0].value : null;
      const statusData = results[1].status === "fulfilled" ? results[1].value : null;
      const detectionData = results[2].status === "fulfilled" ? results[2].value : [];
      const actionData = results[3].status === "fulfilled" ? results[3].value : [];
      const eventData = results[4].status === "fulfilled" ? results[4].value : [];

      if (!meData) {
        // likely unauthenticated — navigate to login
        navigate("/login");
        return;
      }

      setUser(meData);
      setStats(statusData);
      setDetections(detectionData || []);
      setActions(actionData || []);
      setEvents(eventData || []);
      setAgent(statusData.agent || null);
      if (!isEditingAgentInterval) {
        setAgentIntervalDraft(statusData.agent?.interval_seconds || 60);
      }
      setLastUpdate(new Date());

      // Determine system status
      const recentHighSeverity = (detectionData || []).filter((item) =>
        ["critical", "high"].includes((item.severity || "").toLowerCase())
      ).length;

      if (recentHighSeverity > 0) {
        setSystemStatus("threat");
      } else if ((detectionData || []).length > 5) {
        setSystemStatus("warning");
      } else {
        setSystemStatus("secure");
      }
    } catch (error) {
      // In case of unexpected errors, log and surface for debugging
      console.error("fetchData error:", error);
    } finally {
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    fetchData();
    const timer = setInterval(fetchData, refreshInterval);
    return () => clearInterval(timer);
  }, [refreshInterval, eventLimit, alertLimit, actionLimit]);

  const handleLogout = async () => {
    try {
      await api.logout();
      navigate("/login");
    } catch (error) {
      console.error("Logout failed:", error);
    }
  };

  const handleRefresh = async () => {
    await fetchData();
  };

  const updateAgent = async (name, task) => {
    try {
      setAgentBusy(name);
      setAgentMessage("");
      const agentData = await task();
      setAgent(agentData);
      setAgentIntervalDraft(agentData.interval_seconds || agentIntervalDraft);
      setAgentMessage("Agent settings updated.");
    } catch (error) {
      setAgentMessage(error.message);
    } finally {
      setAgentBusy("");
    }
  };

  const handlePauseToggle = async () => {
    if (agent?.paused) {
      await updateAgent("resume", api.resumeAgent);
      return;
    }
    await updateAgent("pause", api.pauseAgent);
  };

  const handleIntervalSave = async () => {
    await updateAgent("interval", () => api.setAgentInterval(Number(agentIntervalDraft)));
    setIsEditingAgentInterval(false);
  };

  const updatePositiveNumber = (setter, value, fallback, min, max) => {
    const next = Number.parseInt(value, 10);
    if (Number.isNaN(next)) {
      setter(fallback);
      return;
    }
    setter(Math.min(Math.max(next, min), max));
  };

  const handleCollectorToggle = async (collectorId, enabled) => {
    await updateAgent(`collector-${collectorId}`, () => api.setCollectorEnabled(collectorId, enabled));
  };

  const updateFirewall = async (name, task) => {
    try {
      setAgentBusy(name);
      setFirewallMessage("Applying firewall rule...");
      const result = await task();
      setFirewallMessage(result.message || "Firewall updated.");
      await fetchData();
    } catch (error) {
      setFirewallMessage(error.message);
    } finally {
      setAgentBusy("");
    }
  };

  const handleFirewallBlock = async () => {
    await updateFirewall("firewall-block", () => api.blockIp(firewallIp, firewallDirection));
  };

  const handleFirewallUnblock = async () => {
    await updateFirewall("firewall-unblock", () => api.unblockIp(firewallIp, firewallDirection));
  };

  const handleFirewallCheck = async () => {
    await updateFirewall("firewall-check", async () => {
      const result = await api.checkIp(firewallIp, firewallDirection);
      const state = result.blocked ? "blocked" : "not blocked";
      return { message: `${result.ip_address} is ${state} for ${result.direction}.` };
    });
  };

  const formatStatusLabel = () => {
    if (systemStatus === "threat") return "🔴 Under Threat";
    if (systemStatus === "warning") return "🟠 Warning";
    return "🟢 Secure";
  };

  const activeThreats = detections.filter((item) =>
    ["critical", "high"].includes((item.severity || "").toLowerCase())
  ).length;
  const recentAlerts = detections.length;
  const recentResolved = actions.length;
  const allTimeAlerts = stats?.summary?.detections || 0;
  const allTimeResolved = stats?.summary?.real_actions || 0;

  if (!user || !stats) {
    return (
      <div className="soc-loading">
        <div className="spinner"></div>
        <p>Initializing SOC Dashboard...</p>
      </div>
    );
  }

  return (
    <div className="soc-dashboard">
      {/* Top Navigation Bar */}
      <header className="soc-navbar">
        <div className="navbar-left">
          <div className="navbar-brand">
            <h1>EDR Tool</h1>
            <span className={`status-badge status-${systemStatus}`}>
              {formatStatusLabel()}
            </span>
          </div>
        </div>
        <div className="navbar-right">
          <div className="navbar-controls">
            <button 
              className="btn-icon"
              onClick={handleRefresh}
              disabled={isRefreshing}
              title="Refresh data"
            >
              🔄
            </button>
            <div className="navbar-divider"></div>
            <span className="last-update">
              Updated: {lastUpdate ? lastUpdate.toLocaleTimeString() : 'never'}
            </span>
            <span className="user-info">{user.email}</span>
            <button 
              className="btn-logout"
              onClick={handleLogout}
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      <div className="soc-container">
        {/* Left Sidebar Navigation */}
        <aside className="soc-sidebar">
          <nav className="sidebar-nav">
            <div 
              className={`nav-item ${activeNav === "dashboard" ? "active" : ""}`}
              onClick={() => setActiveNav("dashboard")}
            >
              <span className="nav-icon">📊</span>
              <span className="nav-label">Dashboard</span>
            </div>
            <div 
              className={`nav-item ${activeNav === "alerts" ? "active" : ""}`}
              onClick={() => setActiveNav("alerts")}
            >
              <span className="nav-icon">⚠️</span>
              <span className="nav-label">Alerts</span>
              {recentAlerts > 0 && <span className="nav-badge">{recentAlerts}</span>}
            </div>
            <div 
              className={`nav-item ${activeNav === "activity" ? "active" : ""}`}
              onClick={() => setActiveNav("activity")}
            >
              <span className="nav-icon">📋</span>
              <span className="nav-label">Activity</span>
            </div>
            <div 
              className={`nav-item ${activeNav === "logs" ? "active" : ""}`}
              onClick={() => setActiveNav("logs")}
            >
              <span className="nav-icon">📝</span>
              <span className="nav-label">Logs</span>
            </div>
            <div 
              className={`nav-item ${activeNav === "endpoints" ? "active" : ""}`}
              onClick={() => setActiveNav("endpoints")}
            >
              <span className="nav-icon">💻</span>
              <span className="nav-label">Endpoints</span>
            </div>
            <div 
              className={`nav-item ${activeNav === "responses" ? "active" : ""}`}
              onClick={() => setActiveNav("responses")}
            >
              <span className="nav-icon">⚡</span>
              <span className="nav-label">Responses</span>
            </div>
            <div 
              className={`nav-item ${activeNav === "settings" ? "active" : ""}`}
              onClick={() => setActiveNav("settings")}
            >
              <span className="nav-icon">⚙️</span>
              <span className="nav-label">Settings</span>
            </div>
          </nav>
        </aside>

        {/* Main Content Area */}
        <main className="soc-main">
          {activeNav === "dashboard" && (
            <>
              {/* Summary Cards */}
              <section className="summary-section">
                <div className="summary-grid">
                  <div className={`summary-card card-threats`}>
                    <div className="card-header">
                      <span className="card-icon">🎯</span>
                      <span className="card-title">Active Threats</span>
                    </div>
                    <div className="card-value">{activeThreats}</div>
                    <div className="card-meta">
                      {activeThreats > 0 ? "Requires attention" : "All clear"}
                    </div>
                  </div>

                  <div className={`summary-card card-alerts`}>
                    <div className="card-header">
                      <span className="card-icon">🚨</span>
                      <span className="card-title">Recent Alerts</span>
                    </div>
                    <div className="card-value">{recentAlerts}</div>
                    <div className="card-meta">
                      All-time total: {allTimeAlerts}
                    </div>
                  </div>

                  <div className={`summary-card card-resolved`}>
                    <div className="card-header">
                      <span className="card-icon">✅</span>
                      <span className="card-title">Resolved</span>
                    </div>
                    <div className="card-value">{recentResolved}</div>
                    <div className="card-meta">
                      All-time total: {allTimeResolved}
                    </div>
                  </div>

                  <div className={`summary-card card-health`}>
                    <div className="card-header">
                      <span className="card-icon">💚</span>
                      <span className="card-title">System Health</span>
                    </div>
                    <div className="card-value">
                      {systemStatus === "secure" ? "100%" : "85%"}
                    </div>
                    <div className="card-meta">
                      {systemStatus === "secure" ? "Optimal" : "Degraded"}
                    </div>
                  </div>
                </div>
              </section>

              {/* Two-column layout for dashboard view */}
              <div className="dashboard-grid">
                <div className="dashboard-col">
                  <AlertsPanel 
                    detections={detections}
                    onSelectAlert={setSelectedAlert}
                  />
                </div>
                <div className="dashboard-col">
                  <ActivityTimeline events={events} />
                </div>
              </div>
            </>
          )}

          {activeNav === "alerts" && (
            <AlertsPanel 
              detections={detections}
              onSelectAlert={setSelectedAlert}
              fullScreen={true}
            />
          )}

          {activeNav === "activity" && (
            <ActivityTimeline events={events} fullScreen={true} />
          )}

          {activeNav === "logs" && (
            <LogsViewer events={events} />
          )}

          {activeNav === "endpoints" && (
            <EndpointsView 
              stats={stats}
              actions={actions}
            />
          )}

          {activeNav === "responses" && (
            <ResponsePanel actions={actions} />
          )}

          {activeNav === "settings" && (
            <section className="panel settings-panel">
              <h2>Settings</h2>
              <div className="settings-content">
                <div className="setting-group">
                  <label>Result Refresh Interval (ms)</label>
                  <input 
                    type="number" 
                    value={refreshInterval} 
                    onChange={(event) => updatePositiveNumber(setRefreshInterval, event.target.value, 5000, 1000, 60000)}
                    min="1000"
                    max="60000"
                    step="1000"
                  />
                  <p className="setting-help">
                    Controls how often the dashboard asks for new events, alerts, and response results.
                  </p>
                </div>

                <div className="setting-group">
                  <label>Visible Result Volume</label>
                  <div className="flow-limit-grid">
                    <label>
                      <span>Events</span>
                      <input
                        type="number"
                        value={eventLimit}
                        onChange={(event) => updatePositiveNumber(setEventLimit, event.target.value, 100, 10, 500)}
                        min="10"
                        max="500"
                        step="10"
                      />
                    </label>
                    <label>
                      <span>Alerts</span>
                      <input
                        type="number"
                        value={alertLimit}
                        onChange={(event) => updatePositiveNumber(setAlertLimit, event.target.value, 50, 10, 500)}
                        min="10"
                        max="500"
                        step="10"
                      />
                    </label>
                    <label>
                      <span>Resolved</span>
                      <input
                        type="number"
                        value={actionLimit}
                        onChange={(event) => updatePositiveNumber(setActionLimit, event.target.value, 30, 10, 500)}
                        min="10"
                        max="500"
                        step="10"
                      />
                    </label>
                  </div>
                  <p className="setting-help">
                    Limits how much recent data is shown per refresh so the interface stays calm while monitoring.
                  </p>
                </div>

                <div className="setting-group">
                  <label>Input Telemetry Flow</label>
                  <div className="agent-control-row">
                    <span className={`agent-state ${agent?.paused ? "paused" : "running"}`}>
                      {agent?.paused ? "Paused" : "Collecting"}
                    </span>
                    <button
                      className="btn-secondary"
                      onClick={handlePauseToggle}
                      disabled={!agent || agentBusy === "pause" || agentBusy === "resume"}
                    >
                      {agent?.paused ? "Resume Collection" : "Pause Collection"}
                    </button>
                  </div>
                  {agentMessage && <p className="setting-message">{agentMessage}</p>}
                </div>

                <div className="setting-group">
                  <label>Input Collection Interval (seconds)</label>
                  <div className="agent-control-row">
                    <input
                      type="number"
                      value={agentIntervalDraft}
                      onFocus={() => setIsEditingAgentInterval(true)}
                      onBlur={() => setIsEditingAgentInterval(false)}
                      onChange={(event) => setAgentIntervalDraft(event.target.value)}
                      min="5"
                      max="3600"
                      step="5"
                    />
                    <button
                      className="btn-secondary"
                      onClick={handleIntervalSave}
                      disabled={!agent || agentBusy === "interval"}
                    >
                      Save Interval
                    </button>
                  </div>
                  <p className="setting-help">
                    Controls how often the backend collects from enabled local data sources.
                  </p>
                </div>

                <div className="setting-group">
                  <label>Data Sources</label>
                  <div className="collector-list">
                    {(agent?.collectors || []).map((collector) => (
                      <label className="collector-toggle" key={collector.id}>
                        <input
                          type="checkbox"
                          checked={collector.enabled}
                          disabled={agentBusy === `collector-${collector.id}`}
                          onChange={(event) => handleCollectorToggle(collector.id, event.target.checked)}
                        />
                        <span>
                          <strong>{collector.label}</strong>
                          <small>{collector.class_name}</small>
                        </span>
                      </label>
                    ))}
                  </div>
                </div>

                <div className="setting-group">
                  <label>Manual Windows Firewall Block</label>
                  <div className="firewall-control-grid">
                    <input
                      type="text"
                      value={firewallIp}
                      onChange={(event) => setFirewallIp(event.target.value)}
                      placeholder="IP address"
                    />
                    <select value={firewallDirection} onChange={(event) => setFirewallDirection(event.target.value)}>
                      <option value="both">Inbound + outbound</option>
                      <option value="outbound">Outbound only</option>
                      <option value="inbound">Inbound only</option>
                    </select>
                    <button
                      className="btn-secondary"
                      onClick={handleFirewallBlock}
                      disabled={!firewallIp || agentBusy === "firewall-block"}
                    >
                      Block IP
                    </button>
                    <button
                      className="btn-secondary"
                      onClick={handleFirewallUnblock}
                      disabled={!firewallIp || agentBusy === "firewall-unblock"}
                    >
                      Unblock IP
                    </button>
                    <button
                      className="btn-secondary"
                      onClick={handleFirewallCheck}
                      disabled={!firewallIp || agentBusy === "firewall-check"}
                    >
                      Check IP
                    </button>
                  </div>
                  <p className="firewall-note">
                    Requires the backend terminal to run as Administrator. This creates real Windows Firewall rules.
                  </p>
                  {firewallMessage && <p className="firewall-message">{firewallMessage}</p>}
                </div>
              </div>
            </section>
          )}
        </main>
      </div>

      {/* Alert Detail Modal */}
      {selectedAlert && (
        <AlertDetailModal 
          alert={selectedAlert}
          onClose={() => setSelectedAlert(null)}
        />
      )}
    </div>
  );
}
