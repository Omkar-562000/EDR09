import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api";

function labelScenario(value) {
  const labels = {
    auto: "Automatic selection",
    auth_burst: "Failed login burst",
    outbound: "Unauthorized outbound",
    process: "Suspicious process"
  };
  return labels[value] || value;
}

function SummaryCard({ label, value, note, tone = "" }) {
  return (
    <article className={`summary-card ${tone}`.trim()}>
      <span>{label}</span>
      <strong>{value}</strong>
      <small>{note}</small>
    </article>
  );
}

export default function Dashboard() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [stats, setStats] = useState(null);
  const [control, setControl] = useState({ mode: "manual", last_run: null, last_scenario: null });
  const [detections, setDetections] = useState([]);
  const [actions, setActions] = useState([]);
  const [events, setEvents] = useState([]);
  const [tab, setTab] = useState("overview");
  const [scenario, setScenario] = useState("auth_burst");
  const [query, setQuery] = useState("");
  const [busy, setBusy] = useState("");
  const [sync, setSync] = useState("Syncing");

  const latestDetection = detections[0];
  const latestAction = actions[0];

  const filteredEvents = useMemo(() => {
    const term = query.trim().toLowerCase();
    if (!term) {
      return events;
    }
    return events.filter((item) =>
      [item.title, item.source, item.event_type, JSON.stringify(item.payload)].join(" ").toLowerCase().includes(term)
    );
  }, [events, query]);

  async function refresh() {
    setSync("Syncing");
    try {
      const [me, statusData, controlData, detectionData, actionData, eventData] = await Promise.all([
        api.me(),
        api.status(),
        api.control(),
        api.detections(),
        api.actions(),
        api.events()
      ]);
      setUser(me);
      setStats(statusData);
      setControl(controlData || statusData.control || control);
      setDetections(detectionData);
      setActions(actionData);
      setEvents(eventData);
      setSync("Live");
    } catch (error) {
      if (error.message.toLowerCase().includes("authentication")) {
        navigate("/login");
        return;
      }
      setSync("Offline");
    }
  }

  useEffect(() => {
    refresh();
    const timer = window.setInterval(refresh, 5000);
    return () => window.clearInterval(timer);
  }, []);

  async function perform(name, task) {
    setBusy(name);
    try {
      await task();
      await refresh();
    } finally {
      setBusy("");
    }
  }

  async function handleModeChange(mode) {
    await perform(`mode-${mode}`, () => api.setMode(mode));
  }

  async function handleLogout() {
    await api.logout();
    navigate("/login");
  }

  if (!user || !stats) {
    return <div className="loading-screen">Loading dashboard...</div>;
  }

  const posture = stats.summary.critical_alerts > 0 ? "Attention needed" : "Stable";

  return (
    <div className="simple-app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">Automated EDR</p>
          <h1>Endpoint Response Dashboard</h1>
          <p className="topbar-copy">A simpler view for monitoring alerts, activity, and response flow.</p>
        </div>
        <div className="topbar-meta">
          <span className={`status-dot ${sync === "Live" ? "good" : sync === "Syncing" ? "warn" : "bad"}`}>{sync}</span>
          <span className="user-badge">{user.email}</span>
          <button className="button-secondary" onClick={handleLogout}>Logout</button>
        </div>
      </header>

      <section className="summary-grid-simple">
        <SummaryCard label="System" value={posture} note={`Mode: ${control.mode}`} tone={stats.summary.critical_alerts > 0 ? "danger" : "ok"} />
        <SummaryCard label="Events" value={stats.summary.events} note="Recent endpoint activity" />
        <SummaryCard label="Alerts" value={stats.summary.detections} note={`${stats.summary.critical_alerts} critical`} />
        <SummaryCard label="Responses" value={stats.summary.actions} note="Automated actions logged" />
      </section>

      <section className="control-strip">
        <div className="mode-toggle" role="tablist" aria-label="Control mode">
          <button className={control.mode === "manual" ? "is-active" : ""} onClick={() => handleModeChange("manual")} disabled={busy.startsWith("mode-")}>Manual</button>
          <button className={control.mode === "autonomous" ? "is-active" : ""} onClick={() => handleModeChange("autonomous")} disabled={busy.startsWith("mode-")}>Autonomous</button>
        </div>

        <div className="control-panel">
          <div>
            <p className="section-label">Control Flow</p>
            <h2>{control.mode === "manual" ? "Choose actions yourself" : "Run one-click autonomous flow"}</h2>
            <p className="muted">
              {control.mode === "manual"
                ? "Scan telemetry, simulate a threat, and reload rules only when you want to."
                : "One click will collect telemetry, pick or use a scenario, and let the backend drive the workflow."}
            </p>
          </div>

          <div className="action-row">
            {control.mode === "manual" ? (
              <>
                <button onClick={() => perform("scan", api.collect)} disabled={busy === "scan"}>{busy === "scan" ? "Scanning..." : "Scan"}</button>
                <select value={scenario} onChange={(event) => setScenario(event.target.value)}>
                  <option value="auth_burst">Failed login burst</option>
                  <option value="outbound">Unauthorized outbound</option>
                  <option value="process">Suspicious process</option>
                </select>
                <button onClick={() => perform("simulate", () => api.simulate(scenario))} disabled={busy === "simulate"}>{busy === "simulate" ? "Running..." : "Simulate Threat"}</button>
                <button className="button-secondary" onClick={() => perform("rules", api.reloadRules)} disabled={busy === "rules"}>{busy === "rules" ? "Reloading..." : "Reload Rules"}</button>
              </>
            ) : (
              <>
                <select value={scenario} onChange={(event) => setScenario(event.target.value)}>
                  <option value="auto">Automatic selection</option>
                  <option value="auth_burst">Failed login burst</option>
                  <option value="outbound">Unauthorized outbound</option>
                  <option value="process">Suspicious process</option>
                </select>
                <button onClick={() => perform("autonomous", () => api.autonomousRun(scenario))} disabled={busy === "autonomous"}>{busy === "autonomous" ? "Running..." : "Run Autonomous Cycle"}</button>
              </>
            )}
          </div>

          <p className="muted small-note">
            Last scenario: {control.last_scenario ? labelScenario(control.last_scenario) : "None yet"}
          </p>
        </div>
      </section>

      <nav className="tab-bar" aria-label="Main views">
        {[
          ["overview", "Overview"],
          ["alerts", "Alerts"],
          ["activity", "Activity"]
        ].map(([value, label]) => (
          <button key={value} className={tab === value ? "is-active" : ""} onClick={() => setTab(value)}>
            {label}
          </button>
        ))}
      </nav>

      {tab === "overview" && (
        <section className="view-grid">
          <article className="panel-simple">
            <p className="section-label">Latest Alert</p>
            {latestDetection ? (
              <>
                <h3>{latestDetection.rule_name}</h3>
                <p>{latestDetection.description}</p>
                <span className={`pill ${latestDetection.severity}`}>{latestDetection.severity}</span>
              </>
            ) : (
              <p className="muted">No alerts yet.</p>
            )}
          </article>

          <article className="panel-simple">
            <p className="section-label">Latest Response</p>
            {latestAction ? (
              <>
                <h3>{latestAction.action_type}</h3>
                <p>{latestAction.details.message}</p>
                <p className="muted">Target: {latestAction.target}</p>
              </>
            ) : (
              <p className="muted">No response actions yet.</p>
            )}
          </article>

          <article className="panel-simple wide">
            <p className="section-label">Current State</p>
            <div className="state-list">
              <div><strong>{stats.isolated_hosts.length}</strong><span>Isolated hosts</span></div>
              <div><strong>{stats.blocked_ips.length}</strong><span>Blocked IPs</span></div>
              <div><strong>{stats.terminated_processes.length}</strong><span>Terminated processes</span></div>
            </div>
          </article>
        </section>
      )}

      {tab === "alerts" && (
        <section className="stack-list">
          {detections.length ? detections.map((item) => (
            <details className="stack-card" key={item.detection_id}>
              <summary>
                <div>
                  <strong>{item.rule_name}</strong>
                  <span>{new Date(item.timestamp).toLocaleString()}</span>
                </div>
                <span className={`pill ${item.severity}`}>{item.severity}</span>
              </summary>
              <p>{item.description}</p>
              <div className="detail-grid">
                <span>Event type: {item.event.event_type}</span>
                <span>Host: {item.event.host}</span>
                <span>Confidence: {item.confidence}%</span>
              </div>
              <code>{JSON.stringify(item.event.payload)}</code>
            </details>
          )) : <div className="panel-simple"><p className="muted">No alerts yet.</p></div>}
        </section>
      )}

      {tab === "activity" && (
        <section className="activity-view">
          <div className="activity-toolbar">
            <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search recent activity" />
          </div>
          <div className="stack-list">
            {filteredEvents.length ? filteredEvents.map((item) => (
              <article className="stack-card" key={item.event_id}>
                <header>
                  <div>
                    <strong>{item.title}</strong>
                    <span>{new Date(item.timestamp).toLocaleString()}</span>
                  </div>
                  <span className="pill neutral">{item.event_type}</span>
                </header>
                <p className="muted">{item.source}</p>
              </article>
            )) : <div className="panel-simple"><p className="muted">No activity matches your search.</p></div>}
          </div>
        </section>
      )}
    </div>
  );
}
