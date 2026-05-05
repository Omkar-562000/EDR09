// Use relative API paths by default so Vite dev server proxy can forward requests
// to the backend during development. If `VITE_API_URL` is set, use that instead.
const API_BASE = import.meta.env.VITE_API_URL || "";

// Add a fetch with timeout using AbortController to avoid hanging requests
async function request(path, options = {}, timeoutMs = 12000) {
  const fetchOptions = {
    credentials: "include",
    ...options
  };

  // Only set Content-Type for JSON bodies (FormData should auto-set its own)
  if (options.body && typeof options.body === "string") {
    fetchOptions.headers = {
      "Content-Type": "application/json",
      ...(options.headers || {})
    };
  } else if (options.headers) {
    fetchOptions.headers = options.headers;
  }

  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeoutMs);
  fetchOptions.signal = controller.signal;

  let response;
  try {
    response = await fetch(`${API_BASE}${path}`, fetchOptions);
  } catch (err) {
    if (err.name === 'AbortError') {
      throw new Error('Request timed out');
    }
    throw err;
  } finally {
    clearTimeout(id);
  }

  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    throw new Error(payload.detail || `Request failed: ${response.status}`);
  }

  return response.json().catch(() => ({}));
}

export const api = {
  me: () => request("/api/me"),
  health: () => request("/api/health"),
  status: () => request("/api/status"),
  events: (limit = 100) => request(`/api/events?limit=${limit}`),
  detections: (limit = 100) => request(`/api/detections?limit=${limit}`),
  actions: (limit = 100) => request(`/api/actions?limit=${limit}`),
  collect: () => request("/api/collect", { method: "POST" }),
  reloadRules: () => request("/api/reload-rules", { method: "POST" }),
  control: () => request("/api/control"),
  agent: () => request("/api/agent"),
  pauseAgent: () => request("/api/agent/pause", { method: "POST" }),
  resumeAgent: () => request("/api/agent/resume", { method: "POST" }),
  setAgentInterval: (intervalSeconds) =>
    request("/api/agent/interval", {
      method: "POST",
      body: JSON.stringify({ interval_seconds: intervalSeconds })
    }),
  setCollectorEnabled: (collectorId, enabled) =>
    request(`/api/agent/collectors/${collectorId}`, {
      method: "POST",
      body: JSON.stringify({ enabled })
    }),
  blockIp: (ipAddress, direction = "both") =>
    request("/api/firewall/block-ip", {
      method: "POST",
      body: JSON.stringify({ ip_address: ipAddress, direction })
    }),
  unblockIp: (ipAddress, direction = "both") =>
    request("/api/firewall/unblock-ip", {
      method: "POST",
      body: JSON.stringify({ ip_address: ipAddress, direction })
    }),
  checkIp: (ipAddress, direction = "both") =>
    request("/api/firewall/check-ip", {
      method: "POST",
      body: JSON.stringify({ ip_address: ipAddress, direction })
    }),
  signup: (email, password) => {
    return request("/api/auth/signup", {
      method: "POST",
      body: JSON.stringify({ email, password }),
      headers: {
        "Content-Type": "application/json"
      }
    });
  },
  login: (email, password) => {
    return request("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
      headers: {
        "Content-Type": "application/json"
      }
    });
  },
  logout: () => request("/api/auth/logout", { method: "POST" })
};
