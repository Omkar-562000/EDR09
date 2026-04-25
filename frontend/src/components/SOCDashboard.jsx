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
  const [refreshInterval, setRefreshInterval] = useState(5000);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [selectedAlert, setSelectedAlert] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [systemStatus, setSystemStatus] = useState("secure");

  // Fetch data
  const fetchData = async () => {
    try {
      setIsRefreshing(true);
      const [meData, statusData, detectionData, actionData, eventData] = await Promise.all([
        api.me(),
        api.status(),
        api.detections(50),
        api.actions(30),
        api.events(100)
      ]);

      setUser(meData);
      setStats(statusData);
      setDetections(detectionData || []);
      setActions(actionData || []);
      setEvents(eventData || []);
      setLastUpdate(new Date());

      // Determine system status
      if (statusData.summary.critical_alerts > 0) {
        setSystemStatus("threat");
      } else if (statusData.summary.detections > 5) {
        setSystemStatus("warning");
      } else {
        setSystemStatus("secure");
      }
    } catch (error) {
      if (error.message.toLowerCase().includes("authentication")) {
        navigate("/login");
      }
    } finally {
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    fetchData();
    const timer = setInterval(fetchData, refreshInterval);
    return () => clearInterval(timer);
  }, [refreshInterval]);

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

  const formatStatusLabel = () => {
    if (systemStatus === "threat") return "🔴 Under Threat";
    if (systemStatus === "warning") return "🟠 Warning";
    return "🟢 Secure";
  };

  const activeThreats = stats?.summary?.critical_alerts || 0;
  const totalAlerts = stats?.summary?.detections || 0;
  const resolvedIncidents = stats?.summary?.actions || 0;

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
              {totalAlerts > 0 && <span className="nav-badge">{totalAlerts}</span>}
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
                      <span className="card-title">Total Alerts</span>
                    </div>
                    <div className="card-value">{totalAlerts}</div>
                    <div className="card-meta">
                      Last 50 detections
                    </div>
                  </div>

                  <div className={`summary-card card-resolved`}>
                    <div className="card-header">
                      <span className="card-icon">✅</span>
                      <span className="card-title">Resolved</span>
                    </div>
                    <div className="card-value">{resolvedIncidents}</div>
                    <div className="card-meta">
                      Automated responses
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
                  <label>Refresh Interval (ms)</label>
                  <input 
                    type="number" 
                    value={refreshInterval} 
                    onChange={(e) => setRefreshInterval(parseInt(e.target.value) || 5000)}
                    min="1000"
                    max="30000"
                    step="1000"
                  />
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
