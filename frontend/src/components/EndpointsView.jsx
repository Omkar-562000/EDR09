export default function EndpointsView({ stats, actions }) {
  const summary = stats?.summary || {};

  return (
    <section className="panel endpoints-panel fullscreen">
      <div className="panel-header">
        <h2>Endpoints Overview</h2>
      </div>

      <div className="endpoints-container">
        <div className="endpoints-grid">
          {/* System Status Card */}
          <div className="endpoint-card">
            <div className="card-title">System Status</div>
            <div className="card-content">
              <div className="status-item">
                <span className="label">Total Events</span>
                <span className="value">{summary.events || 0}</span>
              </div>
              <div className="status-item">
                <span className="label">Total Detections</span>
                <span className="value">{summary.detections || 0}</span>
              </div>
              <div className="status-item">
                <span className="label">Critical Alerts</span>
                <span className="value alert">{summary.critical_alerts || 0}</span>
              </div>
              <div className="status-item">
                <span className="label">Automated Actions</span>
                <span className="value">{summary.actions || 0}</span>
              </div>
            </div>
          </div>

          {/* Response Actions Card */}
          <div className="endpoint-card">
            <div className="card-title">Response Actions Taken</div>
            <div className="card-content">
              <div className="status-item">
                <span className="label">Isolated Hosts</span>
                <span className="value">{stats?.isolated_hosts?.length || 0}</span>
              </div>
              <div className="status-item">
                <span className="label">Blocked IPs</span>
                <span className="value">{stats?.blocked_ips?.length || 0}</span>
              </div>
              <div className="status-item">
                <span className="label">Terminated Processes</span>
                <span className="value">{stats?.terminated_processes?.length || 0}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Isolated Hosts List */}
        {stats?.isolated_hosts && stats.isolated_hosts.length > 0 && (
          <div className="endpoint-section">
            <h3>Isolated Hosts</h3>
            <div className="host-list">
              {stats.isolated_hosts.map((host, idx) => (
                <div key={idx} className="host-item">
                  <span className="host-status">🚫</span>
                  <span className="host-name">{host}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Blocked IPs List */}
        {stats?.blocked_ips && stats.blocked_ips.length > 0 && (
          <div className="endpoint-section">
            <h3>Blocked IP Addresses</h3>
            <div className="ip-list">
              {stats.blocked_ips.map((ip, idx) => (
                <div key={idx} className="ip-item">
                  <span className="ip-status">🔒</span>
                  <span className="ip-address">{ip}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Terminated Processes List */}
        {stats?.terminated_processes && stats.terminated_processes.length > 0 && (
          <div className="endpoint-section">
            <h3>Recently Terminated Processes</h3>
            <div className="process-list">
              {stats.terminated_processes.map((proc, idx) => (
                <div key={idx} className="process-item">
                  <span className="process-status">⚡</span>
                  <span className="process-name">{proc}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </section>
  );
}
