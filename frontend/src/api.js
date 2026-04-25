const API_BASE = "http://localhost:8000";

async function request(path, options = {}) {
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

  const response = await fetch(`${API_BASE}${path}`, fetchOptions);

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
  ingestEvent: (event) =>
    request("/api/ingest", {
      method: "POST",
      body: JSON.stringify({ event })
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
